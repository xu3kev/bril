class Var:
    counter = 0
    prefix = "v"
    def __init__(self, _type):
        self.type = _type
        self.name = self.prefix + str(Var.counter)
        Var.counter += 1

class CG:
    def __init__(self):
        self.code = []

    
    def init(self, t, a):
        if t.type == "bool":
            a = "true" if a else "false"
        else:
            a = str(a)
        self.code.append("{}: {} = const {};".format(t.name, t.type, a))

    
    def op_add(self, t, a, b):
        self.code.append("{}: {} = add {} {};".format(t.name, t.type, a.name, b.name))
    
    def op_mul(self, t, a, b):
        self.code.append("{}: {} = mul {} {};".format(t.name, t.type, a.name, b.name))
    
    def op_and(self, t, a, b):
        self.code.append("{}: {} = and {} {};".format(t.name, t.type, a.name, b.name))
    
    def op_or(self, t, a, b):
        self.code.append("{}: {} = or {} {};".format(t.name, t.type, a.name, b.name))

    def print(self, a):
        self.code.append("print {};".format(a.name))

    #def for_block(self, code):
        

    def print_code(self):
        print("main{")
        for instr in self.code:
            print(instr)
        print("}")
            
