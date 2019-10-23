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
            print('r:int = id %s_%d_%d;' % (mat1, i, k))
            for j in range(n):
                print('tmp:int = mul r %s_%d_%d;' % (mat2, k, j))
                print('%s_%d_%d:int = add %s_%d_%d tmp;' % (res, i, j, res, i, j))


def gen(n):
    print('main {')
    matrix_gen('a', n, 0, 9)
    matrix_gen('b', n, 0, 9)
    matrix_gen('c', n, 0, 0)
    matrix_mult(n, 'c', 'a', 'b')
    matrix_print('c', n)
    print('}')


gen(int(sys.argv[1]))
