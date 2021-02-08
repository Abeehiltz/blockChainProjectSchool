# decalage vers la gauche de s bits avec les s bits de gauche reviennent à droite
import sys
import pyfinite.ffield

VECTEUR_INIT = b"ABCDEFGH"

def _circular_shift(x, s, nbBits = 16):
    return ((x << s) & 0xFFFF) | (x >> (nbBits - s))


def _mod(x):
    return ((x - 1) % 8) + 1


def bytes_xor(a, b) :
    return bytes(x ^ y for x, y in zip(a, b))


class Kasumi:
    def __init__(self, master_key):
        self.key_KL1 = [None] * 9
        self.key_KL2 = [None] * 9
        self.key_KO1 = [None] * 9
        self.key_KO2 = [None] * 9
        self.key_KO3 = [None] * 9
        self.key_KI1 = [None] * 9
        self.key_KI2 = [None] * 9
        self.key_KI3 = [None] * 9

        self.corps_galois = pyfinite.ffield.FField(16)

        key = [None] * 9
        key_prime = [None] * 9

        master_key_prime = master_key ^ 0x0123456789ABCDEFFEDCBA9876543210

        # separer la cle et la cle prime en 8 partie
        for i in range(1, 9):
            key[i] = (master_key >> (16 * (8 - i))) & 0xFFFF
            key_prime[i] = (master_key_prime >> (16 * (8 - i))) & 0xFFFF

        for i in range(1, 9):
            self.key_KL1[i] = _circular_shift(key[_mod(i + 0)], 1)
            self.key_KL2[i] = key_prime[_mod(i + 2)]
            self.key_KO1[i] = _circular_shift(key[_mod(i + 1)], 5)
            self.key_KO2[i] = _circular_shift(key[_mod(i + 5)], 8)
            self.key_KO3[i] = _circular_shift(key[_mod(i + 6)], 13)
            self.key_KI1[i] = key_prime[_mod(i + 4)]
            self.key_KI2[i] = key_prime[_mod(i + 3)]
            self.key_KI3[i] = key_prime[_mod(i + 7)]




        # init RC4
        self.s_box_1 = [i for i in range(0,256)]
        self.s_box_2 = [i for i in range(0,256)]

        a = 0
        b = 0

        k_left = master_key >> 64
        k_right = master_key & 0xFFFFFFFFFFFFFFFFFFFFFFFF
        k_left = k_left.to_bytes(64, sys.byteorder)
        k_right = k_right.to_bytes(64, sys.byteorder)

        for i in range (0,256):
            a = (a + self.s_box_1[i]+k_left[i%64])%256
            b = (b + self.s_box_2[i]+k_right[i%64])%256

            self.s_box_1[i], self.s_box_1[a] = self.s_box_1[a], self.s_box_1[i]
            self.s_box_2[i], self.s_box_2[b] = self.s_box_2[b], self.s_box_2[i]


    def FI_fun(self, round_key_KI, input):

        round_key_KI = _circular_shift(round_key_KI, 2)

        #divide input by two
        left_0 = input >> 8
        right_0 = input & 0b11111111


        left = self.s_box_1[left_0]
        right = self.s_box_2[right_0]


        return round_key_KI ^ (left+right)



    def FO_fun(self, input, round_i):
        input_l = input >> 16
        input_r = input & 0xFFFF

        right_1 = self.FI_fun(self.key_KI1[round_i], input_l ^ self.key_KO1[round_i]) ^ input_r
        left_1 = input_r

        right_2 = self.FI_fun(self.key_KI2[round_i], left_1 ^ self.key_KO2[round_i]) ^ right_1
        left_2 = right_1

        right_3 = self.FI_fun(self.key_KI3[round_i], left_2 ^ self.key_KO3[round_i]) ^ right_2
        left_3 = right_2

        return (left_3 << 16) | right_3

    def FL_fun(self, input, round_i):

        input_l = input >> 16
        input_r = input & 0xFFFF

        right_prime = _circular_shift(input_l & self.key_KL1[round_i], 1) ^ input_r
        left_prime = _circular_shift(right_prime | self.key_KL2[round_i], 1) ^ input_l

        right_prime = self.corps_galois.Inverse(right_prime)
        left_prime = self.corps_galois.Inverse(left_prime)

        return (left_prime << 16) | right_prime

    def f_fun(self, input, round_i):

        if round_i % 2 == 0:
            value = self.FO_fun(input, round_i)
            return_value = self.FL_fun(value, round_i)
        else:
            value = self.FL_fun(input, round_i)
            return_value = self.FO_fun(value, round_i)

        return return_value

    def encoding(self, block):
        left = block >> 32
        right = block & 0xFFFFFFFF

        for i in range(1, 9):
            temp_right = left
            temp_left = right ^ self.f_fun(left, i)

            right = temp_right
            left = temp_left

        return (left << 32) | right

    def decoding(self, block):
        left = block >> 32
        right = block & 0xFFFFFFFF

        for i in range(8, 0, -1):
            temp_left = right
            temp_right = self.f_fun(right, i) ^ left

            right = temp_right
            left = temp_left

        return (left << 32) | right


