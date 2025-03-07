#!/usr/bin/env node
import * as bril from './bril';
import {readStdin, unreachable} from './util';

const argCounts: {[key in bril.OpCode]: number | null} = {
  add: 2,
  mul: 2,
  sub: 2,
  div: 2,
  id: 1,
  lt: 2,
  le: 2,
  gt: 2,
  ge: 2,
  eq: 2,
  not: 1,
  and: 2,
  or: 2,
  print: null,  // Any number of arguments.
  br: 3,
  jmp: 1,
  ret: 0,
  nop: 0,
};

const regSign = 'r_*';

type Value = boolean | BigInt;
type Env = Map<bril.Ident, Value>;
type Count = [number, number];

class counting {
  count = [0, 0]
}

function mem_access(count: counting, ld_inc: number, st_inc: number) {
  let loads = count.count[0];
  let stores= count.count[1];
  loads = loads + ld_inc;
  stores= stores+ st_inc;
  count.count = [loads, stores];
  return count;
}

function regs_con(instr: bril.Constant, args: number) {
  var i: number;
  var loads = 0;
  var stores= 0;
  var regex = RegExp(regSign);
  if (!(regex.test(instr.dest))) {
      stores = stores + 1;
  }
  return {loads, stores};
}

function regs_val(instr: bril.ValueOperation, args: number) {
  var i: number;
  var loads = 0;
  var stores= 0;
  var regex = RegExp(regSign);
  for (i = 0; i < args; i++){
    if (!(regex.test(instr.args[i])))
        loads = loads + 1;
  }
  //if (instr.hasOwnProperty('dest')) {
  if (!(regex.test(instr.dest))) {
      stores = stores + 1;
  }
  return {loads, stores};
}

function regs_eff(instr: bril.EffectOperation, args: number) {
  var i: number;
  var loads = 0;
  var stores= 0;
  var regex = RegExp(regSign);
  for (i = 0; i < args; i++){
    if (!(regex.test(instr.args[i])))
        loads = loads + 1;
  }
  return {loads, stores};
}

function get(env: Env, ident: bril.Ident) {
  let val = env.get(ident);
  if (typeof val === 'undefined') {
    throw `undefined variable ${ident}`;
  }
  return val;
}

/**
 * Ensure that the instruction has exactly `count` arguments,
 * throwing an exception otherwise.
 */
function checkArgs(instr: bril.Operation, count: number) {
  if (instr.args.length != count) {
    throw `${instr.op} takes ${count} argument(s); got ${instr.args.length}`;
  }
}

function getInt(instr: bril.Operation, env: Env, index: number) {
  let val = get(env, instr.args[index]);
  if (typeof val !== 'bigint') {
    throw `${instr.op} argument ${index} must be a number`;
  }
  return val;
}

function getBool(instr: bril.Operation, env: Env, index: number) {
  let val = get(env, instr.args[index]);
  if (typeof val !== 'boolean') {
    throw `${instr.op} argument ${index} must be a boolean`;
  }
  return val;
}

/**
 * The thing to do after interpreting an instruction: either transfer
 * control to a label, go to the next instruction, or end thefunction.
 */
type Action =
  {"label": bril.Ident} |
  {"next": true} |
  {"end": true};
let NEXT: Action = {"next": true};
let END: Action = {"end": true};

/**
 * Interpret an instruction in a given environment, possibly updating the
 * environment. If the instruction branches to a new label, return that label;
 * otherwise, return "next" to indicate that we should proceed to the next
 * instruction or "end" to terminate the function.
 */
function evalInstr(instr: bril.Instruction, env: Env, count: counting): Action {
  // Check that we have the right number of arguments.
  if (instr.op !== "const") {
    let count = argCounts[instr.op];
    if (count === undefined) {
      throw "unknown opcode " + instr.op;
    } else if (count !== null) {
      checkArgs(instr, count);
    }
  }

  switch (instr.op) {
  case "const":
    // Ensure that JSON ints get represented appropriately.
    let value: Value;
    if (typeof instr.value === "number") {
      value = BigInt(instr.value);
    } else {
      value = instr.value;
    }

    env.set(instr.dest, value);
    let {loads, stores} = regs_con(instr, 0);
    count = mem_access(count, loads, stores);
    return NEXT;

  case "id": {
    let val = get(env, instr.args[0]);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 1);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "add": {
    let val = getInt(instr, env, 0) + getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "mul": {
    let val = getInt(instr, env, 0) * getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "sub": {
    let val = getInt(instr, env, 0) - getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "div": {
    let val = getInt(instr, env, 0) / getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "le": {
    let val = getInt(instr, env, 0) <= getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "lt": {
    let val = getInt(instr, env, 0) < getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "gt": {
    let val = getInt(instr, env, 0) > getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "ge": {
    let val = getInt(instr, env, 0) >= getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
   return NEXT;
  }

  case "eq": {
    let val = getInt(instr, env, 0) === getInt(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "not": {
    let val = !getBool(instr, env, 0);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 1);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "and": {
    let val = getBool(instr, env, 0) && getBool(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "or": {
    let val = getBool(instr, env, 0) || getBool(instr, env, 1);
    env.set(instr.dest, val);
    let {loads, stores} = regs_val(instr, 2);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "print": {
    let values = instr.args.map(i => get(env, i).toString());
    console.log(...values);
    let {loads, stores} = regs_eff(instr, instr.args.length);
    count = mem_access(count, loads, stores);
    return NEXT;
  }

  case "jmp": {
    return {"label": instr.args[0]};
  }

  case "br": {
    let cond = getBool(instr, env, 0);
    let {loads, stores} = regs_eff(instr, 1);
    count = mem_access(count, loads, stores);
    if (cond) {
      return {"label": instr.args[1]};
    } else {
      return {"label": instr.args[2]};
    }
  }
  
  case "ret": {
    return END;
  }

  case "nop": {
    return NEXT;
  }
  }
  unreachable(instr);
  throw `unhandled opcode ${(instr as any).op}`;
}

function evalFunc(func: bril.Function) {
  let env: Env = new Map();
  let count = new counting();
  count.count = [0, 0];
  for (let i = 0; i < func.instrs.length; ++i) {
    let line = func.instrs[i];
    if ('op' in line) {
      let action = evalInstr(line, env, count);

      if ('label' in action) {
        // Search for the label and transfer control.
        for (i = 0; i < func.instrs.length; ++i) {
          let sLine = func.instrs[i];
          if ('label' in sLine && sLine.label === action.label) {
            break;
          }
        }
        if (i === func.instrs.length) {
          throw `label ${action.label} not found`;
        }
      } else if ('end' in action) {
        return;
      }
    }
  }
  console.log("#load:",count.count[0]);
  console.log("#store:",count.count[1]);
}

function evalProg(prog: bril.Program) {
  for (let func of prog.functions) {
    if (func.name === "main") {
      evalFunc(func);
    }
  }
}

async function main() {
  let prog = JSON.parse(await readStdin()) as bril.Program;
  evalProg(prog);
}

// Make unhandled promise rejections terminate.
process.on('unhandledRejection', e => { throw e });

main();
