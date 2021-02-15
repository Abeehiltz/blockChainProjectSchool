from hashlib import sha256
from bitstring import BitArray

# Size in bytes
def hashage(data:bytes, size):
    bitrate = 32
    bitData = BitArray(data)
    capacity = size*2

    #Padding
    state = BitArray('uint:' + str(int(capacity/8)) + '=0')
    bitData = pad(bitData, bitrate)
    nbBlocks = int(bitData.len/bitrate)
    blocks = bitData.cut(bitrate)
    state[:bitrate] = BitArray('uint:' + str(bitrate) + '=' + str(bitrate))

    # Absorption
    for block in blocks:
        state[:bitrate] = state[:bitrate] ^ block
        state = BitArray(sha256(state.bytes).digest())

    #Essorage
    bitData = BitArray(sha256(state.bytes).digest())

    return bitData[:size].bytes


def pad(data:BitArray, bitrate):
    #add padding zeros
    length = (bitrate - ((data.len) % bitrate)) % bitrate
    data.append('uint:' + str(length) + '=0')

    return data

if __name__ == '__main__':
    file = open("message", 'r')
    message = file.read().encode()

    hash = BitArray(hashage(message, 128))
    print(hash.len)
    print(hash.hex)


