# simulation/views.py

from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from .crc import CRC


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