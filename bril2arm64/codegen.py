
def func_header(funcname):
    print('\t.global %s' % funcname)
    print('\t.type %s, %%function' % funcname)
    print('%s:' % funcname)

def push_stack(reg):
    print('\tstr    %s, [sp, -0x10]!' % reg)

def pop_stack(reg):
    print('\tldr    %s, [sp], 0x10' % reg)

def store_stack(value, offset):
    print('\tmov    x8, %d' % value)
    print('\tstr    x8, [fp, %s]' % str(hex(offset)))

def binary_oprand(oprand, offdst, offsrc1, offsrc2):
    print('\tldr    x8, [fp, %s]' % str(hex(offsrc1)))
    print('\tldr    x9, [fp, %s]' % str(hex(offsrc2)))
    print('\t%s     x8, x8, x9' % oprand)
    print('\tstr    x8, [fp, %s]' % str(hex(offdst)))

def copy_stack(offdst, offsrc):
    print('\tldr    x8, [fp, %s]' % str(hex(offsrc)))
    print('\tstr    x8, [fp, %s]' % str(hex(offdst)))

def comparison(oprand, offdst, offsrc1, offsrc2):
    print('\tldr    x8, [fp, %s]' % str(hex(offsrc1)))
    print('\tldr    x9, [fp, %s]' % str(hex(offsrc2)))
    print('\tcmp    x8, x9')
    print('\tcset   x8, %s' % oprand)
    print('\tstr    x8, [fp, %s]' % str(hex(offdst)))

def unary_oprand(oprand, offdst, offsrc):
    print('\tldr    x8, [fp, %s]' % str(hex(offsrc)))
    print('\t%s     x8, x8' % oprand)
    print('\tstr    x8, [fp, %s]' % str(hex(offdst)))

def jmp(label):
    print('\tb      %s' % label)

def ret(funcname):
    print('\tb      %s_ret' % funcname)

def br(offset, label1, label2):
    print('\tldr    x8, [fp, %s]' % str(hex(offset)))
    print('\tcbnz   x8, %s' % label1)
    print('\tb      %s' % label2)

def printint(offset):
    print('\tadr    x0, fmtld')
    print('\tldr    x1, [fp, %s]' % str(hex(offset)))
    print('\tbl     printf')

def printbool(offset):
    print('\tldr    x1, [fp, %s]' % str(hex(offset)))
    print('\tbl     printbool')

def printstr(label):
    print('\tadr    x0, %s' % label)
    print('\tbl     printf')

def printfooter():
    print('''
    .global printbool
printbool:
    cbz    x1, printboolfalse
    adr	   x0, strtrue
    b      printboolendif
    printboolfalse:
    adr	   x0, strfalse
    printboolendif:
    bl	   printf
    ret	   lr

    .data
fmtld:      .string "%ld"
strtrue:    .string "true"
strfalse:   .string "false"
strspace:   .string " "
strnewline: .string "\\n"''')
