import random
import sys

def matrix_gen(mat, n, l=0, u=99):
    for i in range(n):
        for j in range(n):
            print('%s_%d_%d:int = const %d;' % (mat, i, j, random.randint(l, u)))

def matrix_print(mat, n):
    for i in range(n):
        s = 'print'
        for j in range(n):
            s += ' %s_%d_%d' % (mat, i, j)
        print(s+';')

def matrix_mult(n, res, mat1, mat2):
    for k in range(n):
        for i in range(n):
            for j in range(n):
                print('%s_%d_%d:int = mul %s_%d_%d %s_%d_%d;' % (res, i, j, mat1, i, k, mat2, k, j))


def gen(n):
    print('main {')
    matrix_gen('a', n)
    matrix_gen('b', n)
    matrix_mult(n, 'c', 'a', 'b')
    matrix_print('c', n)
    print('}')


gen(int(sys.argv[1]))
