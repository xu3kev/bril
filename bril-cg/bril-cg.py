import sys
import json

def codegen_instr(instr, symtbl):
    binary_oprand = {
            'or': 'orr',
            'and': 'and',
            'ge': 'ge',
            'le': 'le',
            'gt': 'gt',
            'lt': 'lt',
            'eq': 'eq',
            'div': 'sdiv',
            'mul': 'mul',
            'sub': 'sub',
            'add': 'add'}
    code = ''

    if instr['op'] == 'const':
        value = instr['value']
        if instr['type'] == 'bool':
            if value:
                value = 1
            else:
                value = 0
        code += 'mov    x8, %d\n' % value
        code += 'str    x8, [fp, %s]\n' % \
                str(hex(symtbl[instr['dest']]['offset']))

    if instr['op'] in binary_oprand:
        tmpreg = 8
        for varname in instr['args']:
            code += 'ldr    x%d, [fp, %s]\n' % (tmpreg, 
                    str(hex(symtbl[varname]['offset'])))
            tmpreg += 1
        code += '%s    x0, x8, x9\n' % binary_oprand[instr['op']]
        code += 'str    x0, [fp, %s]\n' % \
                str(hex(symtbl[instr['dest']]['offset']))

    if instr['op'] == 'not':
        varname = instr['args'][0]
        code += 'ldr    x8, [fp, %s]\n' % (str(hex(symtbl[varname]['offset'])))
        code += 'mvn    x0, x8'
        code += 'str    x0, [fp, %s]\n' % \
                str(hex(symtbl[instr['dest']]['offset']))

    if instr['op'] == 'print':
        for varname in instr['args'][:-1]:
            if symtbl[varname]['type'] == 'int':
                code += 'adr    x0, fmtld\n'
                code += 'ldr    x1, [fp, %s]\n' % \
                        str(hex(symtbl[varname]['offset']))
                code += 'bl     printf\n' 
            elif symtbl[varname]['type'] == 'bool':
                code += 'ldr    x1, [fp, %s]\n' % \
                        str(hex(symtbl[varname]['offset']))
                code += 'bl     printbool\n'
            code += 'adr    x0, strspace\n'
            code += 'bl     printf\n' 
        varname = instr['args'][-1]
        if symtbl[varname]['type'] == 'int':
            code += 'adr    x0, fmtld\n'
            code += 'ldr    x1, [fp, %s]\n' % str(hex(symtbl[varname]['offset']))
            code += 'bl     printf\n' 
        elif symtbl[varname]['type'] == 'bool':
            code += 'ldr    x1, [fp, %s]\n' % \
                str(hex(symtbl[varname]['offset']))
            code += 'bl     printbool\n'
        code += 'adr    x0, strnewline\n'
        code += 'bl     printf\n' 

    if instr['op'] == 'br':
        args = instr['args']
        code += 'ldr    x0, [fp, %s]\n' % str(hex(symtbl[args[0]]['offset']))
        code += 'cbz    x0, %s\n' % args[2]
        code += 'b      %s\n' % args[1]

    if instr['op'] == 'jmp':
        code += 'b      %s\n' % instr['args'][0]

    if instr['op'] == 'ret':
        code += 'ldr    fp, [sp], 0x10\n'
        code += 'ldr    lr, [sp], 0x10\n'
        code += 'add    sp, sp, %s\n' % str(hex(len(symtbl) * 16))
        code += 'ret    lr\n'

    return code


def codegen_func(funcname, instrs):
    code = '.global %s\n' % funcname
    code += '%s:\n' % funcname

    symtbl = {}
    offset = len(symtbl) * 16

    for instr in instrs:
        if 'dest' in instr:
            varname = instr['dest']
            vartype = instr['type']

            if varname not in symtbl:
                symtbl[varname] = {'type': vartype, 'offset': offset+16}
                offset += 16

    code += 'sub    sp, sp, %s\n' % str(hex(len(symtbl) * 16))
    # TODO: callee save reg
    code += 'str    lr, [sp, -0x10]!\n'
    code += 'str    fp, [sp, -0x10]!\n'

    offset += 16 * 2
    for varname in symtbl:
        symtbl[varname]['offset'] = offset - symtbl[varname]['offset']

    code += 'mov    fp, sp\n'

    for instr in instrs:
        if 'dest' in instr:
            varname = instr['dest']
            vartype = instr['type']
            symtbl[varname]['type'] = vartype
        if 'label' in instr:
            code += '%s:\n' % instr['label']
        else:
            code += codegen_instr(instr, symtbl)

    # callee restore
    code += 'ldr    fp, [sp], 0x10\n'
    code += 'ldr    lr, [sp], 0x10\n'
    code += 'add    sp, sp, %s\n' % str(hex(len(symtbl) * 16))

    code += 'ret    lr\n'

    return code

bril = json.load(sys.stdin)

def codegen_print():
    return '''
.global printbool
printbool:
str    lr, [sp, -0x10]!
str    fp, [sp, -0x10]!
cbz    x1, printboolfalse
adr	   x0, strtrue
b      printboolendif
printboolfalse:
adr	   x0, strfalse
printboolendif:
bl	   printf
ldr    fp, [sp], 0x10
ldr    lr, [sp], 0x10
ret	   lr
.data
fmtld:
.string "%ld"
strtrue:
.string "true"
strfalse:
.string "false"
strspace:
.string " "
strnewline:
.string "\\n"'''

for func in bril['functions']:
    code = codegen_func(func['name'], func['instrs'])
    print(code)
    print(codegen_print())