def chiffrement_ECB(kasumi, message):
    messageChiffre = "".encode('utf-8')
    message = message.encode('utf-8')

    # Separate message en partie de 64 bits (8 octets)
    parts = [message[i:i + 8] for i in range(0, len(message), 8)]

    for part in parts:
        messageChiffre += kasumi.encoding(int.from_bytes(part, sys.byteorder)).to_bytes(8, sys.byteorder)

    return messageChiffre


def dechiffrement_ECB(kasumi, message):
    messageDechiffre = "".encode('utf-8')

    # Separate message en partie de 64 bits (8 octets)
    parts = [message[i:i + 8] for i in range(0, len(message), 8)]

    for part in parts:
        messageDechiffre += kasumi.decoding(int.from_bytes(part, sys.byteorder)).to_bytes(8, sys.byteorder)

    messageDechiffre = messageDechiffre.rstrip(b'\x00')
    return messageDechiffre.decode('utf-8')


def chiffrement_CBC(kasumi, message):
    vecteurInit = VECTEUR_INIT

    messageChiffre = "".encode('utf-8')
    message = message.encode('utf-8')

    # Separate message en partie de 64 bits (8 octets)
    parts = [message[i:i + 8] for i in range(0, len(message), 8)]

    vecteurUsed = False

    previousPart = parts[0]
    for part in parts:
        if not vecteurUsed:
            part = bytes_xor(vecteurInit, part)
            vecteurUsed = True
        else:
            part = bytes_xor(previousPart, part)

        part = kasumi.encoding(int.from_bytes(part, sys.byteorder)).to_bytes(8, sys.byteorder)
        messageChiffre += part

        previousPart = part

    return messageChiffre


def dechiffrement_CBC(kasumi, message):
    vecteurInit = VECTEUR_INIT

    messageDechiffre = "".encode('utf-8')

    # Separate message en partie de 64 bits (8 octets)
    parts = [message[i:i + 8] for i in range(0, len(message), 8)]

    vecteurUsed = False

    previousPart = parts[0]
    for part in parts:
        decode = kasumi.decoding(int.from_bytes(part, sys.byteorder)).to_bytes(8, sys.byteorder)

        if not vecteurUsed:
            decode = bytes_xor(vecteurInit, decode)
            vecteurUsed = True
        else:
            decode = bytes_xor(previousPart, decode)

        messageDechiffre += decode

        previousPart = part

    messageDechiffre = messageDechiffre.rstrip(b'\x00')
    return messageDechiffre.decode('utf-8')

def chiffrement_PCBC(kasumi, message):
    vecteurInit = VECTEUR_INIT

    messageChiffre = "".encode('utf-8')
    message = message.encode('utf-8')

    # Separate message en partie de 64 bits (8 octets)
    parts = [message[i:i + 8] for i in range(0, len(message), 8)]

    vecteurUsed = False

    newVector = parts[0]
    for part in parts:
        encode = "".encode('utf-8')
        if not vecteurUsed:
            encode = bytes_xor(vecteurInit, part)
            vecteurUsed = True
        else:
            encode = bytes_xor(newVector, part)

        encode = kasumi.encoding(int.from_bytes(encode, sys.byteorder)).to_bytes(8, sys.byteorder)
        messageChiffre += encode

        newVector = bytes_xor(encode, part)

    return messageChiffre

def dechiffrement_PCBC(kasumi, message):
    vecteurInit = VECTEUR_INIT

    messageDechiffre = "".encode('utf-8')

    # Separate message en partie de 64 bits (8 octets)
    parts = [message[i:i + 8] for i in range(0, len(message), 8)]

    vecteurUsed = False

    newVector = parts[0]
    for part in parts:
        decode = kasumi.decoding(int.from_bytes(part, sys.byteorder)).to_bytes(8, sys.byteorder)

        if not vecteurUsed:
            decode = bytes_xor(vecteurInit, decode)
            vecteurUsed = True
        else:
            decode = bytes_xor(newVector, decode)

        messageDechiffre += decode

        newVector = bytes_xor(decode, part)

    messageDechiffre = messageDechiffre.rstrip(b'\x00')
    return messageDechiffre.decode('utf-8')

def openFile(path):
    file = open(path, 'r')
    return file

def saveFileEncrypt(path, message):
    file = open(path, 'wb')
    file.write(message)

def saveFileDecrypt(path, message):
    file = open(path, 'w')
    file.write(message)

if __name__ == '__main__':
    key = 0x9900aabbccddeeff1122334455667788
    my_kasumi = Kasumi(key)
    file = openFile("message")
    text = file.read()

    encrypted = chiffrement_PCBC(my_kasumi, text)
    saveFileEncrypt("message.encrypt", encrypted)

    decrypted = dechiffrement_PCBC(my_kasumi, encrypted)
    saveFileDecrypt("message.decrypt", decrypted)
