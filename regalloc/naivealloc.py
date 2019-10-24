import json
import sys
sys.path.append("examples")

from form_blocks import form_blocks
from util import flatten, var_args
MREGS = 4

def lookup(table, index):
    return table.get(index)

def select_reg(new_instr, arg, regs, var2reg, rrindex):
    # if regs empty, select in round-robin
    if None in regs:
        # Make a list of empty elements in regs
        empty = [index for index, elem in enumerate(regs) if elem is None]
        var2reg[arg] = empty[0]
        regs[empty[0]] = arg
        new_var = 'r_{}'.format(empty[0])
    
    # if regs full, swap with a current reg
    else:
        var = regs[rrindex]
        new_instr.append({
            'dest':'{}'.format(var),
            'op':'id',
            'type': 'int',
            'args': ['r_{}'.format(rrindex)]
        })    
        var2reg[arg] = rrindex
        regs[rrindex] = arg
        new_var = 'r_{}'.format(rrindex)
        
        rrindex = (rrindex + 1) % MREGS
    
    return new_instr, rrindex, new_var

def eval_var(new_block, arg, regs, var2reg, rrindex):
    # Check if this argument is already assigned
    isarg = lookup(var2reg, arg)
    
    # If argument has already been encountered
    if isarg is not None:
        isreg = [index for index, elem in enumerate(regs) if elem == arg]
        # if argument in regs
        if isreg:
            # update var with reg name
            new_var = 'r_{}'.format(isreg[0])
        # if not, bring it from the store
        else:
            new_block, rrindex, new_var = select_reg(new_block, arg, regs, var2reg, rrindex)
            # add load instruction
            new_block.append({
                'dest':'{}'.format(new_var),
                'op':'id',
                'type': 'int',
                'args': ['{}'.format(arg)]
            })

    # If argument hasn't been encountered
    else:
        new_block, rrindex, new_var = select_reg(new_block, arg, regs, var2reg, rrindex)

    return new_block, rrindex, new_var

def reg_alloc_block(block, regs):
    rrindex = 0
    var2reg = {}
    new_block = []
    for instr in block:
        if 'dest' in instr:
            new_block, rrindex, new_var = eval_var(new_block, instr['dest'], regs, var2reg, rrindex)
            instr.update({
                'dest': new_var,
            })
        
        args = var_args(instr)
        new_vars = []
        for arg in args:
            new_block, rrindex, new_var = eval_var(new_block, arg, regs, var2reg, rrindex)
            new_vars.append(new_var)
        instr.update({
            'args': new_vars,
        })
        new_block.append(instr)
    
    #print(new_block)
    return new_block

def reg_alloc(func):
    blocks = list(form_blocks(func['instrs']))
    new_blocks = []
    registers = [None for x in range(MREGS)]
    for block in blocks:
        new_block = reg_alloc_block(block, registers)
        new_blocks.append(new_block)
    func['instrs'] = flatten(new_blocks)

if __name__ == '__main__':
    # Apply the change to all the functions in the input program.
    bril = json.load(sys.stdin)
    for func in bril['functions']:
        reg_alloc(func)
    json.dump(bril, sys.stdout, indent=2, sort_keys=True)
