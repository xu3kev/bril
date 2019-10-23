from regalloc import regalloc
from codegen import codegen
import json
import argparse
import sys

REG_PREFIX = "r_"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='register allocation for bril json format')
    parser.add_argument("--stats", action="store_true", help="print var to reg mapping instead of code generation")
    parser.add_argument("--num", type=int, default=3, help="number of registers")
    args = parser.parse_args()

    bril = json.load(sys.stdin)

    regs = [REG_PREFIX+'%02d'%(i+1) for i in range(args.num)]

    for func in bril['functions']:
        regmap,colored,spilled = regalloc(func['instrs'], regs)
        print('%s {' % func['name'])
        codegen(func['instrs'], regmap)
        print('}')
