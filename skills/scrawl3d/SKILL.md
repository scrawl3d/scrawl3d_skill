---
name: scrawl3d
description: Design and build 3D-printable parts and models in scrawl3d (or local Jarvis CAD) through its MCP tools. Use when asked to model, fix or change a part, rework an imported STL, build an assembly (enclosure, bracket, gearbox, scale model, car), make something printable, or export it for a slicer. Covers the build workflow, editing existing parts, measuring, coordinate conventions, which tool fits which shape, printability (DfAM), materials and export.
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
| Pipes, cables, gaskets, springs | `sweep` a profile along a 3D path |
| Sizes that follow each other (wall = 2) | `values`, then `{"expr":"wall * 2"}` in place of a number |
| Longer or shorter, ends unchanged | `stretch` (`scale` also resizes the holes) |
| Change a hole already in a part | `edit_hole` (imported meshes too) |
| Will it hold? | `simulate` |

Details and worked examples: [references/recipes.md](references/recipes.md).

## Editing an existing part

Imported STLs and finished parts have no parameters to change, so measure first
and make every edit something you can take back.

1. **Find out where the user means.** `marks` gives the points they numbered,
   with the face direction at each; `last_click` gives "this" and "here". Read
   them again before placing anything, because the user can move a mark between
   messages and keep its number.
2. **Measure, don't guess.** `slice` gives a flat cut on any plane: outlines,
   holes, sizes, and fitted circles and rectangles. Use it to map a shape.
   `probe` gives single wall thicknesses and surface positions. Don't trust a
   document's labels or dimensions over the mesh, or over the user.
3. **Cut with negatives** (`set_negative`) so a pocket stays movable. A negative
   cuts every part it overlaps, and it also cuts solids you merge in later.
4. **Fill with `boolean` union.** Let a fill overlap into the neighbouring
   material; where it runs into a pocket, the negative trims it back. Merged
   solids stay as edits in the body's history, so `edit_op` with `delete` takes
   one back out.
5. **Make room with `stretch`.** It cuts at the plane and everything on the +
   side moves, so holes and marks on that side change coordinates. Measure again
   afterwards.
6. **Check the result:** `probe` the walls you changed and the paths that must
   stay clear, and `check_clashes` for anything that has to fit against another
   part. Report what you measured, and say what you assumed.
7. **Save before `open_project`.** It replaces the scene.

Traps:

- **Start a `probe` ray outside the body.** A ray that starts inside solid reports
  the point where it leaves as its first hit, and `thickness` then measures the
  empty space beyond. A hit whose normal faces back along the ray, a long way
  from where you expected a surface, usually means this.
- **`probe` gives only the first wall for each body.** No hits means nothing lies
  on that line at all. To map a shape, send a grid of rays in `batch`, or use
  `slice`.
- **Place negatives with `move` anchor `origin`.** Until a part is negative, other
  negatives clip the bounds that anchors `base` and `center` use, which can shift
  it. A cylinder's origin is its base centre.
- **A cylinder rotated [90, 0, 0] runs from its origin toward −Y.**
- **Confirm a hole's depth with `probe`.** `edit_hole` can misread how long a bore
  is on an imported mesh, and then resize only part of it.
- **A cut can skim something else.** Lengthening a negative to clear a path may
  shave a neighbouring face, so check what it now crosses.

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
