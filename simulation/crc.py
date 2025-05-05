class CRCError(Exception):
    """Błąd wykryty przez CRC (niezerowa reszta)."""
    pass

class InvalidInputError(ValueError):
    """Nieprawidłowe dane wejściowe."""
    pass

class CRC:
    def __init__(self):
        self.codeword = None  # przechowuje ostatnio zakodowane dane

    def _validate(self, bits: str):
        if not bits:
            raise InvalidInputError("Ciąg nie może być pusty")
        if any(c not in '01' for c in bits):
            raise InvalidInputError("Ciąg może zawierać tylko '0' i '1'")

    def xor(self, a: str, b: str) -> str:
        # Bitowe XOR, ale pomijamy MSB – wynik ma długość len(b)-1.
        assert len(a) == len(b)
        return ''.join('0' if a[i] == b[i] else '1' for i in range(1, len(b)))

    def _compute_crc(self, message: str, key: str) -> str:
        pick = len(key)
        tmp = message[:pick]
        # klasyczne dzielenie bitowe
        while pick < len(message):
            if tmp[0] == '1':
                tmp = self.xor(key, tmp) + message[pick]
            else:
                tmp = self.xor('0' * len(key), tmp) + message[pick]
            pick += 1
        # ostatni krok: XOR bez dopisywania nowego bitu
        if tmp[0] == '1':
            tmp = self.xor(key, tmp)
        else:
            tmp = self.xor('0' * len(key), tmp)
        # tmp już ma długość len(key)-1
        return tmp

    def encode(self, data: str, key: str) -> str:
        """Zakoduj ciąg danych, zwracając codeword = data + CRC"""
        self._validate(data)
        self._validate(key)
        if len(key) < 2:
            raise InvalidInputError("Klucz CRC musi mieć długość co najmniej 2")
        # dopisujemy zera do message
        padded = data + '0' * (len(key) - 1)
        rem = self._compute_crc(padded, key)
        cw = data + rem
        self.codeword = cw
        return cw

    def verify(self, codeword: str, key: str) -> bool:
        """Sprawdź codeword; True jeśli reszta zerowa (brak błędów)."""
        self._validate(codeword)
        self._validate(key)
        rem = self._compute_crc(codeword, key)
        return all(bit == '0' for bit in rem)

    def verify_or_raise(self, codeword: str, key: str) -> None:
        """Jak verify(), ale rzuca CRCError jeśli błąd."""
        if not self.verify(codeword, key):
            raise CRCError("Wykryto błąd w przesłanych danych")

    def test_all_errors(self, key: str) -> bool:
        """
        Dla ostatniego codeword sprawdza wszystkie pojedyncze flips.
        Rzuca CRCError, jeśli któryś błąd nie jest wykrywany.
        """
        if self.codeword is None:
            raise InvalidInputError("Najpierw zakoduj dane metodą encode().")
        self._validate(key)
        undetected = []
        for i in range(len(self.codeword)):
            flipped = list(self.codeword)
            flipped[i] = '1' if self.codeword[i] == '0' else '0'
            flipped = ''.join(flipped)
            if self.verify(flipped, key):
                undetected.append(i)
        if undetected:
            raise CRCError(f"Nie wykryto błędów przy flipach bitów: {undetected}")
        return True

    # metody kompatybilne ze starą wersją interfejsu:
    def encodedData(self, data: str, key: str):
        cw = self.encode(data, key)
        remainder = cw[len(data):]
        return cw, remainder

    def receiverSide(self, key: str, codeword: str) -> bool:
        return self.verify(codeword, key)

if __name__ == "__main__":
    data = '101100110000'
    key = '10011'
    crc = CRC()
    # stary interfejs:
    encoded, rem = crc.encodedData(data, key)
    print("Zakodowane dane:", encoded)
    print("Remainder:", rem)
    print("Sprawdzenie odbiornika:", "No Error" if crc.receiverSide(key, encoded) else "Error")
