---
name: scrawl3d
description: Design and build 3D-printable parts and models in scrawl3d (or local Jarvis CAD) through its MCP tools. Use when asked to model, fix or change a part, build an assembly (enclosure, bracket, gearbox, scale model, car), make something printable, or export it for a slicer. Covers the build workflow, coordinate conventions, which tool fits which shape, printability (DfAM), materials and export.
---

# Building in scrawl3d

scrawl3d is a browser CAD workspace for 3D printing; its MCP tools act on the
user's **open tab**, live. Units are mm, Z up, the print bed is z = 0. Every
change is an undoable step and is auto-saved in the browser.

## Rules that protect the user's work

- **Start with `get_scene`.** Know what is open before changing anything. If
  `unsaved` is true and the scene is not yours, it is the user's work.
- **Never discard work.** `new_project` refuses when there are unsaved
  changes: ask the user, don't pass `discard: true` on your own.
- **Check which project answered.** If the tab you were using closed or paused,
  calls move to another open tab, which may hold a different project. A
  surprising `get_scene` (other name, other parts) means stop and ask.
- **Save when a step is done:** `save_project` with a name.
- **Verify with numbers, not only pictures.** `screenshot` can lag in a
  background tab; `get_scene` bounds and `get_bounds` don't.

## Workflow

1. **Plan in numbers first.** Write down the main dimensions, the origin, and
   which way the thing faces before the first call (e.g. car faces −x, wheels
   at x ±54, wheel centre z 13.5). Every later placement follows from them.
2. **Block out with primitives** (`add_part` box / cylinder / sphere), placed
   with `move` (anchor `base` puts a part on a surface: position z = that
   surface). Check proportions with a screenshot before detailing.
3. **Shape with sketches** where a primitive is wrong: `sketch_part` for
   profiles (extrude or revolve), `loft` for bodies that change section along
   their length, `silhouette` for a body from side + top (+ front) views.
4. **Combine and cut**: `boolean` (union / subtract / intersect: tools are
   used up and stay in the target's history), `cut_sketch` for windows, slots
   and lettering, negative parts (`set_negative`) for cuts that must stay
   movable.
5. **Functional features last**, on finished surfaces: `add_feature` (holes,
   counterbores, heat-set inserts, nut pockets, threads, bearing seats, vents,
   connector cutouts, text), `mount_board`, `make_lid`.
6. **Round edges** (`fillet`, `round_edge`) after the cuts that touch them.
7. **Organise**: `group_parts` into named layers (Body, Wheels, Glass,
   Interior…), names that say what a part is (they pick its material).
8. **Check printability** (`check_printability`), fix, then export.

Use `batch` for runs of simple calls (up to 50, ids from earlier results are
in each result). Not for `screenshot` or `export_stl`.

## Coordinates and orientation cheatsheet

- `add_part` position = the base centre of the part.
- `sketch_part` planes:
  - `xy`: top view, extrudes up +z.
  - `xz`: side view (sketch x → x, sketch y → z), extrudes toward −y.
  - `yz`: front view (sketch x → y, sketch y → z), extrudes toward +x.
  - `revolve` spins around the sketch Y axis, which becomes height; only x ≥ 0
    counts. Then `move` it into place (rotate to lay the axis where needed).
- `loft` stacks sections up Z. To lay a loft along X (a fuselage, a car body):
  `move` rotation [90, 90, 0] maps loft z → X, section u → Y, v → Z.
- `move` rotation is XYZ Euler degrees. A cylinder (axis Z) pointing along unit
  direction d = (nx, ny, nz): rotation [atan2(−ny, nz), asin(nx), 0] in
  degrees, positioned at the midpoint of its run.
- `mirror` plane `xz` flips Y (left ↔ right side of a car that faces ±x), `yz`
  flips X. Model one side, mirror, `merge: true` when they must be one solid.
- `pattern` count **includes the original**, and its returned ids include the
  original: dedupe before passing them on (a duplicate id breaks `boolean`).

## Choosing the tool for a shape

| Shape | Tool |
| --- | --- |
| Plates, blocks, standoffs, pins | `add_part` box / cylinder (r rounds edges) |
| Profile with holes (bracket, flange, rim face, spoke wheel) | `sketch_part` extrude (inner shapes become holes) |
| Turned parts (tyre, knob, bottle, nozzle, barrel) | `sketch_part` revolve |
| Fuselage, car body, boat hull, duct | `loft` sections, or `silhouette` from views |
| Blades and fins | `loft` with `naca` sections, then `pattern` round the hub |
| Gears, racks, planetary, cycloidal, bolts, nuts, hinges | `add_part` parametric types |
| Windows, slots, vents through a curved body | `cut_sketch` |
| Screw holes, inserts, nut traps, threads, bearing seats | `add_feature` |
| Enclosure lid | `make_lid` on the open container |
| Too big for the bed | `cut` across an axis, then join the halves (see printing reference) |

Details and worked examples: [references/recipes.md](references/recipes.md).

## Making it printable

Run `check_printability` (one part by id, or every visible part) before export
and act on it; rules and fixes in [references/printing.md](references/printing.md).

- **Overhangs past 45°** need support: turn the part (`update_part
  print_rotation`, take the first of `ways_to_lay`), chamfer the underside at
  45°, or split it.
- **Walls**: at least two nozzle lines (≈ 1.3 mm on a 0.6 nozzle, 0.9 mm on a
  0.4). Under one line the slicer drops them.
- **Print orientation is separate from placement**: turning a part in the
  scene moves it in the assembly; `print_rotation` only changes how it lies on
  the plate.
- **Materials**: every part has one (`update_part material`, or on a group).
  On auto the name decides: tyre / seal / grip / foot → TPU, glass / lens /
  light → clear PETG, hotend / exhaust → ASA, else PLA. Name parts for what
  they are and the material follows.
- **Export**: `export_stl` kind `plate` (laid out), `assembly` (in place) or
  `body`; `material` narrows a plate to one filament. The user's File ›
  Export › By material gives one 3MF per material for the slicer.

## Scale models

At 1:24 or smaller, real details fall under the nozzle. Keep visible details
≥ 2 lines thick (spokes, mirrors, spoilers), exaggerate thin parts slightly,
and model details that would be lost (panel lines, badges) as shallow cuts
(≥ 0.4 mm deep) rather than raised hair-thin ribs. Parts that are a different
material (tyres, glass) are separate bodies so they print separately.

## When the user gives feedback

Treat visual feedback as geometry: "tyres poke through the hood" means read the
bounds of both and fix the overlap in numbers; "not on the side but on top"
means change the sketch plane. Re-check with `get_scene` bounds and a
screenshot from the view that shows the problem (`front`, `top`, `iso`…).
