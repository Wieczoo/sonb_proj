# simulation/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NodeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Pobieramy identyfikator węzła z URL
        self.node_id = self.scope['url_route']['kwargs']['node_id']
        self.group_name = f'node_{self.node_id}'
        # Dołączamy do własnej grupy oraz do wspólnej grupy "nodes"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add("nodes", self.channel_name)
        await self.accept()
        print(f"Node {self.node_id} connected")

    async def disconnect(self, close_code):
        # Usuwamy węzeł z grup
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard("nodes", self.channel_name)
        print(f"Node {self.node_id} disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received from Node {self.node_id}: {data}")

        # Jeśli wiadomość zawiera pole "target", przekazujemy ją dalej
        target = data.get('target')
        message = data.get('message', '')
        if target:
            if target == "master":
                # Przesyłamy wiadomość do grupy master
                await self.channel_layer.group_send("master", {
                    'type': 'node_message',
                    'node': self.node_id,
                    'message': message
                })
            else:
                # Przesyłamy wiadomość do konkretnego węzła
                await self.channel_layer.group_send(f'node_{target}', {
                    'type': 'node_message',
                    'node': self.node_id,
                    'message': message
                })
        else:
            # Jeśli nie określono celu, zwracamy błąd
            await self.send(text_data=json.dumps({'error': 'No target specified'}))

    # Metoda obsługująca wiadomości wysyłane do tego węzła
    async def node_message(self, event):
        sender = event.get('node')
        message = event.get('message')
        await self.send(text_data=json.dumps({
            'from': sender,
            'message': message
        }))


class MasterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Dołączamy do grupy "master", aby otrzymywać wiadomości od węzłów
        await self.channel_layer.group_add("master", self.channel_name)
        print("Master connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("master", self.channel_name)
        print("Master disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received at Master: {data}")
        command = data.get('command')
        target = data.get('target')  # target może być numerem węzła, "all" lub inny

        if command:
            if target == "all":
                # Wysyłamy komendę do wszystkich węzłów
                await self.channel_layer.group_send("nodes", {
                    'type': 'node_message',
                    'node': 'master',
                    'message': command
                })
            else:
                # Wysyłamy komendę do konkretnego węzła
                await self.channel_layer.group_send(f'node_{target}', {
                    'type': 'node_message',
                    'node': 'master',
                    'message': command
                })
            await self.send(text_data=json.dumps({
                'status': 'Command sent',
                'command': command,
                'target': target
            }))
        else:
            await self.send(text_data=json.dumps({'error': 'No command specified'}))

    # Metoda odbierająca wiadomości wysłane przez węzły do grupy master
    async def node_message(self, event):
        sender = event.get('node')
        message = event.get('message')
        await self.send(text_data=json.dumps({
            'from': sender,
            'message': message
        }))
