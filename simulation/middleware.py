from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import SimulationState

class SimulateFailureMiddleware(MiddlewareMixin):
    def process_request(self, request):
        state = SimulationState.objects.filter(key="simulate_failure").first()
        if state and state.value and request.path != "/simulation/toggle-simulate-failure/":
            return JsonResponse({"error": "Serwer jest niedostępny z powodu symulowanej awarii."}, status=503)