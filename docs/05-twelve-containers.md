# 05 — Twelve containers: 1,053 members, every one named by a grammar that closes

*Measure: `python tools/res.py --census Teenagent` (notes/res-census.txt); `python tools/res.py FILE --list` for each (notes/res-list.txt); `python tools/res.py Teenagent/OFF.RES Teenagent/ADVERT.RES Teenagent/UNLOGIC.RES --render _work/screens` (notes/res-render.txt); `python tools/res.py --room 20 --out _work/room20.png` (notes/res-rooms.txt); `python tools/dosdis.py _work/TEENAGNT.unp.exe --at $((192+0x2D8B)) --length 0xFA --org 0x2D8B --targets` (notes/dosdis-engine-stepper.txt).*

## The container, and the engine reading it

Every `.RES` is `u32 count` followed by `count + 1` little-endian offsets,
the first equal to 4 + 4 (count + 1), the last equal to the file's length,
monotonic; member *i* is the bytes between offset *i* and offset *i + 1*.
Twelve files, twelve closures with residue 0, 1,053 members. No names, no
types, no signatures anywhere in the directory.

The engine reads it exactly so. Its loader at code 0B0D4h (`dx` = file
name, `cx` = member number, 1-based) does `open` (3D00h), `lseek` to
4 · cx (4200h), `read` 8 bytes (3Fh) — two consecutive offsets — takes the
low words' difference as the size, `lseek`s to the first, `read`s into
the caller's segment, `close`s (3Eh). Member *cx* of the engine is member
*cx − 1* of `res.py`. The loader is copied whole into the SoundBlaster
drivers, which open `sam_sam.res` for themselves.

| file | bytes | members | what they are, by the grammar below |
|---|---:|---:|---|
| `ADVERT.RES` | 712,500 | 11 | 11 screens: the shareware advertisement, pages 1–11 |
| `OFF.RES` | 2,720,432 | 42 | 42 screens: the rooms' backgrounds |
| `ON.RES` | 153,907 | 42 | 28 overlays + 14 empty: one per room, the static objects over it |
| `ONS.RES` | 173,077 | 113 | 113 sprites at fixed screen positions |
| `LAN_000.RES` | 535,599 | 168 | 94 animations + 74 empty: 42 rooms × 4 slots |
| `LAN_500.RES` | 9,538,457 | 492 | 492 animations, ids 500 and up (`sub cx,1F3h` in the loader at 0ABA9h) |
| `UNLOGIC.RES` | 202,880 | 11 | 1 screen (the Union Logic logo) + 10 sprites (its globe, 138 × 100 at (73,54)) |
| `VARIA.RES` | 216,683 | 11 | Mark's frames (2 overlays, 42 + 9), the inventory panel (a 286 × 141 sprite at (17,12)), 92 items (an overlay with 6 nested sequences), a palette, the TEENAGENT logo (320 × 68 raw), 2 fonts, the METROPOLIS strip (320-wide raw), 2 text-mode screens |
| `MMM.RES` | 42,104 | 11 | 11 songs: a header read, a body not |
| `SAM_MMM.RES` | 229,636 | 51 | 51 music samples, signed 8-bit PCM |
| `SAM_SAM.RES` | 769,552 | 93 | 93 effect samples, the same |
| `SDR.RES` | 14,665 | 8 | 8 sound drivers, 8086 code |
| | **15,309,492** | **1,053** | 54 screens, 586 animations, 124 sprites, 31 overlays, 88 empty, 11 song heads, 8 drivers, 2 fonts, 2 text screens, 1 palette, 146 read by their players |

## Screens: the palette is in the tail and is 6-bit

Fifty-four members are exactly 64,768 = 320 × 200 + 768 bytes. In every one
the last 768 bytes are all ≤ 63 and the first 768 are not (up to 207 in
`OFF`, 223 in `ADVERT`): a trailing 256 × RGB palette of 6-bit VGA values,
scaled `v << 2 | v >> 4` for the PNG. The first render was right: every
index of every screen is inside the 256 its palette defines, the 42-room
sheet was put in front of the owner during the session, and the room
compositions below land their sprites where the engine's own step list
says — the checks a render can have without running the game.

**`OFF.RES` is the game's 42 rooms**, each using 186–227 of its 256
indices: a farm from above (lake, red-roofed cottages, a haystack, beehives,
a blue car), a camouflage tent inside a wire fence, the fence's gate, a
brick wall, a *Cantina*, a bare room with a bunk, an office with a map and
rifles on the wall, a bar, a storeroom of barrels and crates, a red-and-
white sentry box, a forest, a hollow stump with a door, the lake with an
island, a rowing boat and a well, the lake bed with a wreck, a cottage, a
dining room, another cottage front, a hall, a pink sitting room with a
grandfather clock, a cellar with a ladder, cliffs, a cave, a field of
haystacks and a scarecrow, a corridor of pipes, a staircase, a library, a
hall with a statue, a study, a kitchen, a bathroom with a sailboat on the
tiles, a television room, a machine room with a propeller, a laboratory,
a vault with a `$` safe, a street of *SHOP* and *CAFE*, a *MEGABANK*
front, and a corridor of safes.

