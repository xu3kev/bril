import sys

import symbol_table

symtbl = symbol_table.symbol_table()
binary_oprands = {
        'or': 'orr',
        'and': 'and',
        'div': 'sdiv',
        'mul': 'mul',
        'sub': 'sub',
        'add': 'add'}
unary_oprands = {'not': 'mvn'}
comparisons = {
        'ge': 'ge',
        'le': 'le',
        'gt': 'gt',
        'lt': 'lt',
        'eq': 'eq'}


class regstatus:
    def __init__(self, var, vartype, name):
        self.var = var
        self.reg = name
        self.type = vartype
        self.valid = False
        self.dirty = False

    def load(self):
        self.valid = True
        self.dirty = False

    def update(self):
        self.valid = True
        self.dirty = True


caller_save_regs = ['__x%d'%i for i in range(11, 16)]
callee_save_regs = ['__x%d'%i for i in range(19, 30)]
reg_table = {'__x%d'%i:regstatus('', '', '__x%d'%i) for i in range(32)}


def replace_variable(funcname, ins, regmap):
    if 'args' in ins:
        for i in range(len(ins['args'])):
            arg = ins['args'][i]
            if arg not in regmap:
                continue
            reg = regmap[arg]
            if reg_table[reg].var != arg:
                vartype = symtbl.get_type(funcname, dest)
                reg_table[reg] = regstatus(dest, vartype, reg)
            if not reg_table[reg].valid:
                reg_table[reg].load()
                offset = symtbl.get_offset(funcname, arg)
                print('\tldr    %s, [fp, %s]' % (reg[2:], offset))
            ins['args'][i] = reg

    if 'dest' in ins:
        dest = ins['dest']
        if dest not in regmap:
            return
        reg = regmap[dest]
        if reg_table[reg].var != dest:
            vartype = symtbl.get_type(funcname, dest)
            reg_table[reg] = regstatus(dest, vartype, reg)
        reg_table[reg].update()

        ins['dest'] = reg

def is_reg(name):
    return name.startswith('__x')
        
def printstr(label):
    print('\tadr    x0, %s' % label)
    print('\tbl     printf')

def func_header(funcname):
    print('\t.global %s' % funcname)
    print('\t.type %s, %%function' % funcname)
    print('%s:' % funcname)

def printfooter():
    print('''
        .global printbool
printbool:
        str    lr, [sp, -0x10]!
        str    fp, [sp, -0x10]!
        mov    x9, 0x10
        sub    sp, sp, 0x10

        cbz    x1, printboolfalse
        adr	   x0, strtrue
        b      printboolendif
        printboolfalse:
        adr	   x0, strfalse
        printboolendif:
        bl	   printf

        mov    x9, 0x10
        add    sp, sp, 0x10
        ldr    fp, [sp], 0x10
        ldr    lr, [sp], 0x10
        ret     lr

        .data
fmtld:      .string "%ld"
strtrue:    .string "true"
strfalse:   .string "false"
strspace:   .string " "
strnewline: .string "\\n"''')


def push_stack(reg):
    print('\tstr    %s, [sp, -0x10]!' % reg)

def pop_stack(reg):
    print('\tldr    %s, [sp], 0x10' % reg)

def get_type(funcname, arg):
    if is_reg(arg):
        return reg_table[arg].type
    else:
        return symtbl.get_type(funcname, arg)

def store_value(funcname, value, dst):
    if is_reg(dst):
        print('\tmov    %s, %d' % (dst[2:], value))
    else:
        offset = symtbl.get_offset(funcname, dst)
        print('\tmov    x9, %d' % value)
        print('\tstr    x9, [fp, %s]' % str(hex(offset)))


def load_reg(funcname, src, reg):
    if is_reg(src):
        print('\tmov    %s, %s' % (reg[2:], src[2:]))
    else:
        offset = symtbl.get_offset(funcname, src)
        print('\tldr    %s, [fp, %s]' % (reg[2:], str(hex(offset))))

def store_reg(funcname, reg, dst):
    if is_reg(dst):
        print('\tmov    %s, %s' % (dst[2:], reg[2:]))
    else:
        offset = symtbl.get_offset(funcname, dst)
        print('\tstr    %s, [fp, %s]' % (reg[2:], str(hex(offset))))

