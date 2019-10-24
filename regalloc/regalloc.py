from collections import namedtuple

from form_blocks import form_blocks
from form_blocks import TERMINATORS
import cfg
from util import var_args

from graph_coloring import *

PRINT_STATS = False

# A single dataflow analysis consists of these part:
# - forward: True for forward, False for backward.
# - init: An initial value (bottom or top of the latice).
# - merge: Take a list of values and produce a single value.
# - transfer: The transfer function.
Analysis = namedtuple('Analysis', ['forward', 'init', 'merge', 'transfer'])

def union(sets):
    out = set()
    for s in sets:
        out.update(s)
    return out


def df_worklist(blocks, analysis):
    """The worklist algorithm for iterating a data flow analysis to a
    fixed point.
    """
    preds, succs = cfg.edges(blocks)

    # Switch between directions.
    if analysis.forward:
        first_block = list(blocks.keys())[0]  # Entry.
        in_edges = preds
        out_edges = succs
    else:
        first_block = list(blocks.keys())[-1]  # Exit.
        in_edges = succs
        out_edges = preds

    # Initialize.
    in_ = {first_block: analysis.init}
    out = {node: analysis.init for node in blocks}

    # Iterate.
    worklist = list(blocks.keys())
    while worklist:
        node = worklist.pop(0)

        inval = analysis.merge(out[n] for n in in_edges[node])
        in_[node] = inval

        outval = analysis.transfer(blocks[node], inval)

        if outval != out[node]:
            out[node] = outval
            worklist += out_edges[node]

    if analysis.forward:
        return in_, out
    else:
        return out, in_


def fmt(val):
    """Guess a good way to format a data flow value. (Works for sets and
    dicts, at least.)
    """
    if isinstance(val, set):
        if val:
            return ', '.join(v for v in sorted(val))
        else:
            return '∅'
    elif isinstance(val, dict):
        if val:
            return ', '.join('{}: {}'.format(k, v)
                             for k, v in sorted(val.items()))
        else:
            return '∅'
    else:
        return str(val)


def run_df(bril, analysis):
    for func in bril['functions']:
        # Form the CFG.
        blocks = cfg.block_map(form_blocks(func['instrs']))
        cfg.add_terminators(blocks)

        in_, out = df_worklist(blocks, analysis)
        constraints = []
        for block in blocks:
            print('{}:'.format(block))
            print('  in: ', fmt(in_[block]))
            print('  out:', fmt(out[block]))


def gen(block):
    """Variables that are written in the block.
    """
    return {i['dest'] for i in block if 'dest' in i}


def use(block):
    """Variables that are read before they are written in the block.
    """
    defined = set()  # Locally defined.
    used = set()
    for i in block:
        used.update(v for v in var_args(i) if v not in defined)
        if 'dest' in i:
            defined.add(i['dest'])
    return used


def backward_use(out, block, in_):
    ret = [out]
    used = out
    for i in block[-1::-1]:
        if 'dest' in i:
            used.discard(i['dest'])
        used.update(v for v in var_args(i))
        ret.append(set(used))
    assert in_==used
    return ret


def cprop_transfer(block, in_vals):
    out_vals = dict(in_vals)
    for instr in block:
        if 'dest' in instr:
            if instr['op'] == 'const':
                out_vals[instr['dest']] = instr['value']
            else:
                out_vals[instr['dest']] = '?'
    return out_vals


def cprop_merge(vals_list):
    out_vals = {}
    for vals in vals_list:
        for name, val in vals.items():
            if val == '?':
                out_vals[name] = '?'
            else:
                if name in out_vals:
                    if out_vals[name] != val:
                        out_vals[name] = '?'
                else:
                    out_vals[name] = val
    return out_vals


ANALYSES = {
    # A really really basic analysis that just accumulates all the
    # currently-defined variables.
    'defined': Analysis(
        True,
        init=set(),
        merge=union,
        transfer=lambda block, in_: in_.union(gen(block)),
    ),

    # Live variable analysis: the variables that are both defined at a
    # given point and might be read along some path in the future.
    'live': Analysis(
        False,
        init=set(),
        merge=union,
        transfer=lambda block, out: use(block).union(out - gen(block)),
    ),

    # A simple constant propagation pass.
    'cprop': Analysis(
        True,
        init={},
        merge=cprop_merge,
        transfer=cprop_transfer,
    ),
}


def coloring(constraints, regs):
    variables = []
    for each in constraints:
        variables += each
    variables = set(variables)
    print_stats("varaibels: ", variables)

    nodes = {name:Node(name) for name in variables}
    for each in constraints:
        if len(each) >= 2:
            for i in range(len(each)):
                for j in range(i+1, len(each)):
                    left = nodes[list(each)[i]]
                    right = nodes[list(each)[j]]
                    add_edge(left, right)
    return optimistic_coloring([nodes[name] for name in nodes], regs)


def print_stats(*args):
    if PRINT_STATS:
        sys.stdout.write('# ')
        print(*args)


def code_transform(bril, var_to_reg):
    for f in bril["functions"]:
        for instr in f["instrs"]:
            #print(instr)
            if 'op' in instr:
                if instr['op'] == 'br':
                    # Only the first argument to a branch is a variable.
                    new_var = (var_to_reg(instr['args'][0]))
                    instr['args'][0] = new_var
                elif instr['op'] in TERMINATORS:
                    # Unconditional branch, for example, has no variable arguments.
                    pass
                elif "args" in instr:
                    for i,arg in enumerate(instr['args']):
                        new_var = var_to_reg(arg)
                        instr['args'][i] = new_var
            if 'dest' in instr:
                instr['dest'] = var_to_reg(instr['dest'])


def liveness_analysis(func):
    # Form the CFG.
    blocks = cfg.block_map(form_blocks(func))
    cfg.add_terminators(blocks)

    in_, out = df_worklist(blocks, ANALYSES['live'])
    constraints = []
    for block in blocks:
        constraints += backward_use(out[block], blocks[block], in_[block])
    return constraints


def regalloc(func, regs):
    constraints = liveness_analysis(func)
    colored, spilled = coloring(constraints, len(regs))
    regmap = {each.name:regs[each.color-1] for each in colored}
    return regmap,colored,spilled
