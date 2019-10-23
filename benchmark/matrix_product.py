from cg import *
from random import randint
cg = CG()

n=20

c = [[Var("int") for i in range(n)] for i in range(n)]
a = [[Var("int") for i in range(n)] for i in range(n)]
b = [[Var("int") for i in range(n)] for i in range(n)]

m=100

for vs in a:
    for v in vs:
        cg.init(v, randint(0,m))

for vs in b:
    for v in vs:
        cg.init(v, randint(0,m))


for i in range(n):
    for j in range(n):
        cg.init(c[i][j], 0)
        for k in range(n):
            tmp = Var("int")
            cg.op_mul(tmp, a[i][k], b[k][j])
            cg.op_add(c[i][j], c[i][j], tmp)

cg.print_code()