def codegen_operation(funcname, instr):
    op = instr['op']
    if op == 'const':
        value = instr['value']
        if instr['type'] == 'bool':
            value = 1 if value else 0
        store_value(funcname, value, instr['dest'])

    if op == 'id':
        arg = instr['args'][0]
        dst = instr['dest']
        if is_reg(arg) and is_reg(dst):
            if arg != dst:
                print('\tmov     %s, %s' % (dst[2:], arg[2:]))
        elif is_reg(arg):
            store_reg(funcname, arg, dst)
        elif is_reg(dst):
            load_reg(funcname, arg, dst)
        else:
            load_reg(funcname, arg, '__x9')
            store_reg(funcname, '__x9', dst)

    if instr['op'] == 'br':
        cond = instr['args'][0]
        label1 = instr['args'][1]
        label2 = instr['args'][2]
        if is_reg(cond):
            print('\tcbnz   %s, %s' % (cond[2:], label1))
        else:
            load_reg(funcname, cond, '__x9')
            print('\tcbnz   x9, %s' % label1)
        print('\tb      %s' % label2)

    if instr['op'] == 'jmp':
        print('\tb      %s' % instr['args'][0])

    if instr['op'] == 'ret':
        print('\tb      %s_ret' % funcname)

    if instr['op'] == 'print':
        args = instr['args']
        for i in range(len(args)):
            load_reg(funcname, args[i], '__x1')
            if get_type(funcname, args[i]) == 'int':
                print('\tadr    x0, fmtld')
                print('\tbl     printf')
            elif get_type(funcname, args[i]) == 'bool':
                print('\tbl     printbool')
            if i != len(args)-1:
                printstr('strspace')
            else:
                printstr('strnewline')

    if op in comparisons or op in binary_oprands:
        dst = instr['dest']
        arg0 = instr['args'][0]
        arg1 = instr['args'][1]
        if not is_reg(arg0):
            load_reg(funcname, arg0, '__x9')
            arg0 = '__x9'
        if not is_reg(arg1):
            load_reg(funcname, arg1, '__x10')
            arg1 = '__x10'

        if op in comparisons:
            print('\tcmp    %s, %s' % (arg0[2:], arg1[2:]))
            if is_reg(dst):
                print('\tcset   %s, %s' % (dst[2:], comparisons[op]))
            else:
                print('\tcset   x9, %s' % comparisons[op])
                store_reg(funcname, '__x9', dst)
        elif op in binary_oprands:
            if is_reg(dst):
                print('\t%s     %s, %s, %s' % (binary_oprands[op], dst[2:], arg0[2:], arg1[2:]))
            else:
                print('\t%s     x9, %s, %s' % (binary_oprands[op], arg0[2:], arg1[2:]))
                store_reg(funcname, '__x9', dst)


    if instr['op'] in unary_oprands:
        dst = instr['dest']
        arg0 = instr['args'][0]
        if not is_reg(arg0):
            load_reg(funcname, arg0, '__x9')
            arg0 = '__x9'
        if is_reg(dst):
            print('\t%s     %s, %s' % (unary_oprands[op], dst[2:], arg0[2:]))
        else:
            print('\t%s     x9, %s' % (unary_oprands[op], dst[2:], arg0[2:]))
            store_reg(funcname, '__x9', dst)

def codegen_func(funcname, instrs, regmap):
    func_header(funcname)
    symtbl.set_regs(funcname, ['lr', 'fp'])
    saved_regs = symtbl.get_regs(funcname)
    for reg in saved_regs:
        push_stack(reg)

    for instr in instrs:
        if 'dest' in instr:
            symtbl.insert(funcname, instr['dest'], instr['type'])
    size = symtbl.size(funcname)
    print('\tmov    x9, %s' % str(hex(size)))
    print('\tsub    sp, sp, %s' % str(hex(size)))
    print('\tmov    fp, sp')

    # TODO: callee save regs

    for instr in instrs:
        if 'label' in instr:
            print('%s:' % instr['label'])
        else:
            replace_variable(funcname, instr, regmap)
            codegen_operation(funcname, instr)

    print('\t%s_ret:' % funcname)
    # TODO: caller save regs
    size = symtbl.size(funcname)
    print('\tmov    x9, %s' % str(hex(size)))
    print('\tadd    sp, sp, %s' % str(hex(size)))
    saved_regs.reverse()
    for reg in saved_regs:
        pop_stack(reg)

    print('\tret    lr')
