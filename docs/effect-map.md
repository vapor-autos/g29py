# Effect Map

## `force_off`

- payload
  - byte 1 = slot mask / off command
  - bytes 2..7 = `0x00`
- points
  - `0xf3` = stops active force effects

## `force_constant`

- payload
  - byte 1 = `0x11`
  - byte 2 = `0x00`
  - byte 3 = force value
  - bytes 4..7 = `0x00`
- public range
  - `val`: `-1.0..1.0` inclusive, scaled to `0x00..0xff`
- points
  - `-1.0` = `0x00`
  - `0.0` = `0x80`
  - `1.0` = `0xff`

## `set_friction`

- payload
  - byte 1 = `0x21`
  - byte 2 = `0x02`
  - byte 3 = clockwise force
  - byte 4 = `0x00`
  - byte 5 = anti-clockwise force
  - byte 6 = `0x00`
  - byte 7 = `0x00`
- observed working range for bytes 3 and 5
  - `0x00..0x07` inclusive
- points
  - `0x00` = no resistance
  - `0x07` = max resistance
  - `0x08` = unsupported

## `set_range`

- payload
  - byte 1 = `0xf8`
  - byte 2 = `0x81`
  - byte 3 = low byte of range
  - byte 4 = high byte of range
  - bytes 5..7 = `0x00`
- public range
  - `val`: `400..900` inclusive

## `set_autocenter`

- payload
  - byte 1 = `0x14` wake command
  - byte 2 = `0x0d`
  - byte 3 = `ccw_proportion`
  - byte 4 = `cw_proportion`
  - byte 5 = `force`
  - bytes 6..8 = `0x00`
- public ranges
  - `ccw_proportion`: `0.0..1.0` inclusive, scaled to `0x00..0x07`
  - `cw_proportion`: `0.0..1.0` inclusive, scaled to `0x00..0x07`
  - `force`: `0.0..1.0` inclusive, scaled to `0x00..0xff`
- tested force range
  - `0x0c..0x7f` inclusive
- tested proportion points
  - `0x00` = little / directional bias only
  - `0x03` = strong when force is high
  - `0x07` = strong
  - `0x0b` = strong
  - `0x07` = strong in both directions

## `set_anticenter`

- payload
  - byte 1 = slot command
  - byte 2 = `0x01`
  - byte 3 = `cw_position`
  - byte 4 = `ccw_position`
  - byte 5 = `(cw_proportion << 4) | ccw_proportion`
  - byte 6 = `(cw_reverse << 4) | ccw_reverse`
  - byte 7 = `force`
- public ranges
  - `slot`: `1..4`
  - `cw_position`: `0.0..1.0` inclusive, scaled to `0x00..0xff`
  - `ccw_position`: `0.0..1.0` inclusive, scaled to `0x00..0xff`
  - `cw_proportion`: `0.0..1.0` inclusive, scaled to `0x00..0x0f`
  - `ccw_proportion`: `0.0..1.0` inclusive, scaled to `0x00..0x0f`
  - `cw_reverse`: `False` / `True`, scaled to `0x0` / `0x1`
  - `ccw_reverse`: `False` / `True`, scaled to `0x0` / `0x1`
  - `force`: `0.0..1.0` inclusive, scaled to `0x00..0xff`
- points
  - `0x01` is the supported subtype
  - equal-angle sweeps move and hold

## `autocenter_off`

- payload
  - byte 1 = `0xf5`
  - bytes 2..7 = `0x00`
- points
  - stops active simple autocenter
