import sys
import json

sys.path.insert(1, '../regalloc')
from regalloc import regalloc
from codegen import callee_save_regs,caller_save_regs,codegen_func,printfooter

def main():
    regs = callee_save_regs
    nregs = len(regs)

    if len(sys.argv) > 1:
        nregs = min(nregs, int(sys.argv[1]))
    if len(sys.argv) > 2:
        sys.stdin = open(sys.argv[2], 'r')
    if len(sys.argv) > 3:
        sys.stdout = open(sys.argv[3], 'w')

    bril = json.load(sys.stdin)
    regs = regs[:nregs]


    for func in bril['functions']:
        regmap, colored, spilled = regalloc(func['instrs'], regs)
        codegen_func(func['name'], func['instrs'], regmap)

    printfooter()

if __name__=='__main__':
    main()
