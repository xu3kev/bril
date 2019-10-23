class regstatus:
    def __init__(self, var, vartype, name):
        self.var = var
        self.type = vartype
        self.name = name
        self.valid = False
        self.dirty = False

    def load(self):
        self.valid = True
        self.dirty = False

    def update(self):
        self.valid = True
        self.dirty = True


def replace_variable(ins, regmap, regs, types):
    if 'args' in ins:
        for i in range(len(ins['args'])):
            arg = ins['args'][i]
            if arg not in regmap:
                continue
            reg = regmap[arg]
            if regs[reg].var != arg:
                regs[reg] = regstatus(dest, types[arg], reg)
            if not regs[reg].valid:
                regs[reg].load()
                print('\t%s: %s = id %s;' % (reg, regs[reg].type, arg));
            ins['args'][i] = reg

    if 'dest' in ins:
        dest = ins['dest']
        if dest not in regmap:
            return
        reg = regmap[dest]
        if regs[reg].var != dest:
            regs[reg] = regstatus(dest, types[dest], reg)
        regs[reg].update()
        
        ins['dest'] = reg




def printbril(ins):
    op = ins['op']
    if op == 'const':
        if ins['type'] == 'int':
            print('\t%s: int = const %d;' % (ins['dest'], ins['value']))
        elif ins['value']:
            print('\t%s: bool = const true;' % ins['dest'])
        else:
            print('\t%s: bool = const false;' % ins['dest'])

    if op == 'id':
        print('\t%s: %s = id %s;' % (ins['dest'], ins['type'], ins['args'][0]));

    if op in ['print', 'br', 'jmp', 'ret']:
        print('\t%s ' % op + ' '.join(ins['args'])+';')

    if op in ['add', 'mul', 'sub', 'div', 'eq', 'lt', 'gt', 'le', 'ge', 'and', 'or']:
        print('\t%s: %s = %s %s %s;' % (ins['dest'], ins['type'], op, ins['args'][0],
            ins['args'][1]))

    if op == 'not':
        print('\t%s: %s = %s %s;' % (ins['dest'], ins['type'], op, ins['args'][0]))
     

def codegen(instrs, regmap):
    types = {}
    for ins in instrs:
        if 'dest' in ins:
            types[ins['dest']] = ins['type']

    regs = {}
    for var in regmap:
        reg = regmap[var]
        if reg not in regs:
            regs[reg] = regstatus(var, types[var], reg)

    for ins in instrs:
        if 'label' in ins:
            print('%s:' % ins['label'])
        else:
            replace_variable(ins, regmap, regs, types)
            printbril(ins)
