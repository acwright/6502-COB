#!/usr/bin/env node
// check-schematics — evaluate the COB cards' address decoding from the schematics themselves.
//
// The same method as 6502-ACE's Tests/check-schematics.mjs, whose RAM bank latches were wrong
// twice while the logic looked right on paper. This does not trust anyone's reading of the
// gates. It asks KiCad for each card's netlist, builds the glue logic from the parts it finds
// there, fits the card's jumpers, and then drives every address, as a read and as a write, with
// PHI2 high and low — 262,144 bus states — and compares every select, strobe and latch enable
// with the memory map below. Nets nobody drives come out as unknown, so a missing wire fails
// too.
//
// Usage:  node Tests/check-schematics.mjs
// Needs kicad-cli: on the PATH, at the macOS default, or named by KICAD_CLI.

import { execFileSync } from 'node:child_process'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const HW = join(ROOT, 'Hardware')

// ---- The cards, as built --------------------------------------------------------------

// The RAM Card's two windows are chosen with J3: odd pins are the 74HC138's outputs, one per
// 1 KB IO slot from $8000, and even pins are the two window selects, CSB0 (pins 2, 6, 10, 14)
// and CSB1 (4, 8, 12, 16). So window 0 can be at IO 1, 3, 5 or 7 and window 1 at IO 2, 4, 6
// or 8. Window 0 is the AS6C4008's lower 256 KB and window 1 its upper. On Rev 1.0, CSB0
// drives A18 and JP1 enables the one bank latch's outputs.
const slot = (k) => [`J3.${2 * k + 1}`, `J3.${2 * k + 2}`]   // IO slot k ($8000 + k * $400)
const inSlot = (a, k) => a >= 0x8000 + k * 0x400 && a < 0x8400 + k * 0x400
const hex = (k) => (0x8000 + k * 0x400).toString(16).toUpperCase()
const regWrite = (a, r, p) => (a & 0x3FF) === 0x3FF && !r && p

// Rev 1.1 has the ACE 1.1's circuit (KICAD.md K11): a latch for each window, U2 for window 0
// and U9 for window 1, each with its outputs on only while its own window is selected, and
// loaded only by a write to $x3FF of that window with PHI2 high. It has no pull-ups on the
// window selects, so a card runs with one shunt per window, never none: every one of those
// 16 settings is checked.
const REV11 = []
for (const k0 of [0, 2, 4, 6]) for (const k1 of [1, 3, 5, 7]) {
  REV11.push({
    name: `RAM Card Rev 1.1, IO ${k0 + 1} ($${hex(k0)}) and IO ${k1 + 1} ($${hex(k1)})`,
    board: 'RAM Card/Rev 1.1/RAM Card.kicad_sch',
    jumpers: [slot(k0), slot(k1)],
    window: (a) => inSlot(a, k0) ? 0 : inSlot(a, k1) ? 1 : -1,
    latches: [
      ['U2', 11, 'window 0 latch LE', (a, r, p, w) => w === 0 && regWrite(a, r, p) ? 1 : 0],
      ['U9', 11, 'window 1 latch LE', (a, r, p, w) => w === 1 && regWrite(a, r, p) ? 1 : 0],
      ['U2', 1, 'window 0 latch /OE', (a, r, p, w) => w === 0 ? 0 : 1],
      ['U9', 1, 'window 1 latch /OE', (a, r, p, w) => w === 1 ? 0 : 1]
    ],
    ram: 'U1'
  })
}

const CONFIGS = [
  {
    // Rev 1.0 is deprecated, and kept as it was made. It has one bank latch for both windows,
    // and R1 and R2 pull the window selects to GND, so a window with no jumper is selected
    // everywhere. Both windows must therefore be jumpered, and the setting the BIOS expects
    // is the one checked here.
    name: 'RAM Card Rev 1.0, IO 1 and IO 2',
    board: 'RAM Card/Rev 1.0/RAM Card.kicad_sch',
    jumpers: [slot(0), slot(1), ['JP1.1', 'JP1.2']],
    // a = address, r = 1 for a read, p = PHI2. A window is 0 (CSB0, $8000) or 1 (CSB1, $8400).
    window: (a) => a >= 0x8000 && a < 0x8400 ? 0 : a >= 0x8400 && a < 0x8800 ? 1 : -1,
    // One latch: a write to the last byte of either window loads it.
    latches: [['U2', 11, 'bank latch LE', (a, r, p, w) => w >= 0 && regWrite(a, r, p) ? 1 : 0]],
    ram: 'U1'
  },
  ...REV11
]

// The AS6C4008's pins the map checks.
const RAM = { ce: 22, oe: 24, we: 29, a18: 1 }

// ---- Netlists -------------------------------------------------------------------------

function kicadCli() {
  const candidates = [process.env.KICAD_CLI, '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli', 'kicad-cli']
  for (const c of candidates.filter(Boolean)) {
    try { execFileSync(c, ['version'], { stdio: 'ignore' }); return c } catch {}
  }
  throw new Error('kicad-cli not found; set KICAD_CLI')
}

