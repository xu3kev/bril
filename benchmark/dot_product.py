from cg import *
from random import randint
n = 50
m = 1000

c = CG()

a = [Var("int") for i in range(n)]
b = [Var("int") for i in range(n)]
for v in a:
    c.init(v, randint(0,m))
for v in b:
    c.init(v, randint(0,m))

s = Var("int")
c.init(s, 0)

for u in a:
    for v in b:
        tmp = Var("int")
        c.op_mul(tmp, u, v)
        c.op_add(s, s, tmp)
 
c.print(s)

c.print_code()
