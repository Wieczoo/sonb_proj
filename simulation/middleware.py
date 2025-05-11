from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from simulation.views import simulate_failure

class SimulateFailureMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if simulate_failure and request.path != "/toggle_simulate_failure/":
            return JsonResponse({"error": "Serwer jest niedostępny z powodu symulowanej awarii."}, status=503)