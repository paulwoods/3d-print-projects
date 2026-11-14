# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A collection of 3D-print projects, one directory per project. Models are code-CAD: a Python script builds the solids with `manifold3d` and exports STLs via `trimesh`. There is no build system, test suite, or linter.

Currently one project: `pi5-case/`, a wall-mount Raspberry Pi 5 case.

## Commands

```sh
pip install manifold3d trimesh numpy
cd pi5-case/v2 && python3 pi5_wall_case.py
```

The script writes its STLs to the **current working directory**, so run it from inside the version directory or it will drop files elsewhere.

The printed summary is the only check: every part must report `watertight=True`, and the extents, Z heights, and "Stack screw thread into HAT standoff" length should be sane after any parameter change.

## Layout and versioning

Each `vN/` directory is a complete, self-contained snapshot (script + generated STLs + `.3mf`), one per hardware configuration, not a history of the same design:

- `pi5-case/v1`: official Active Cooler + Raspberry Pi M.2 HAT+; the Pi screws into heat-set inserts in the standoffs.
- `pi5-case/v2`: 52Pi U2500 HAT (dual 2.5GbE + NVMe), no cooler; four M2.5 x 16 screws enter from the back of the case through counterbored standoffs into the HAT's female standoffs. Also has `assemble.html`, the hand-written assembly guide.

A change for a different hardware stack goes in a new `vN/` copy; leave earlier versions as they are.

The STLs are generated output committed alongside the script, so regenerate them whenever the script changes. The `.3mf` files are not produced by the script (they come from the slicer) and go stale when the STLs change.

## Model conventions (`pi5_wall_case.py`)

- Units are mm. The origin is the Pi PCB corner, not the case corner: the board spans X 0..85, Y 0..56, and Z = 0 is the back of the case against the wall. Case extents are therefore negative on the low sides.
- Orientation when hung: X+ (USB/Ethernet end) points down, X- is up. Y = 0 is the USB-C/HDMI edge, Y = 56 the GPIO edge. Vents and keyhole slots are oriented around this.
- All dimensions are named constants in the `parameters` block, with Z levels and interior/outer extents computed in the `derived` block. Change a parameter there; do not put literal dimensions into the geometry functions. Values commented as "measured" came from the physical hardware.
- `box`, `cyl`, and `slot_x` take absolute coordinates (`z0`, `z1`, and so on), not sizes. Geometry is built by adding and subtracting these with `+`, `-`.
- `base()`, `lid()`, and `template()` each return one part modelled in its assembled position. Reorientation for printing (the lid is flipped, everything is moved to the origin) happens only in `__main__`.
- The drill template's holes mark where the wall screws end up (the resting end of each keyhole, `KEY_X - KEY_SLOT_L`), not the keyhole entry holes.

## Working with the user

- Always ask questions one at a time: ask one, wait for the answer, then ask the next.
