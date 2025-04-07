# simulation/views.py

from django.shortcuts import render
from .crc import CRC
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .transmission import simulate_transmission
from .models import Node, Transmission, EventLog

@require_POST
def crc_view(request):
    try:
        body = json.loads(request.body)
        data = body.get("data")
        key = body.get("key")
        if not data or not key:
            return JsonResponse({"error": "Podaj zarówno 'data', jak i 'key'."}, status=400)

        crc_instance = CRC()
        encoded_data, remainder = crc_instance.encodedData(data, key)
        is_valid = crc_instance.receiverSide(key, encoded_data)

        response = {
            "encoded_data": encoded_data,
            "remainder": remainder,
            "valid": is_valid
        }
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def test_crc_page(request):
    return render(request, "simulation/test_crc.html")


def test_node_page(request):
    return render(request, "simulation/node_test.html")

def test_master_page(request):
    return render(request, "simulation/master_test.html")


@require_POST
def simulate_transmission_view(request):
    try:
        payload = json.loads(request.body)
        source_id = payload.get('source_id')
        destination_id = payload.get('destination_id')
        data_bits = payload.get('data')
        key = payload.get('key')
        delay = float(payload.get('delay', 0.0))
        packet_loss_percentage = float(payload.get('packet_loss_percentage', 0.0))
        error_params = payload.get('error_params')  # np. {"error_type": "single", "error_count": 1}

        if not (source_id and destination_id and data_bits and key):
            return JsonResponse({'error': "source_id, destination_id, data oraz key są wymagane."}, status=400)

        # Pobieramy tylko aktywne węzły
        source = get_active_node(source_id)
        destination = get_active_node(destination_id)

        if source is None or destination is None:
            return JsonResponse({'error': "Jeden lub oba węzły nie są aktualnie podłączone."}, status=400)

        simulation_result = simulate_transmission(
            data=data_bits,
            key=key,
            delay=delay,
            packet_loss_percentage=packet_loss_percentage,
            error_params=error_params
        )

        transmission = Transmission.objects.create(
            source=source,
            destination=destination,
            data=data_bits,
            delay=delay,
            packet_loss_percentage=packet_loss_percentage,
            error_info=({"error_type": simulation_result.get("error_type"),
                         "error_count": simulation_result.get("error_count")}
                        if simulation_result.get("error_type") else {})
        )

        EventLog.objects.create(
            transmission=transmission,
            crc_code=simulation_result.get("crc_remainder", ""),
            error_type=simulation_result.get("error_type", ""),
            error_count=simulation_result.get("error_count", 0),
            verification_result=simulation_result.get("crc_verification", True),
            details=f"Original codeword: {simulation_result.get('original_codeword')}, "
                    f"After error: {simulation_result.get('error_injected_codeword')}"
        )

        return JsonResponse(simulation_result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_or_create_node(node_id):
    """
    Pobiera Node o danym identyfikatorze lub tworzy go, jeśli nie istnieje.
    Dla nowo utworzonego węzła ustawiamy domyślne wartości.
    """
    try:
        node = Node.objects.get(id=int(node_id))
    except Node.DoesNotExist:
        node = Node.objects.create(
            name=f"Node {node_id}",
            ip_address="127.0.0.1",  # domyślny adres – można rozszerzyć o pobieranie IP
            status="online"
        )
    return node


def get_active_node(node_id):
    """
    Pobiera węzeł o danym ID, ale tylko jeśli ma aktywne połączenie (czyli istnieje wpis w ActiveConnection).
    Zwraca Node lub None, jeśli węzeł nie jest podłączony.
    """
    try:
        node = Node.objects.get(id=int(node_id))
        # Sprawdzamy, czy węzeł ma powiązany ActiveConnection (relacja one-to-one o nazwie active_connection)
        if hasattr(node, 'active_connection'):
            return node
        else:
            return None
    except Node.DoesNotExist:
        return None
def test_simulation_page(request):
    return render(request, "simulation/test_simulation.html")
