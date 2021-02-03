import random

from pip._vendor.msgpack.fallback import xrange


def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


def exponentationRapide(num, exp, modulo):
    t = 1
    while (exp > 0):

        # for cases where exponent
        # is not an even value
        if (exp % 2 != 0):
            t = (t * num) % modulo

        num = pow(num, 2, modulo)
        exp = int(exp / 2)
    return t % modulo


def is_probable_prime(n, k=5):
    # Test nombre inférieur à 6 rapidement
    if n < 6:
        return [False, False, True, True, False, True][n]
    elif n & 1 == 0:  # should be faster than n % 2
        return False
    else:  # Nombres grands
        s = 0
        d = n - 1

        # Calculer d et s pour 2^s * d = n-1
        while d & 1 == 0:  # d mod 2 == 0
            s += 1
            d = d >> 1  # d diviser par 2

        for i in range(0, k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x != 1 and (x + 1) != n:
                for r in xrange(1, s):
                    x = pow(x, 2, n)
                    if x == 1:
                        return False
                    elif x == (n - 1):
                        a = 0
                        break
                if a:
                    return False
        return True


def genererNombrePremier(keysize=512):
    # Retourner un nombre premiers de taille keysize bits
    while True:
        num = random.getrandbits(keysize)
        if is_probable_prime(num):
            if is_probable_prime(int((num - 1) / 2)):
                return num


def trouverGenerateur(nombre_premier):
    for i in range(3, nombre_premier):
        if pow(i, 1, nombre_premier) != 1:
            if pow(i, 2, nombre_premier) != 1:
                if pow(i, int((nombre_premier - 1) / 2), nombre_premier) != 1:
                    return i

    return -1


if __name__ == '__main__':
    nombre = genererNombrePremier(10)
    print('nombre premier:', nombre)
    generateur = trouverGenerateur(nombre)
    print('generateur', generateur)