**`ADVERT.RES` is not the game: it is the shareware advertisement**, pages
1 to 11 numbered on each screen (53–234 colours: text pages and three
painted scenes). Page 1: *Can You Solve The Mystery Of The Disappearing
Gold? ... Only $29.95 US ... 14 megs of TEENAGENT with dozens of beautiful
hand-painted backgrounds! Over 20 000 frames of animation, equivalent to
40 minutes of cartoons! An ultra cool manual and a free bonus game!
Multi-channel soundtrack and over 100 sound effects! To place an order
(800) 583-4838*. Pages 2–3: ways to order, `ftp.unlogic.com /pub/unionlogic`,
a BBS. Pages 4–6: Mark at a dead tree, at a cliff, under water. Pages
7–10: distributors — Belgium, Argentina, Chile, Czech Republic, Germany,
Denmark, Italy (*Systems Comunicazioni srl, Gaggiano*), Japan, the
Netherlands, South Africa, Norway, Spain, and **Poland: Metropolis Software
House, ul. M.C. Skłodowskiej 92, 59-300 Lubin**. Page 11: *Other Projects
Coming Soon! Radix: Into The Void ... Coming spring 1995! Tactical Factor
... Coming spring 1995!* — the year painted.

`UNLOGIC.RES` member 0 is the publisher's logo screen, a blue pyramid and a
globe over *UnionLogic Software Publishing, Inc.*; members 1–10 are the
globe alone, ten frames of it turning.

## Sprites, overlays, animations: three grammars, one blitter

**Sprite** — `u16 w, u16 h, u16 offset, w × h pixels`, the offset a screen
address (y × 320 + x), FFh transparent. The engine's blitter at code 1B10h
is the whole warrant: `cx = [bx]; dx = [bx+2]; si = [bx+4]; bx += 6`, then
per row `mov al,es:[bx]; cmp al,0FFh; jz skip; mov [si],al` and `add
si,140h; sub si,cx` for the 320-byte stride. 113 of 113 `ONS` members, the
ten `UNLOGIC` frames and the inventory panel close on the arithmetic.

**Overlay** — `u8 n, u16 off[n]` from the member's start (so `off[0]` =
1 + 2n: 3, 5, 9 ...), then n sprites tiling the member. `ON.RES` has one
per room: 28 rooms carry 1–4 objects, 14 carry the single byte `00`.
`VARIA.RES` members 0 and 1 are overlays whose sprites are all 61–62
pixels high at offset 0 — **Mark** himself, red shirt, blue jeans: 42
frames walking left, right, towards and away (the last four 25 × 8, a
detail) and 9 more. Member 3 is the **92 inventory items**: spanner,
toolbox, car jack, hen, feather, shovel, rope, apple, sunglasses, banana,
bow, nut, potatoes, mug, key ... each drawn at (3–9, 2–11) inside a cell;
six of the 92 entries are not a sprite but a **sequence** — `u8 k, u16
off[k]` with repeats over 3–6 sprites (16, 40, 21, 22, 4 and 32 steps): the
items that move.

**Animation** — the stepper at code 2D8Bh reads it, and `res.py` reads it
the way the stepper does:

    u16 L                         length of the step list (= 2 + 3 n)
    n x (u8 frame, u16 offset)    frame number (1-based) and screen position
    at L: u8 frames, u16 off[frames]   1-based, relative to L
    each frame: u16 w, u16 h, w x h pixels, FFh transparent

(`bx = 3·step − 1; cmp bx,[0]; cl = [bx]; si = [bx+1]; bx = [0] − 1 + 2·cl;
bx = [bx] + [0]; w = [bx]; h = [bx+2]; pixels at bx + 4` — every line of
that is in the listing.) The closure is that the frames tile the member
from the table to its end and every step names an existing frame at an
on-screen position: **660 of 660** (`LAN_000` 94 + 74 empty, `LAN_500`
492), with one member — `LAN_500` 11 — carrying a single trailing byte
(1Ah) after its last frame that the engine never reads. The smallest
member is 13 bytes: L = 5, one step placing frame 1 at (160,100), one
frame of 1 × 1 transparent pixel.

