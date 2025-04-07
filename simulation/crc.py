
class CRC:
    def __init__(self):
        self.cdw = ''

    def xor(self, a, b):
        result = []
        for i in range(1, len(b)):
            if a[i] == b[i]:
                result.append('0')
            else:
                result.append('1')
        return ''.join(result)

    def crc(self, message, key):
        pick = len(key)
        tmp = message[:pick]
        while pick < len(message):
            if tmp[0] == '1':
                tmp = self.xor(key, tmp) + message[pick]
            else:
                tmp = self.xor('0' * pick, tmp) + message[pick]
            pick += 1

        if tmp[0] == "1":
            tmp = self.xor(key, tmp)
        else:
            tmp = self.xor('0' * pick, tmp)
        checkword = tmp
        return checkword

    def encodedData(self, data, key):
        l_key = len(key)
        append_data = data + '0' * (l_key - 1)
        remainder = self.crc(append_data, key)
        codeword = data + remainder
        self.cdw = codeword
        return codeword, remainder

    def receiverSide(self, key, data):
        r = self.crc(data, key)
        # Oczekujemy, że r będzie miało długość (len(key) - 1)
        if r == '0' * (len(key) - 1):
            return True
        else:
            return False


if __name__ == "__main__":
    data = '101100110000'
    key = '10011'
    crc_instance = CRC()
    encoded, rem = crc_instance.encodedData(data, key)
    print("Zakodowane dane:", encoded)
    print("Remainder:", rem)
    print("Sprawdzenie odbiornika:", "No Error" if crc_instance.receiverSide(key, encoded) else "Error")