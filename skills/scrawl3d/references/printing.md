# Design for printing (FDM)

`check_printability` measures each part as it will lie on the plate and
returns its size, `fits_bed`, `overhang_mm2`, `thinnest_wall`, thin and
too-thin face counts, `issues`, and `ways_to_lay` (six orientations, least
support first). Fix what it reports, then check again.

## Orientation

- Take the first entry of `ways_to_lay` unless the part has a reason to lie
  otherwise, and set it: `update_part {id, print_rotation: [x, y, z]}`. It
  changes only the export, never the part's place in the assembly.
- Strength runs along the layers, not across them. A hook, clip or bracket
  arm loaded in bending should have its layers along the arm: lie it flat,
  even at the cost of some support.
- The face on the bed comes out flat and true: put the face that must mate
  with something there.

## Overhangs (past 45° from vertical)

- Chamfer the underside of a ledge at 45° instead of a flat shelf.
- Horizontal holes: a teardrop or a flat top (the slicer bridges the top).
- Short flat spans (< ~10 mm at 0.6 mm nozzle) bridge without support; long
  ones sag.
- Split the part so each piece prints without support (`cut`, then pins).

## Walls and small features

| Nozzle | One line (won't print under) | Two lines (minimum sound wall) |
| --- | --- | --- |
| 0.4 | 0.42 | 0.84 |
| 0.6 | 0.63 | 1.26 |

- Load-bearing walls: 3–4 lines. Screw bosses: outer diameter ≥ 2× the screw.
- Pins and posts under 3 mm diameter break: use steel or make them thicker.
- Text and engraving: ≥ 0.4 mm deep, strokes ≥ two lines wide.

## Fits (the app's printer profile holds the measured values)

- Holes print small: features from `add_feature` already add the printer's
  hole compensation.
- Slide or turn fit: 0.3 mm gap per side. Press fit: 0.1 mm interference.
- Print-in-place parts (hinges, captive gears) need ≥ 0.3 mm clearance and a
  first layer that doesn't fuse them: check the gap at the bed.

## Materials

| Material | For | Notes |
| --- | --- | --- |
| PLA | Most parts | Softens ~55 °C: not in a car in summer |
| PETG | Tougher, outdoor-ish | ~75 °C; sticks hard to PEI, use glue as release |
| PETG clear | Glass, lenses, light covers | Thin walls for clarity |
| ASA | Heat, sun | ~95 °C; needs an enclosure |
| PC-CF | Stiff, hot | ~110 °C; hardened nozzle |
| TPU 95A | Tyres, seals, grips, feet | Slow; avoid long retractions; no fine overhangs |

Flexible parts must be separate bodies from rigid ones. A TPU tyre on a rigid
rim: model the tyre's bore 0.2–0.4 mm under the rim's diameter, so it grips.
Parts of different materials print as separate jobs on a single-extruder
printer: export by material.
