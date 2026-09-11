# 01 — What this is: a 15 MB adventure inside a 93 MB shop

*Measure: `python tools/treecensus.py Teenagent` (notes/treecensus.txt), `python tools/hashall.py Teenagent` (notes/hashall.txt), `python tools/coverage.py tree --root Teenagent` (notes/coverage.txt), `python tools/res.py --census Teenagent` (notes/res-census.txt).*

## The object

**TEENAGENT**, a mouse-driven point-and-click adventure — Mark walks where
you click, the left button looks, the right acts, the inventory drops from
the top of the screen (GOG's `teenagent_manual.txt`, 1,684 bytes, in the
object) — as GOG Galaxy wrote it to disk on 2026-09-11. The live install
was not touched; `Teenagent\` here is a byte-for-byte copy with
modification times preserved, and every figure below was taken on the copy.

    433 files    34 directories    93,184,691 bytes    416 distinct SHA-1

The game is **fifteen files and 15,392,150 bytes = 16.5179 %** of that.
The other 418 files are the emulator GOG runs it in and GOG's own
furniture:

| family | files | bytes | share |
|---|---:|---:|---:|
| the game: 12 `.RES` containers | 12 | 15,309,492 | 16.4292 % |
| the game: `TEENAGNT.EXE`, `SOUNDSET.EXE`, `SOUND.SET` | 3 | 82,658 | 0.0887 % |
| DOSBox Staging 0.82.x with its source ZIP (`DOSBOX\`) | 393 | 36,580,902 | 39.2563 % |
| GOG: Inno uninstaller, `goggame-*`, icons, confs, manual, two shipped logs, a 38 MB "Game Configurator" | 25 | 41,211,639 | 44.2258 % |
| | **433** | **93,184,691** | 100 % |

(`python _work/families.py`, re-counted; `set_config\Game Configurator.exe`
alone is 38,115,928 bytes, 40.9 % of the object, and is not declared in
GOG's own manifest — [06](06-the-shop-and-the-emulator.md).)

## What the game's bytes say about the game

Before this session, nothing readable: twelve containers whose 1,053 members
had no names, a 78 KB program with entropy 7.85 and 411 strings of noise,
and — in the clear — eight sound drivers signed `(c) Adrian M.Chmielarz
1994` and a text-mode order form for **Union Logic Software Publishing
Inc., Nepean, Ontario** with prices in dollars.

After it, the object says who made it, when, and in what language:

* **the program unpacks** — it is LZEXE 0.91 with the `LZ91` marker
  replaced by `0C 0A 09 01`, and so is `SOUNDSET.EXE`; `tools/lzexe.py`,
  written from the stub's disassembly, releases 152,434 bytes whose `MZ`
  header closes on its own size ([03](03-the-packer-that-erased-its-name.md));
* **the words are in it**: 656 messages, 1,217 lines, 4,338 words in the
  data segment, from *Life is brutal.* to *I hope all this fish stuff is
  not a red herring.*, and a credit roll ending **`production /
  METROPOLIS SOFTWARE HOUSE / (c) 1994-1995`** — programming and script
  Adrian Chmielarz, animation Grzegorz Miechowski, backgrounds Andrzej
  Dobrzyński, music Radek Szamrej ([04](04-the-words.md));
* **the twelve containers open**: 42 backgrounds, 42 per-room overlays,
  586 animations in the grammar the engine's own stepper uses, Mark's 51
  walking frames, 92 inventory items, two fonts that put **the Polish
  alphabet on the punctuation slots**, eleven pages of shareware
  advertising, a text-mode *Registered Version (DO NOT DISTRIBUTE!)*
  screen naming *Union Logic Software Publishing, Inc. & Metropolis
  Software House*, eleven song headers naming all 51 music samples in
  BCD, and eight drivers one of which says the samples are signed 8-bit
  PCM at 11,025 Hz ([05](05-twelve-containers.md));
* **the year is painted twice and printed once**: `(c) 1994-1995` in the
  credits, *Coming spring 1995!* on advert page 11, `(c) Metropolis 1994`
  in the sound setup — and 1994 on every driver.

## Coverage, and what the figure means

`coverage.py tree` classifies by magic, not by extension:

| bucket | files | bytes | share |
|---|---:|---:|---:|
| specified (PE/MZ 35, ZIP 2, text 337, icons 4, JPEG 1) | 379 | 75,190,495 | 80.6898 % |
| **derived: the 12 `.RES`, by `res.py`'s closure** | 12 | 15,309,492 | 16.4292 % |
| opaque (FreeDOS `.cpi` x18, `.txt` x13, `.sys` x4, `.com` x2, Inno `.dat` x2, `unins000.msg`, `.lnk`, `SOUND.SET`) | 42 | 2,684,704 | 2.8811 % |
| | 433 | 93,184,691 | residue 0 |

The 80.69 % is the emulator and the shop, specified by other people's
documents, and says nothing about the game. The 16.43 % that moved from
opaque to derived is the game's data, and behind the container's directory
`res.py --census` names every member by a grammar that closes: **1,053 of
1,053** — 54 screens, 586 animations, 124 sprites, 31 overlays, 88 empty
slots, 11 song headers, 8 drivers, 2 fonts, 2 text screens, 1 palette, and
146 members read by the code that plays them rather than by their own
bytes (144 samples, the title logo, the studio strip). Two things stay
undecoded and are said so: the song *bodies* after their headers, and
the engine's room scripts.

## The denominators

    433          files                              93,184,691 bytes
    416          distinct SHA-1                     17 repeats
    15           files that are the game            16.5179 %
    12           .RES containers                    1,053 members
    54           320 x 200 screens                  3,497,472 bytes
    152,434      bytes of unpacked engine image     656 messages, 4,338 words
    4 of 416     hashes crossing 114 repositories   all four GOG's installer

## How the chapters are cut, and why

The content decided seven: one chapter for the object, one for the sheet,
**one for the program** (the packer read and removed, and the repair of the
tool that said "no packer"), **one for the words** (they are behind the
packer, so they follow it), **one for the twelve containers** (the 16.4 %),
one section-sized chapter for the shop, the emulator and the six clocks
that are none of the game's, and one for what the pre-briefing got wrong,
the five hunches scored, and the calibration term. The engine is
disassembled exactly as far as the formats needed — the loader, the
blitter, the animation stepper, the driver chooser, one sound driver — and
there is no chapter on the engine.
