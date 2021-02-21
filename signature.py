# El Gamal

import generateurClefs
import hashage
import random
from math import gcd, lcm
import sys

class ElGamal:

    def __init__(self, key):
        self.p = key
        self.g = generateurClefs.trouverGenerateur(self.p)
        self.x = random.randrange(1, self.p-2)
        self.y = pow(self.g, self.x, self.p)

    def signature(self, message):

        k = random.randrange(2, self.p-2)
        while gcd(k, self.p-1) != 1:
            k = random.randrange(2, self.p-2)

        r = pow(self.g, k, self.p)

        hash = hashage.hashage(message.encode(), 32)
        hash = int.from_bytes(hash, sys.byteorder)


        s = (pow(k, -1, self.p-1) * (hash - self.x * r)) % (self.p-1)
        return [r, s]

    def verifierSignature(self, signature, message):
        r = signature[0]
        s = signature[1]

        hash = hashage.hashage(message.encode(), 32)
        hash = int.from_bytes(hash, sys.byteorder)


        # test 1
        if not 0 < r < self.p:
            return False
        if not 0 < s < self.p-1:
            return False

        # test 2
        left = pow(self.g, hash, self.p)
        right = (pow(self.y, r, self.p)*pow(r, s, self.p)) % self.p

        return left == right

class RSA:
    def __init__(self, p, q):
        self.p = p
        self.q = q
        self.n = p*q
        self.phi = lcm(p-1, q-1)
        self.e = random.randrange(1, self.phi)
        while gcd(self.phi, self.e) != 1:
            self.e = random.randrange(1, self.phi)
        self.d = pow(self.e, -1, self.phi)

    def signature(self, message):
        hash = hashage.hashage(message.encode(), 32)
        hash = int.from_bytes(hash, sys.byteorder)

        signature = pow(hash, self.d, self.n)
        return signature

    def verifierSignature(self, signature, message):
        hash = hashage.hashage(message.encode(), 32)
        hash = int.from_bytes(hash, sys.byteorder)

        # test
        test = pow(signature, self.e, self.n)
        return test == hash




if __name__ == '__main__':
    key = generateurClefs.openFile("nombrePremiers/nombrePremier512bits").read()
    key = int(key)
    key2 =generateurClefs.openFile("nombrePremiers/nombrePremier512bits_bis").read()
    key2 = int(key2)
    message = generateurClefs.openFile("message").read()

    # EL GAMAL
    el = ElGamal(key)
    signature = el.signature(message)
    print(el.verifierSignature(signature, message))

    # RSA
    rsa = RSA(key, key2)
    signatureRSA = rsa.signature(message)
    print(rsa.verifierSignature(signatureRSA, message))

