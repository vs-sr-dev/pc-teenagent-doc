# pc-teenagent-doc

A measured description of one directory: 433 files, 93,184,691 bytes, as
GOG Galaxy wrote them to disk on 2026-09-11, holding **TEENAGENT**
(Metropolis Software House, MS-DOS, `(c) 1994-1995`; published by Union
Logic Software Publishing Inc. of Nepean, Ontario — all of it read out of
the object's own bytes, none of it from outside) inside DOSBox Staging and
GOG's storefront. The game is fifteen of the files and 16.5 % of the bytes.
The object is not published. What is published is what could be counted,
unpacked, decoded, rendered and checked — and this time the packer had
erased its own name and the words were behind it.

## The short card

| | |
| --- | --- |
| **what it is** | a mouse-driven point-and-click adventure: Mark, a rookie, after disappearing gold, through 42 painted rooms — delivered inside a GOG Galaxy install of which it is 16.5 %, with **the 16.4 % that is its twelve `.RES` containers opened this session to the last of 1,053 members** |
| **studio** | Metropolis Software House — `production / METROPOLIS SOFTWARE HOUSE` in the unpacked engine's credit roll; `(c) Metropolis 1994` in the unpacked `SOUNDSET.EXE`; painted in `VARIA.RES`; typed on the registered-version exit screen; address *ul. M.C. Skłodowskiej 92, 59-300 Lubin* on advert page 10. Programming and script Adrian Chmielarz, animation Grzegorz Miechowski, backgrounds Andrzej Dobrzyński, music Radek Szamrej |
| **year** | 1994–1995 — `(c) 1994-1995` printed by the program; *Coming spring 1995!* painted on advert page 11; 1994 on the eight sound drivers and the sound setup |
| **publisher** | Union Logic Software Publishing Inc., Nepean, Ontario, Canada — on two text-mode order screens, eleven advert pages and a logo screen; the registered-version screen says *copyrighted by Union Logic Software Publishing, Inc. & Metropolis Software House* |
| **platform** | IBM PC, VGA 320 × 200 × 256, mouse; eight sound drivers (GUS, AdLib, SB, SB Pro, PC Speaker, none, SB DMA, Covox); delivered through DOSBox Staging 0.82.2 |
| **files** | 433 in 34 directories; the game 15 (12 `.RES`, 2 `.EXE`, `SOUND.SET`); DOSBox 393; GOG 25 |
| **bytes** | 93,184,691 — game 15,392,150 (16.5179 %), DOSBox 36,580,902 (39.2563 %), GOG 41,211,639 (44.2258 %, of which one 38 MB "Game Configurator" undeclared in GOG's manifest) |
| **distinct sha1** | 416 |
| **the clocks** | six, none the game's: 1994 (drivers), 2017/2019 (GOG icons), 2025-06-17 (DOSBox source), 2025-11-06 (the packager's two shipped logs), 2025-11-19 (GOG's build), 2026-09-11 (the install); the game's own is the printed 1994–1995 |
| **coverage** | specified 80.6898 %, derived 16.4292 % (the twelve `.RES`), opaque 2.8811 %, residue 0 |
| **the program** | `TEENAGNT.EXE` 78,426 B, LZEXE 0.91 with the `LZ91` marker replaced by `0C 0A 09 01` and `*FAB*` still in the stub; unpacked by `lzexe.py` from the stub's disassembly to 152,434 B, 39 relocations, closing; `SOUNDSET.EXE` the same |
| **the words** | 656 messages, 1,217 lines, 4,338 words in the unpacked data segment — none in any `.RES` |
| **the containers** | 12 directories closing on their lengths; 1,053 members: 54 screens (42 rooms, 11 advert pages, a logo), 586 animations, 124 sprites, 31 overlays (Mark, 92 items), 88 empty slots, 2 fonts with the Polish alphabet on the punctuation slots, 2 exit screens, 11 song headers, 144 signed 8-bit samples, 8 drivers |
| **crossings** | 4 of 416 hashes over 114 repositories — all four GOG's installer furniture; no game file, no DOSBox file |
| **tools** | 592 Python files: 589 inherited (4 changed), 3 written |

**The work this time was two readers and the words between them.** The
program's entry stub was disassembled whole — 330 bytes, 168 instructions,
every byte decoded — and `lzexe.py` was written from that listing: a
16-bit bit buffer, three match shapes, a delta-coded relocation list, an
entry taken from the stub's first eight bytes. Out came a data segment
with every line the game says, from *Life is brutal.* to *I hope all this
fish stuff is not a red herring.*, and a credit roll that closed the two
cells the pre-briefing had left open. Then the twelve containers: their
directory is twenty lines, and the engine's loader reads it the same way;
their members are five grammars read out of the engine's blitter, its
animation stepper and one sound driver — screens with a trailing 6-bit
palette, sprites at screen offsets with FFh transparent, per-room
overlays, animations as step lists over frame tables, glyphs of 0/1/2 —
each closing on every member it claims. Out came the game: a farm, a lake,
a mansion with a library and a vault, a *MEGABANK*, a hen that walks and
flaps in 40 frames, Mark in a red shirt, 92 things to pick up, and a font
that still spells *Dobrzyński* the Polish way.

**The pre-briefing was wrong six times**, each caught by a byte:
`SOUNDSET.EXE` is packed too; *Metropolis* is in four game files; the
header offset it quoted was one row up; the advert pages are not the
title; the year is printed after all; and one of the session's own
sentences claimed a confirmation the owner had not yet given (it came
after, on all 54 renders). Its five
hunches score four true in the main and one half, with the samples signed
where it said unsigned.

## The chapters

Seven, and the count is the content's. One for the program, because the
packer is the gate to the words; one for the words, because they are the
game; one for the twelve containers, because they are the 16.4 %; one for
the shop and the emulator together, because they are 83.5 % of the bytes
and none of the game; and no chapter for the engine, which was
disassembled exactly as far as the formats needed.

| chapter | the sentence |
|---|---|
| [01 — What this is](docs/01-what-this-is.md) | a 15 MB adventure inside a 93 MB shop: the object, the split, the coverage, the denominators |
| [02 — The technical sheet](docs/02-the-technical-sheet.md) | every figure with the command that re-derives it |
| [03 — The program](docs/03-the-packer-that-erased-its-name.md) | a packer that erased its name, read from its own stub and removed; `dospack.py` repaired |
| [04 — The words](docs/04-the-words.md) | 4,338 of them in the data segment; the credits, the studio, the year, the Polish font map |
| [05 — Twelve containers](docs/05-twelve-containers.md) | 1,053 members, every one named by a grammar that closes: rooms, adverts, sprites, animations, Mark, items, fonts, exit screens, music heads, samples, drivers |
| [06 — The shop and the emulator](docs/06-the-shop-and-the-emulator.md) | 83.5 % of the bytes, 0 % of the game; the six clocks; the CD image that was there and is not here |
| [07 — Corrections, predictions and calibration](docs/07-corrections-predictions-and-calibration.md) | six corrections, five hunches scored, one term, rule 0 as a program |

## The rules this was written under

The object is not run, not installed, not emulated — a DOSBox is in it and
was not launched. Unpacking LZEXE by reading its stub and decoding the
containers are reading bytes as data. **The famous free implementation of
this game's engine was not opened, read, quoted or consulted to check a
result**; what the pre-briefing recalled of it was tested against the bytes
and nothing more. Every figure names its denominator and the command that
re-derives it; every reader refuses a directory, prints a non-Latin-1 name
safely, selects by magic, and passes its selftest in a repository that
does not hold the object or says what it skipped. The documents are in
English; the sessions were in Italian.
