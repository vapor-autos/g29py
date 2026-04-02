# WiiBrew Wheel Dump

Source: https://wiibrew.org/wiki/Logitech_USB_steering_wheel

Minimal local dump of the parts we care about when checking packet reads and write effects.

## Write Command Layout

- Byte 1:
  - upper nibble = effect slot selection
  - lower nibble = command/action
- Slot selection:
  - `0x1_` = slot 1
  - `0x2_` = slot 2
  - `0x3_` = slots 1 + 2
  - `0x4_` = slot 3
  - `0x5_` = slots 3 + 1
  - `0x6_` = slots 3 + 2
  - `0x7_` = slots 3 + 2 + 1
  - `0x8_` = slot 4
  - `0x9_` = slots 4 + 1
  - `0xA_` = slots 4 + 2
  - `0xB_` = slots 4 + 2 + 1
  - `0xC_` = slots 4 + 3
  - `0xD_` = slots 4 + 3 + 1
  - `0xE_` = slots 4 + 3 + 2
  - `0xF_` = slots 4 + 3 + 2 + 1
- Command/action nibble:
  - `0x_0` = turn off effect
  - `0x_1` = set effect
  - `0x_2` = maximum force to the right
  - `0x_4` = change mystery byte to `0x03`
  - `0x_5` = change mystery byte to `0x02`
  - `0x_C` = set effect
  - `0x_E` = set simple autocenter

## Write Effects

- Constant force
  - Byte 2 = `0x_0`
  - Byte 3 = force clockwise and anti-clockwise (`0x00..0xFF`)
  - Byte 4..7 = `0x00`

- Auto/anti-center complex
  - Byte 2 = `0x_1`
  - Byte 3 = clockwise angle
  - Byte 4 = anti-clockwise angle
  - Byte 5 = L/R proportion force, upper nibble clockwise + lower nibble anti-clockwise
  - Byte 6 = reverse direction, upper nibble clockwise + lower nibble anti-clockwise
  - Byte 7 = force

- Friction force
  - Byte 2 = `0x_2`
  - Byte 3 = clockwise force
  - Byte 4 = clockwise resist/assist
  - Byte 5 = anti-clockwise force
  - Byte 6 = anti-clockwise resist/assist
  - Byte 7 = `0x00`

- Auto/anti-center complex
  - Byte 2 = `0x_3`
  - Byte 3 = clockwise angle
  - Byte 4 = anti-clockwise angle
  - Byte 5 = L/R proportion force, upper nibble clockwise + lower nibble anti-clockwise
  - Byte 6 = reverse direction, upper nibble clockwise + lower nibble anti-clockwise
  - Byte 7 = force

- De-associate
  - Byte 2 = `0x_F`
  - Byte 3..7 = anything, usually `0x00`

- Simple autocenter
  - not written to a normal slot
  - Byte 2 = `0x_D`
  - Byte 3 = anti-clockwise proportion (`0x00..0x07`)
  - Byte 4 = clockwise proportion (`0x00..0x07`)
  - Byte 5 = force (`0x00..0xFF`)
  - Byte 6..7 = `0x00`

## On-Air Write Packet Layout

- Bytes 1..2 = negotiated sub-channel address
- Byte 3 = packet ack
- Byte 4 = mystery byte
- Bytes 5..10 = effect slot 1
- Bytes 11..16 = effect slot 2
- Bytes 17..22 = effect slot 3
- Bytes 23..28 = effect slot 4
- Bytes 29..30 = autocenter
- Byte 31 = hopping RF channel delta

## Read Packet Layout

- Byte 0 = `0x40` data flag
- Byte 1 = `0x00`
- Byte 2 = lower bit of position?
- Byte 3 = button bit field
- Byte 4 = button bit field
- Byte 5 = wheel position
- Byte 6 = accelerator paddle
- Byte 7 = brake paddle

## Notes

- This source is useful for force-feedback structure and for the possibility that button bytes are bit fields.
- It is not a guaranteed exact match for every G29-specific behavior.
