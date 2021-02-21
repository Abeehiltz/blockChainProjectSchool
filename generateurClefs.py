import random



def testRabinMiller(n, k=5):
    # Test nombre inférieur à 6 rapidement
    if n < 6:
        return [False, False, True, True, False, True][n]
    elif not (n & 1):
        return False

    nBits = n - 1
    s = 0
    d = 0

    while nBits % 2 == 0:
        nBits = nBits // 2
        s = s + 1

    d = nBits

    for i in range(k):
        a = random.randint(2, n - 1)
        x = pow(a, d, n)

        if (x == 1) or (x == n - 1):
            continue

        for r in range(1, s):
            x = (x ** 2) % n
            if x == 1:
                return False
            if x == n - 1:
                continue

        return False
    return True


def genererNombrePremier(keysize=512):

    import multiprocessing as mp

    manager = mp.Manager()
    pool = mp.Pool(mp.cpu_count())
    flag = manager.Value('stop', 0)
    returnList = manager.list([])
    data = [(keysize, flag, returnList) for _ in range(int(mp.cpu_count()))]



    try:
        pool.starmap(genererNombrePremierWorker, data)
    except KeyboardInterrupt:
        pool.terminate()
        return False
    else:
        pool.close()

    return returnList[0]


def genererNombrePremierWorker(keysize=512, flag=None, returnList:list=[]):

    if not flag:
        from multiprocessing import Manager
        flag = Manager().Value('stop', 0)
    # Retourner un nombre premiers de taille keysize bits
    while not bool(flag.value):
        num = random.getrandbits(keysize)
        if testRabinMiller(num):
            q = (num - 1) // 2
            if testRabinMiller(q):
                flag.value=1
                returnList.append(num)

def trouverGenerateur(nombre_premier):
    q = (nombre_premier-1)//2

    for i in range (2, nombre_premier-1):
        if pow(i, 2, nombre_premier) == 1:
            continue

        if pow(i, q, nombre_premier) == 1:
            continue

        return i

def openFile(path):
    file = open(path, 'r')
    return file

def saveFile(path, nombrePremier):
    file = open(path, 'w')
    file.write(str(nombrePremier))
    file.close()

if __name__ == '__main__':
    key = genererNombrePremier(512)
    saveFile("nombrePremiers/nombrePremier512bits_bis", key)
