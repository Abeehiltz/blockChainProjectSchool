import random


def kasumiEncodingBlock(input, key):
    keyBytes = input.to_bytes(16, 'big')
    inputBytes = input.to_bytes(8, 'big')
    inputR = inputBytes[:4]
    inputL = inputBytes[4:]
    print(inputR)
    print(inputL)


if __name__ == '__main__':
    key = 116656439549747520770026372207237495529
    input = 12574838010064957341
    kasumiEncodingBlock(input, key)