function sexpr(text) {
  const stack = [[]]
  const re = /\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))/gy
  let m
  while ((m = re.exec(text)) && m[0].length) {
    if (m[1]) stack.push([])
    else if (m[2]) { const x = stack.pop(); stack[stack.length - 1].push(x) }
    else stack[stack.length - 1].push(m[3] !== undefined ? m[3].replace(/\\(.)/g, '$1') : m[4])
  }
  return stack[0][0]
}
const kids = (node, key) => node.filter(c => Array.isArray(c) && c[0] === key)
const kid = (node, key) => kids(node, key)[0]

// The card edge's pins are named (A0, RWB, PHI2), so pins are kept as strings throughout.
const netlists = new Map()
function netlist(cli, sch, dir) {
  if (!netlists.has(sch)) netlists.set(sch, readNetlist(cli, sch, dir))
  return netlists.get(sch)
}
function readNetlist(cli, sch, dir) {
  const out = join(dir, `${Math.random().toString(36).slice(2)}.net`)
  execFileSync(cli, ['sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', out, join(HW, sch)], { stdio: 'ignore' })
  const root = sexpr(readFileSync(out, 'utf8'))
  const comps = new Map()
  for (const c of kids(kid(root, 'components'), 'comp')) comps.set(kid(c, 'ref')[1], kid(c, 'value')[1])
  const pinNet = new Map()
  for (const n of kids(kid(root, 'nets'), 'net')) {
    for (const x of kids(n, 'node')) pinNet.set(`${kid(x, 'ref')[1]}.${kid(x, 'pin')[1]}`, kid(n, 'name')[1])
  }
  return { comps, pinNet }
}

// Joins nets: jumpers fitted.
function assemble(cli, cfg, dir) {
  const { comps, pinNet } = netlist(cli, cfg.board, dir)
  const parent = new Map([...new Set(pinNet.values())].map(n => [n, n]))
  const find = (x) => { while (parent.get(x) !== x) x = parent.get(x); return x }
  for (const [a, b] of cfg.jumpers) {
    if (!pinNet.has(a) || !pinNet.has(b)) throw new Error(`${cfg.board}: cannot fit a jumper from ${a} to ${b}`)
    const x = find(pinNet.get(a)), y = find(pinNet.get(b))
    if (x !== y) parent.set(y, x)
  }
  const net = (ref, pin) => { const n = pinNet.get(`${ref}.${pin}`); return n === undefined ? undefined : find(n) }
  return { comps, net, vcc: find('VCC'), gnd: find('GND') }
}

// ---- The logic ------------------------------------------------------------------------

const X = 'X'
const nand = ins => ins.includes(0) ? 1 : ins.every(v => v === 1) ? 0 : X
const and = ins => ins.includes(0) ? 0 : ins.every(v => v === 1) ? 1 : X
const nor = ins => ins.includes(1) ? 0 : ins.every(v => v === 0) ? 1 : X

const GATES = {
  '74HC00': { fn: nand, units: [[[1, 2], 3], [[4, 5], 6], [[9, 10], 8], [[12, 13], 11]] },
  '74HC02': { fn: nor, units: [[[2, 3], 1], [[5, 6], 4], [[8, 9], 10], [[11, 12], 13]] },
  '74HC21': { fn: and, units: [[[1, 2, 4, 5], 6], [[9, 10, 12, 13], 8]] },
  '74HC30': { fn: nand, units: [[[1, 2, 3, 4, 5, 6, 11, 12], 8]] }
}
const Y138 = [15, 14, 13, 12, 11, 10, 9, 7]

function compile(board) {
  const gates = []
  for (const [ref, value] of board.comps) {
    const g = GATES[value === '74HCT00' ? '74HC00' : value]
    if (g) {
      for (const [ins, out] of g.units) {
        const o = board.net(ref, out)
        if (o !== undefined) gates.push({ ins: ins.map(p => board.net(ref, p)), out: o, fn: g.fn })
      }
    } else if (value === '74HC138') {
      const ins = [1, 2, 3, 4, 5, 6].map(p => board.net(ref, p))
      Y138.forEach((pin, k) => {
        const o = board.net(ref, pin)
        if (o === undefined) return
        gates.push({
          ins, out: o,
          fn: ([a, b, c, e1, e2, e3]) => {
            if (e1 === 1 || e2 === 1 || e3 === 0) return 1
            if ([a, b, c, e1, e2, e3].includes(X)) return X
            return (a | b << 1 | c << 2) === k ? 0 : 1
          }
        })
      })
    }
  }
  // Schottky diodes, cathode (pin 1) to a select and anode (pin 2) to a pulled-up net: a wired
  // AND, low when any cathode is low (the ACE's D2 and D3, the RAM Card 1.1's D1 and D2).
  const anodes = new Map()
  for (const [ref, value] of board.comps) {
    if (!/^D\d+$/.test(ref) || !/BAT|schottky/i.test(value)) continue
    const k = board.net(ref, 1), a = board.net(ref, 2)
    if (a !== undefined) anodes.set(a, [...(anodes.get(a) ?? []), k])
  }
  for (const [a, ks] of anodes) gates.push({ ins: [...ks, board.vcc], out: a, fn: and })
  const counts = new Map()
  for (const g of gates) counts.set(g.out, (counts.get(g.out) ?? 0) + 1)
  for (const [n, k] of counts) if (k > 1) throw new Error(`net ${n} has ${k} gate outputs driving it — two jumpers in one J3 column?`)
  // Resistors to VCC or GND hold a net nobody drives.
  const holds = new Map()
  for (const ref of board.comps.keys()) {
    if (!/^R\d+$/.test(ref)) continue
    const a = board.net(ref, 1), b = board.net(ref, 2)
    for (const [rail, v] of [[board.vcc, 1], [board.gnd, 0]]) {
      if (a === rail && b !== undefined) holds.set(b, v)
      if (b === rail && a !== undefined) holds.set(a, v)
    }
  }
  return { gates, holds, driven: new Set(counts.keys()) }
}

