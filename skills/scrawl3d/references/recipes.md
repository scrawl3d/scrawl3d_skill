# Recipes

Worked patterns, as tool calls. Ids come from each call's result; `…` marks
values you fill in. Sketch shapes: `rect {cx,cy,w,h,r?,rot?}`,
`circle {cx,cy,d}`, `ellipse`, `slot`, `polygon {cx,cy,R,n}`,
`path {points, bulges?, handles?}`, `spline {points, tension?}`,
`naca {code, chord}`.

## Enclosure for a circuit board, with a lid

1. Board for the fit check: `add_part {type: "board", params: {board: "…"}}`.
2. Box around it: `add_part box {x, y, z, r: 2}`, inner pocket as a second box
   2 mm smaller per side, `boolean subtract` (box keeps it as history).
3. Put the board in, then `mount_board {board_id, how: "inserts"}`: heat-set
   insert holes appear under its mounting holes in whatever is below.
4. Cutouts: `add_feature {feature: "connector", params: {kind: "…"}}` on the
   wall the port faces (`from: "-y"` etc.), vents with `feature: "vent"`.
5. `make_lid {body_id: box, style: "inset", fit: 0.2}`.
6. Hide the board (`update_part hidden: true`) before export: it is not
   printed.

## Bracket or plate from a sketch

One `sketch_part` beats a stack of booleans: outline plus holes in one go.

```json
{"shapes": [
  {"type": "path", "points": [[0,0],[60,0],[60,8],[12,8],[12,40],[0,40]]},
  {"type": "circle", "cx": 6, "cy": 32, "d": 3.4},
  {"type": "slot", "cx": 40, "cy": 4, "w": 12, "h": 3.4}],
 "op": "extrude", "h": 20, "plane": "xz", "corner": 1}
```

Then `fillet` the outer edges and `round_edge` the inside corner of the L
(stress collects there). Countersinks: `add_feature countersink` at the hole.

## Wheel: tyre, rim barrel, spoke face

A real wheel is three bodies: tyre (TPU), barrel and spoke face (one material).

- **Tyre:** `sketch_part revolve` of the half cross-section (x = radius,
  y = width), e.g. a rounded rect from x 9.2 to 13.5. Name it "Tyre": it
  prints in TPU.
- **Barrel:** a revolve of a thin ring just inside the tyre (inner radius
  leaves room for the brake).
- **Spoke face:** draw it as a sketch, an outer circle with the windows
  between spokes as inner shapes (they become holes), extruded 1.5–2 mm on
  the plane the wheel faces (`xz` for a car facing ±x).
- **Brakes:** the disc must clear the caliper inside the barrel: disc radius
  + caliper depth < barrel inner radius.
- Place one wheel, `pattern` along the axle line (`step`), `mirror` across
  `xz` for the other side. Dedupe pattern ids before any boolean.

## Car, plane or boat body

- `loft` along Z with one section per station (nose to tail), then `move`
  rotation [90, 90, 0] to lay it along X. Or `silhouette` from a side and a
  top view: quick and smooth for car shapes.
- Wheel arches: cylinders a few mm bigger than the tyre, `boolean subtract`.
  Then check: tyre bounds must sit inside the arch with clearance on every
  side (`get_scene` bounds of both). No tyre through the bodywork.
- Glasshouse: a separate body cut from the cabin shape, coloured `glass` or
  `smoke` (both draw see-through) and named "Glass" / "Windshield" (clear
  PETG).
- Air ducts and vents: `cut_sketch` the opening on the right plane (a top
  scoop is an `xy` sketch above the panel), plus a cylinder channel
  (`boolean subtract`) to where the air goes.
- An interior through the glass: cut a tub into the body under the cabin,
  then seats, dash and wheel as separate bodies in an "Interior" group.

## Propeller, fan, rotor

`loft` with `naca` sections from root (z 0) to tip, chord and `rot` changing
along the span, then `pattern {axis: "z", count: n, merge: true}` onto a hub
cylinder. Check the tip thickness: at least two nozzle lines.

## Gears and mechanisms

Use the parametric parts (`gear`, `bevel`, `rack`, `ringGear`, `planetary`,
`cycloidal`, `hinge`, `bolt`, `hexNut`): they mesh and fit by construction,
and `set_params` changes them later. A group's bill of materials (in the app)
lists the bearings, pins and screws it needs.

## Too big for the bed

`cut {body_id, axis, at}` splits it (each half prints flat on its cut face).
Join the halves with:

- **Pins:** matching holes in both halves (`add_feature hole`, d = pin + 0.2)
  and a separate pin, or a steel dowel.
- **Bolts:** counterbore one half, heat-set insert the other.
- **Key:** a box added to one half, the same box as a cut in the other, made
  0.2 mm bigger per side.

Put the seam where it is hidden or where the part is thick, not across a thin
or stressed section.