`LAN_000` is 168 = 42 rooms × 4 slots: the loader at 0AC02h computes
`cx = (room − 1) · 4 + slot`, and the code before it substitutes members
of `LAN_500` for some slots when a game flag at ds:0DB3Ch.. is set (the
door opened, the character gone). `LAN_500` member 1 is a hen: 60 steps
over 40 frames, walking right to left along y = 171–178, pecking,
flapping. Member 0 is 22 frames 62 pixels high — Mark's size. Room 20
composed (`--room 20`) puts a 26 × 46 figure in blue on the pavement at
the cottage door, where its step says.

## Fonts and the two order screens

`VARIA.RES` members 6 and 7: `u16 off[n]`, n = off[0] / 2, each glyph
`u8 h, u8 w, h × w` bytes of 0, 1, 2; 97 and 95 glyphs from 20h, tiling
7,072 and 8,852 bytes exactly. The small one carries the Polish letters on
the punctuation slots ([04](04-the-words.md)); the large one, 15 pixels
wide, has letters only.

Members 9 and 10 are 3,680 = 80 × 23 × 2 bytes of character / attribute
pairs: the DOS screens shown on exit. **Member 9: `■ Registered Version
(DO NOT DISTRIBUTE!) ■` — *TEENAGENT is copyrighted by Union Logic
Software Publishing, Inc. & Metropolis Software House. It is illegal to
distribute this registered version of TEENAGENT.*** Member 10: `■
Shareware Version (Distribute freely!) ■` with the order pitch. Both
carry the Nepean address and the three telephone numbers. This is the
registered release, and it ships the shareware screen beside its own.

Member 5 is the **TEENAGENT** title logo, 320 × 68 raw; member 8 the
*METROPOLIS software house* strip, 320 wide, seven colours; member 4 a
768-byte palette; member 2 the wavy inventory panel.

## Music and samples: what the drivers say

`SDR.RES` holds eight drivers — Gravis UltraSound v1.04 (2,264 B), AdLib
v1.03 (743), SoundBlaster v1.25 (4,759), SoundBlaster Pro v1.26 (4,766),
PC Speaker v1.03 (718), *No sound driver v1.00* (51), SoundBlaster DMA
v1.02 (883), Covox v1.02 (441) — each `(c) Adrian M.Chmielarz 1994`, each a
code blob dispatching on `ah` (`cmp ah,3; cmp ah,1; cmp ah,2 ...`).
`SOUND.SET`'s five bytes `04 20 02 07 01` are read whole into ds:3242h and
the first is the driver's member number: **4 = SoundBlaster Pro**, at port
220h, IRQ 7, DMA 1.

The SB DMA driver (member 6, 883 bytes, 100 % decoded after its two error
strings) declares the sample format. Its function 5 loads a member of
`sam_sam.res` with a copy of the engine's container reader and then runs
`xor [bx],8080h` over the whole buffer before handing it to the DSP: **the
samples on disk are signed 8-bit PCM**, and the Sound Blaster wants them
unsigned. Its rate routine divides 256,000,000 (`0F42h:4000h`) by
2 × **2B11h = 11,025** and sends `40h` then 256 − low byte = 167 as the
time constant: 11,025 Hz is the constant the driver was written with, and
1,000,000 / (256 − 167) = 11,236 Hz is what the DSP plays. The transfer is
single-cycle DMA (`48h` + channel, DSP command `14h`, length − 1). The PC
Speaker driver carries a byte table ramping from `@` down to `!` in runs
of ten — a level map for the same samples, not read further.

`MMM.RES`: every member begins `MMM 06`, then `u8 n` and **n sample numbers
in BCD** (`10 11 12 13`; `48 21 35 49 50 51`) — 3 to 7 per song, 51
distinct across the eleven, 1..51 with none missing: exactly the 51
members of `SAM_MMM.RES`. Then three tagged values `Q`, `R`, `S`, each a
BCD sample number from the song's own list, then the sequence (`00 2B 24
00 ...`, `24 20 30 00 ...`) — **not decoded**. What the music is, then: a
sample-based format of the drivers' own, eleven songs over 51 samples,
with the SoundBlaster drivers (the two 4.7 KB ones, which name `mmm.res`
and `sam_mmm.res`) as its players. Not MIDI, not any public format the
box knows.

## What the container is not

The owner's "SCUMM-like" is the interface. The bytes share nothing with the
two SCUMM-branch neighbours beyond being a table of offsets: no chunk
tags, no XOR, no index in the executable, no room files — twelve flat
containers and a program that names them in a list. Nothing of theirs was
opened to say so; their `docs\` say what their containers are, and this
one is not that.

## What was not read

The song bodies. The room scripts that choose which animation runs and
which message shows. The three `Q/R/S` roles. The flag-driven
substitution rules at 0AC5Ch beyond the fact that they exist. `VARIA` member 4's use.
The `GUS`, `AdLib`, `SB`, `SB Pro`, `Covox` and `PC Speaker` drivers
beyond their strings and their dispatch — one driver was enough to say
what a sample is, and the others were left as bytes.
