# simulation/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from simulation.models import ActiveConnection, Node

class NodeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Pobieramy identyfikator węzła z URL
        self.node_id = self.scope['url_route']['kwargs']['node_id']
        self.group_name = f'node_{self.node_id}'
        client_ip = self.scope["client"][0]  # adres IP klienta

        # Dołączamy do grupy indywidualnej oraz do wspólnej grupy "nodes"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add("nodes", self.channel_name)
        await self.accept()
        print(f"Node {self.node_id} connected")

        # Dodajemy aktywne połączenie oraz tworzony węzeł, jeśli nie istnieje
        await self.add_active_connection(self.node_id, client_ip)

    async def disconnect(self, close_code):
        # Usuwamy węzeł z grup
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard("nodes", self.channel_name)
        print(f"Node {self.node_id} disconnected")
        # Usuwamy wpis aktywnego połączenia z bazy
        await self.remove_active_connection(self.node_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received from node {self.node_id}: {data}")

        # Symulacja wyłączonego serwera źródłowego
        node = await sync_to_async(Node.objects.filter(id=self.node_id).first)()
        if node and node.status == "offline":
            await self.send(text_data=json.dumps({
                'error': f"Source server {self.node_id} is offline. Message ignored."
            }))
            print(f"Message from node {self.node_id} ignored due to offline status.")
            return

        # Obsługa wiadomości
        if "target" in data and "message" in data:
            target = data["target"]
            message = data["message"]
            if target.lower() == "master":
                await self.channel_layer.group_send("master", {
                    'type': 'node_message',
                    'node': self.node_id,
                    'message': message
                })
            else:
                await self.channel_layer.group_send(f'node_{target}', {
                    'type': 'node_message',
                    'node': self.node_id,
                    'message': message
                })
        else:
            await self.send(text_data=json.dumps({
                'error': 'Brak pola "target" lub "message" w przesłanej wiadomości'
            }))

    async def command(self, event):
        command_data = event['command']
        await self.send(text_data=json.dumps({
            'command': command_data
        }))

    async def node_message(self, event):
        """Metoda odbierająca wiadomości wysyłane z innego node'a lub mastera."""
        sender = event.get('node')
        message = event.get('message')
        await self.send(text_data=json.dumps({
            'from': sender,
            'message': message
        }))

    @sync_to_async
    def add_active_connection(self, node_id, client_ip):
        # Próba pobrania węzła, jeżeli nie istnieje, tworzony jest nowy wpis
        try:
            node = Node.objects.get(id=int(node_id))
        except Node.DoesNotExist:
            node = Node.objects.create(
                name=f"Node {node_id}",
                ip_address=client_ip,
                status="online"
            )
        # Tworzymy wpis w ActiveConnection, jeśli jeszcze nie istnieje
        ActiveConnection.objects.get_or_create(node=node)

    @sync_to_async
    def remove_active_connection(self, node_id):
        try:
            node = Node.objects.get(id=int(node_id))
            ActiveConnection.objects.filter(node=node).delete()
        except Node.DoesNotExist:
            pass


class MasterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global simulate_failure  # Upewnij się, że używasz globalnej zmiennej
        if simulate_failure:
            await self.close()  # Zamykamy połączenie natychmiast
            print("Master server failure simulated")
            return

        await self.accept()
        await self.channel_layer.group_add("master", self.channel_name)
        print("Master connected")

    async def receive(self, text_data):
        global simulate_failure
        if simulate_failure:
            await self.send(text_data=json.dumps({
                'error': 'Master server is currently unavailable. Message ignored.'
            }))
            return

        # Oryginalna logika przetwarzania wiadomości
        data = json.loads(text_data)
        command = data.get('command')
        target = data.get('target')

        if not command:
            await self.send(text_data=json.dumps({"error": "Brak komendy"}))
            return

        print(f"Master received command: {command} for target: {target}")

        if target == "all":
            await self.channel_layer.group_send("nodes", {
                'type': 'command',
                'command': command
            })
        else:
            target_group_name = f'node_{target}'
            await self.channel_layer.group_send(target_group_name, {
                'type': 'command',
                'command': command
            })

        await self.send(text_data=json.dumps({
            'status': 'Komenda wysłana',
            'command': command,
            'target': target
        }))
