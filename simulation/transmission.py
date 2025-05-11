# simulation/transmission.py

import time
import random
from .crc import CRC


def flip_bit(data, index):
    """
    Pomocnicza funkcja, która zmienia wartość bitu na podanej pozycji.
    """
    if data[index] == '0':
        return data[:index] + '1' + data[index + 1:]
    else:
        return data[:index] + '0' + data[index + 1:]


def inject_error(data, error_type, error_count=1):
    """
    Funkcja wprowadza błędy do ciągu binarnego.

    Parametry:
    - data: oryginalny ciąg binarny (np. "100100011")
    - error_type: typ błędu ('single', 'double', 'odd', 'burst')
    - error_count: liczba bitów do zmiany (dla 'burst' określa długość bloku błędów)

    Zwraca zmodyfikowany ciąg z wprowadzonymi błędami.
    """
    n = len(data)
    modified = data

    if error_type == "single":
        # zmień jeden losowy bit
        idx = random.randint(0, n - 1)
        modified = flip_bit(modified, idx)
    elif error_type == "double":
        # zmień dwa różne bity
        indices = random.sample(range(n), 2)
        for idx in indices:
            modified = flip_bit(modified, idx)
    elif error_type == "odd":
        # upewnij się, że liczba błędów jest nieparzysta
        if error_count % 2 == 0:
            error_count += 1
        indices = random.sample(range(n), error_count)
        for idx in indices:
            modified = flip_bit(modified, idx)
    elif error_type == "burst":
        # zmień ciągły blok bitów o długości error_count
        if error_count > n:
            error_count = n
        start = random.randint(0, n - error_count)
        for i in range(start, start + error_count):
            modified = flip_bit(modified, i)
    else:
        # brak wprowadzania błędów
        modified = data

    return modified



def simulate_transmission(data, key, delay=0.0, packet_loss_percentage=0.0, error_params=None):
    """
    Symulacja transmisji danych między węzłami.

    Parametry:
    - data: oryginalny ciąg bitów (np. "100100")
    - key: klucz CRC (np. "1101")
    - delay: opóźnienie transmisji (w sekundach)
    - packet_loss_percentage: procentowa szansa utraty pakietu (0-100)
    - error_params: słownik z parametrami błędu, np. {"error_type": "single", "error_count": 1}

    Zwraca słownik z informacjami:
      - delay: opóźnienie
      - packet_lost: True/False, czy pakiet został utracony
      - original_codeword: kod wygenerowany przez CRC przed błędem
      - crc_remainder: reszta z operacji CRC
      - error_type, error_count (jeśli błąd został określony)
      - error_injected_codeword: kod po wprowadzeniu błędu
      - crc_verification: wynik weryfikacji CRC (True - brak błędu, False - wykryto błąd)
    """
    result = {}

    # Symulacja opóźnienia transmisji
    time.sleep(delay)
    result["delay"] = delay

    # Symulacja utraty pakietu
    if random.uniform(0, 100) < packet_loss_percentage:
        result["packet_lost"] = True
        result["error"] = "Packet lost during transmission"
        return result
    result["packet_lost"] = False
    try:
        # Obliczenie kodu CRC na oryginalnych danych
        crc_instance = CRC()
        print("Data Bits in crc", data)
        encoded_data, remainder = crc_instance.encodedData(data, key)
        print("encoded_data", encoded_data)
        result["original_codeword"] = encoded_data
        result["crc_remainder"] = remainder
        print("error_params",error_params)
        # Wprowadzenie błędów, jeśli parametr error_params jest przekazany
        if error_params and error_params.get("error_type") != "none":
            error_type = error_params.get("error_type")
            error_count = error_params.get("error_count", 1)
            error_injected_data = inject_error(encoded_data, error_type, error_count)
            result["error_type"] = error_type
            result["error_count"] = error_count
            result["error_injected_codeword"] = error_injected_data

            # Weryfikacja transmisji z błędem przy użyciu CRC
            is_valid = crc_instance.receiverSide(key, error_injected_data)
            result["crc_verification"] = is_valid
        else:
            print("simulate_transmission else")
            result["error_injected_codeword"] = encoded_data
            print("pre is valid")
            is_valid = crc_instance.receiverSide(key, encoded_data)
            print("is_valid")

            result["crc_verification"] = is_valid

        return result
    except Exception as e:
        print(e)
        result["error"] = f"An error occurred: {str(e)}"