function evaluate(board, logic, inputs) {
  const val = new Map(inputs)
  val.set(board.vcc, 1); val.set(board.gnd, 0)
  for (const [n, v] of logic.holds) if (!logic.driven.has(n) && !inputs.has(n)) val.set(n, v)
  for (let pass = 0; pass < 32; pass++) {
    let changed = false
    for (const g of logic.gates) {
      const v = g.fn(g.ins.map(n => n === undefined ? X : val.has(n) ? val.get(n) : X))
      if (val.get(g.out) !== v) { val.set(g.out, v); changed = true }
    }
    if (!changed) return val
  }
  throw new Error('the logic did not settle: is there a loop?')
}

// ---- Rules ----------------------------------------------------------------------------

function checkDecode(board, cfg) {
  const logic = compile(board)
  const edge = (pin) => board.net('J1', pin)
  const addr = [...Array(16)].map((_, i) => edge(`A${i}`))
  const rwb = edge('RWB'), phi2 = edge('PHI2')
  const failures = new Map()
  const fail = (what, a, r, p, got, want) => {
    const f = failures.get(what) ?? { count: 0, examples: [] }
    f.count++
    if (f.examples.length < 6) f.examples.push(`$${a.toString(16).toUpperCase().padStart(4, '0')} ${r ? 'read ' : 'write'} PHI2=${p}: got ${got}, want ${want}`)
    failures.set(what, f)
  }
  const low = (cond) => cond ? 0 : 1
  const checks = [
    [cfg.ram, RAM.ce, 'RAM /CE', (a, r, p, w) => low(w >= 0)],
    [cfg.ram, RAM.oe, 'RAM /OE', (a, r, p) => low(r && p)],
    [cfg.ram, RAM.we, 'RAM /WE', (a, r, p) => low(!r && p)],
    [cfg.ram, RAM.a18, 'RAM A18', (a, r, p, w) => w >= 0 ? w : '-'],
    ...cfg.latches
  ].map(([ref, pin, what, want]) => {
    const n = board.net(ref, pin)
    if (n === undefined) throw new Error(`${ref} pin ${pin} (${what}) is not in the netlist`)
    return [n, what, want]
  })
  for (let p = 0; p <= 1; p++) for (let r = 0; r <= 1; r++) {
    for (let a = 0; a < 0x10000; a++) {
      const inputs = new Map()
      addr.forEach((n, i) => inputs.set(n, a >> i & 1))
      inputs.set(rwb, r); inputs.set(phi2, p)
      const val = evaluate(board, logic, inputs)
      const w = cfg.window(a)
      for (const [n, what, want] of checks) {
        const expected = want(a, r, p, w)
        const got = val.has(n) ? val.get(n) : X
        if (expected !== '-' && got !== expected) fail(what, a, r, p, got, expected)
      }
      // The card drives the data bus only on a read of its own window, with PHI2 high.
      const v = (pin) => val.get(board.net(cfg.ram, pin))
      const drives = v(RAM.ce) === 0 && v(RAM.oe) === 0
      if (drives !== (w >= 0 && r === 1 && p === 1)) fail('card driving the data bus', a, r, p, drives, !drives)
    }
  }
  return [...failures].map(([what, f]) => `${what}: wrong in ${f.count} bus states, e.g.\n        ${f.examples.join('\n        ')}`)
}

// ---- Main -----------------------------------------------------------------------------

const cli = kicadCli()
const dir = mkdtempSync(join(tmpdir(), 'cob-check-'))
let failed = 0
try {
  for (const cfg of CONFIGS) {
    const errs = checkDecode(assemble(cli, cfg, dir), cfg)
    console.log(cfg.name)
    console.log(`  ${errs.length ? 'FAIL' : 'ok  '}  address decoding (262,144 bus states)`)
    for (const e of errs) console.log(`      ${e}`)
    failed += errs.length
  }
} finally {
  rmSync(dir, { recursive: true, force: true })
}
process.exit(failed ? 1 : 0)
