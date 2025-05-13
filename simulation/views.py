# simulation/views.py
import sys
from django.shortcuts import render
from .crc import CRC
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_http_methods
from .transmission import simulate_transmission
from .models import Node, Transmission, EventLog
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from .models import SimulationState
import logging
logger = logging.getLogger(__name__)


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
    print("simulate_transmission_view")
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
            return JsonResponse({'error': "Jeden lub oba węzły nie są aktywne."}, status=400)

        if source.status == "offline":
            return JsonResponse({'error': "Węzeł źródłowy jest offline."}, status=400)

        if destination.status == "offline":
            return JsonResponse({'error': "Węzeł docelowy jest offline."}, status=400)
        print("OiRG Data Bts",data_bits)
        simulation_result = simulate_transmission(
            data=data_bits,
            key=key,
            delay=delay,
            packet_loss_percentage=packet_loss_percentage,
            error_params=error_params
        )
        print("simulation_result",simulation_result)
        # transmission = Transmission.objects.create(
        #     source=source,
        #     destination=destination,
        #     data=data_bits,
        #     delay=delay,
        #     packet_loss_percentage=packet_loss_percentage,
        #     error_info=({"error_type": simulation_result.get("error_type"),
        #                  "error_count": simulation_result.get("error_count")}
        #                 if simulation_result.get("error_type") else {})
        # )
        # print("2")
        # EventLog.objects.create(
        #     transmission=transmission,
        #     crc_code=simulation_result.get("crc_remainder", ""),
        #     error_type=simulation_result.get("error_type", ""),
        #     error_count=simulation_result.get("error_count", 0),
        #     verification_result=simulation_result.get("crc_verification", True),
        #     details=f"Original codeword: {simulation_result.get('original_codeword')}, "
        #             f"After error: {simulation_result.get('error_injected_codeword')}"
        # )

        return JsonResponse(simulation_result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_or_create_node(node_id):
    """
  ub  Pobiera Node o danym identyfikatorze l tworzy go, jeśli nie istnieje.
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
        return  node
        # Sprawdzamy, czy węzeł ma powiązany ActiveConnection (relacja one-to-one o nazwie active_connection)
        # if hasattr(node, 'active_connection'):
        #     return node
        # else:
        #     return None
    except Node.DoesNotExist:
        return None
def test_simulation_page(request):
    return render(request, "simulation/test_simulation.html")


@require_http_methods(["GET"])
def get_all_nodes(request):
    nodes = Node.objects.filter(status="online")
    data = [{
        "id": node.id,
        "name": node.name,
        "ip_address": node.ip_address,
        "status": node.status,
    } for node in nodes]
    return JsonResponse({"nodes": data})

@require_POST
def create_node(request):
    try:
        payload = json.loads(request.body)
        name = payload.get("name")
        ip_address = payload.get("ip_address", "127.0.0.1")  # opcjonalne, domyślnie localhost
        status = payload.get("status", "online")

        if not name:
            return JsonResponse({"error": "Pole 'name' jest wymagane."}, status=400)

        node = Node.objects.create(name=name, ip_address=ip_address, status=status)
        return JsonResponse({
            "id": node.id,
            "name": node.name,
            "ip_address": node.ip_address,
            "status": node.status
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def ensure_ten_online_nodes(request):
    try:
        existing_online_nodes = Node.objects.filter(status="online").count()
        nodes_to_create = 10 - existing_online_nodes

        created_nodes = []
        for i in range(nodes_to_create):
            node = Node.objects.create(
                name=f"AutoNode {existing_online_nodes + i + 1}",
                ip_address=f"127.0.0.1",
                status="online"
            )
            created_nodes.append({
                "id": node.id,
                "name": node.name,
                "ip_address": node.ip_address,
                "status": node.status
            })

        return JsonResponse({
            "message": f"Upewniono się, że jest 10 węzłów online.",
            "new_nodes_created": nodes_to_create,
            "created_nodes": created_nodes
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
@require_POST
def shutdown_master(request):
    try:
        payload = json.loads(request.body)
        source_id = payload.get("source_id")

        if not source_id:
            return JsonResponse({"error": "Brakuje ID węzła źródłowego."}, status=400)

        node = Node.objects.get(id=source_id)
        node.status = "offline"
        node.save()
        return JsonResponse({"status": f"Węzeł źródłowy {node.name} został wyłączony."})
    except Node.DoesNotExist:
        return JsonResponse({"error": "Węzeł źródłowy nie istnieje."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def shutdown_node(request):
    try:
        payload = json.loads(request.body)
        destination_id = payload.get("destination_id")

        if not destination_id:
            return JsonResponse({"error": "Brakuje ID węzła docelowego."}, status=400)

        node = Node.objects.get(id=destination_id)
        node.status = "offline"
        node.save()
        return JsonResponse({"status": f"Węzeł docelowy {node.name} został wyłączony."})
    except Node.DoesNotExist:
        return JsonResponse({"error": "Nie znaleziono węzła docelowego."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def toggle_simulate_failure(request):
    state, _ = SimulationState.objects.get_or_create(key="simulate_failure")
    state.value = not state.value
    state.save()
    print(f"simulate_failure: {state.value}")
    return JsonResponse({"simulate_failure": state.value})

@csrf_exempt
@require_POST
def shutdown_source_server(request):
    try:
        payload = json.loads(request.body)
        source_id = payload.get("source_id")

        if not source_id:
            return JsonResponse({"error": "Brakuje ID serwera źródłowego."}, status=400)

        node = Node.objects.get(id=source_id)
        node.status = "offline"
        node.save()
        return JsonResponse(    {"status": f"Serwer źródłowy {node.name} został wyłączony."
                                ,"nodeid":source_id,
                                 "state":node.status})
    except Node.DoesNotExist:
        return JsonResponse({"error": "Serwer źródłowy nie istnieje."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)