import sys
import json

import codegen as gen
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

def codegen_operation(funcname, instr):
    if instr['op'] == 'const':
        value = instr['value']
        if instr['type'] == 'bool':
            value = 1 if value else 0
        gen.store_stack(value, symtbl.get_offset(funcname, instr['dest']))

    if instr['op'] == 'id':
        gen.copy_stack(symtbl.get_offset(funcname, instr['dest']),
                symtbl.get_offset(funcname, instr['args'][0]))

    if instr['op'] == 'br':
        gen.br(symtbl.get_offset(funcname, instr['args'][0]),
                instr['args'][1], instr['args'][2])

    if instr['op'] == 'jmp':
        gen.jmp(instr['args'][0])

    if instr['op'] == 'ret':
        gen.ret(funcname)

    if instr['op'] == 'print':
        args = instr['args']
        for i in range(len(args)):
            if symtbl.get_type(funcname, args[i]) == 'int':
                gen.printint(symtbl.get_offset(funcname, args[i]))
            if symtbl.get_type(funcname, args[i]) == 'bool':
                gen.printbool(symtbl.get_offset(funcname, args[i]))
            if i != len(args)-1:
                gen.printstr('strspace')
            else:
                gen.printstr('strnewline')

    if instr['op'] in comparisons:
        gen.comparison(comparisons[instr['op']],
                symtbl.get_offset(funcname, instr['dest']),
                symtbl.get_offset(funcname, instr['args'][0]),
                symtbl.get_offset(funcname, instr['args'][1]))

    if instr['op'] in binary_oprands:
        gen.binary_oprand(binary_oprands[instr['op']],
                symtbl.get_offset(funcname, instr['dest']),
                symtbl.get_offset(funcname, instr['args'][0]),
                symtbl.get_offset(funcname, instr['args'][1]))

    if instr['op'] in unary_oprands:
        get.unary_oprand(unary_oprands[instr['op']],
                symtbl.get_offset(funcname, instr['dest']),
                symtbl.get_offset(funcname, instr['args'][0]))

def codegen_func(funcname, instrs):
    gen.func_header(funcname)
    symtbl.set_regs(funcname, ['lr', 'fp'])
    saved_regs = symtbl.get_regs(funcname)
    for reg in saved_regs:
        gen.push_stack(reg)

    for instr in instrs:
        if 'dest' in instr:
            symtbl.insert(funcname, instr['dest'], instr['type'])
    print('\tsub    sp, sp, %s' % str(hex(symtbl.size(funcname))))
    print('\tmov    fp,sp')

    
    for instr in instrs:
        if 'label' in instr:
            print('%s:' % instr['label'])
        else:
            codegen_operation(funcname, instr)

    print('\t%s_ret:' % funcname)
    print('\tadd    sp, sp, %s' % str(hex(symtbl.size(funcname))))
    saved_regs.reverse()
    for reg in saved_regs:
        gen.pop_stack(reg)

    print('\tret    lr')


def main():
    if len(sys.argv) > 1:
        sys.stdin = open(sys.argv[1], 'r')
    if len(sys.argv) > 2:
        sys.stdout = open(sys.argv[2], 'w')

    bril = json.load(sys.stdin)

    for func in bril['functions']:
        codegen_func(func['name'], func['instrs'])

    gen.printfooter()

if __name__=='__main__':
    main()
