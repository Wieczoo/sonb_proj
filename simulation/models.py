# simulation/models.py
from django.db import models

class Node(models.Model):
    """
    Model reprezentujący pojedynczy komputer (węzeł) w sieci.
    """
    name = models.CharField(max_length=50, help_text="Nazwa węzła (np. Node 1)")
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, help_text="Adres IP węzła")
    status = models.CharField(max_length=20, default='online', help_text="Status węzła, np. online/offline")
    last_seen = models.DateTimeField(auto_now=True, help_text="Data i czas ostatniego kontaktu")

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class Transmission(models.Model):
    """
    Model reprezentujący transmisję danych między węzłami.
    """
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='transmissions_sent',
                               help_text="Węzeł wysyłający dane")
    destination = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='transmissions_received',
                                    help_text="Węzeł odbierający dane")
    data = models.TextField(help_text="Przesyłane dane (np. ciąg bitów)")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Data i czas rozpoczęcia transmisji")
    delay = models.FloatField(default=0.0, help_text="Opóźnienie transmisji (w sekundach)")
    packet_loss_percentage = models.FloatField(default=0.0, help_text="Procent utraconych pakietów")
    error_info = models.JSONField(blank=True, null=True, help_text="Informacje o wprowadzonych błędach (np. typ i ilość)")

    def __str__(self):
        return f"Transmisja od {self.source.name} do {self.destination.name} ({self.timestamp})"


class EventLog(models.Model):
    """
    Model rejestrujący zdarzenia transmisji, m.in. obliczony kod CRC, typ i ilość błędów oraz wynik weryfikacji.
    """
    transmission = models.ForeignKey(Transmission, on_delete=models.CASCADE, related_name='events',
                                     help_text="Transmisja, do której odnosi się zdarzenie")
    event_time = models.DateTimeField(auto_now_add=True, help_text="Data i czas zdarzenia")
    crc_code = models.CharField(max_length=64, help_text="Wygenerowany kod CRC")
    error_type = models.CharField(max_length=50, blank=True, help_text="Typ błędu, np. 'single', 'double', 'burst'")
    error_count = models.IntegerField(default=0, help_text="Liczba wprowadzonych błędów")
    verification_result = models.BooleanField(help_text="Wynik weryfikacji (True - brak błędów, False - wykryto błąd)")
    details = models.TextField(blank=True, help_text="Dodatkowe informacje o zdarzeniu")

    def __str__(self):
        return f"Zdarzenie transmisji {self.transmission.id} o {self.event_time}"


class ActiveConnection(models.Model):
    """
    Model rejestruący aktywne połjączenie danego węzła.
    W momencie, gdy węzeł (Node) łączy się z systemem, tworzony jest wpis,
    a przy rozłączeniu – usuwany.
    """
    node = models.OneToOneField(Node, on_delete=models.CASCADE, related_name="active_connection")
    connected_at = models.DateTimeField(auto_now_add=True, help_text="Data i czas nawiązania połączenia")

    def __str__(self):
        return f"Aktywne połączenie {self.node.name} od {self.connected_at}"


class SimulationState(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.BooleanField(default=False)