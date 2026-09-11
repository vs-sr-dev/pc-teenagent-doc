# 04 — The words: 4,338 of them, in the data segment, behind the packer

*Measure: `python tools/teentext.py _work/TEENAGNT.unp.exe --count` and `--polish` (notes/teentext.txt); `python tools/strdump.py _work/TEENAGNT.unp.exe --min 6` (notes/strings-teenagnt-unpacked.txt); `python tools/res.py Teenagent/VARIA.RES --font 6 --out _work/font6.png` (notes/res-font-06.txt).*

## Where they are

The pre-briefing carried a recollection — that the public engine for this
title takes its texts from the executable, not from a `.RES` — and marked
it *to be tested against the bytes, not looked up*. It was tested this way:
the twelve containers were read to the last member ([05](05-twelve-containers.md))
and hold **no game prose at all** — the only words in them are the
publisher's order screens, the drivers' names, and the letters of two
fonts. The program was unpacked ([03](03-the-packer-that-erased-its-name.md))
and its data segment, 0B520h..19C40h in the image, holds every line the
game says. No engine source was opened to confirm either half.

`teentext.py` walks that segment for blocks of printable lines separated by
a single zero byte and closed by a second:

    656 messages    1,217 lines    4,338 words    23,418 characters
    285 messages open with a byte below 20h -- 73 x 00h and 205 x 01h
        followed by a name line, the hotspot and inventory entries
        (`<01>mansion wall / It must be 3 kilometers thick...`,
        `<00>nugget / Pure gold!`, `<01>tons of gold / (gulp)`), and seven
        others (04h, 09h, 0Ah, 15h x2, 17h x2)
      a few open with a short run of printable bytes the display code
        reads (`3&4I have no idea what to do with it.`); they are counted
        as text
      1 is not the game's: the DOS error table, 0E53Fh, `$`-terminated
        (`File not found`, `Too many open files`...), with the two
        anti-piracy lines at its end

The lines are cut where the font would wrap them, at 30–40 characters,
which is why a message is one to four lines. The first message in the
segment is the list of files the engine opens, at ds:0013h: `sound.set`,
`off.res`, `on.res`, `lan_500.res`, `lan_000.res`, `sdr.res`, `ons.res`,
`varia.res`, `mmm.res`, `sam_sam.res`, `sam_mmm.res`, `unlogic.res`,
`advert.res`, `teenage0.sav` — the twelve containers, the sound setting,
and one save slot.

## What they say

Mark is a rookie (*Sir, I'm Mark. A rookie.*) sent after gold (*Can You
Solve The Mystery Of The Disappearing Gold?* is the advert's headline;
*tons of gold / (gulp)* and *nugget / Pure gold!* are hotspots) into a
mansion (*Meanwhile in the mansion...*, *mansion wall / It must be 3
kilometers thick...*) past a captain (*I think it's time to call
captain...*), a guard, crows, bees, a mouse, a hen (*I wonder if hens can
fly. Come here,*), a boat and a lake he dives in (*I really can't talk
underwater!...*, *I was really hooked on this anchor!*). The voice is one
teenager's, and the puns are declared: the credits end *All allusions and
puns / are intentional*. A sample, in the order the segment keeps them:

    Life is brutal.                        Life is really brutal.
    One small step for man, / one big pain in the ...head...
    I hope all this fish stuff is not a red herring.
    People leave food in unbelievable places.
    Hundred moments later...               Another hundred moments later...
    I really don't know how to talk to / girls...
    It's not DOOM. It's a harmless graphic adventure
    Smells like Teen Spirit.
    'Saving is a very fine thing. Especially / when your parents have done it for you'
    'Soccer rulz'                          The rest of graffiti is obscene.
    I'm not a thief. And it's empty, by the way.
    Nice design. Especially that 'LOVE CANDY' label.
    It makes me feel like another / wanna-be cliffhanger.

And two lines that are not Mark's, at the end of the DOS error table:
*Due to anti-virus blockade you have to install this game from original
disks.* and *Call yourself pirate, hacker, elite or whatever. But you are a
THIEF.* — the copy protection's script, whose trigger was not read.

## The credits, and the two open cells

At 19937h the segment holds the credit roll, 39 lines, and the cells the
pre-briefing left open close on it:

    programming             ADRIAN CHMIELARZ
    animation               GRZEGORZ MIECHOWSKI
    additional animations   TOMASZ PILIK
    backgrounds             ANDRZEJ DOBRZYŃSKI
    music                   RADEK SZAMREJ
    cover art               DARIUSZ ANACKI
    translation help        PETER WELLS
    betatesters             TOMASZ FURMANIUK, PATRYK SAWICKI, PAWEL MIECHOWSKI,
                            MAREK CHMIELARZ, JEDREK WICHA, MR. JOHN DOE, MARCIN DREWS
    ideas                   ADRIAN CHMIELARZ, GRZEGORZ MIECHOWSKI, ANDRZEJ SAWICKI
    print                   JAROSŁAW WEISS, AGENCJA STYL
    thanks                  HENRY KUTTNER, U-KNOW-WHO-U-R-BUT-WANT-2-STAY-IN-SHADOW,
                            EPIC MEGAGAMES, XLAND SOFTWARE PUBLISHING, KATARZYNA MIECHOWSKA
    special thanks          ANDRZEJ MICHALAK
    production              METROPOLIS SOFTWARE HOUSE
                            (c) 1994-1995
                            All allusions and puns / are intentional

A shorter roll precedes it (`Pbackgrounds / iANDRZEJ DOBRZY;SKI`, four
pairs, each line opening with a letter the display code reads and each
pair with a two-byte head), then `\after the tiring journey...` and `\THE
END`.

* **Studio: Metropolis Software House.** In the bytes four times over —
  here; in `SOUNDSET.EXE` unpacked (`Sound Source Setup v1.00 (c)
  Metropolis 1994`); painted in `VARIA.RES` member 8 (a 320-pixel-wide
  strip reading *METROPOLIS software house*); and in the text-mode
  *Registered Version* screen of `VARIA.RES` member 9 (*TEENAGENT is
  copyrighted by Union Logic Software Publishing, Inc. & Metropolis
  Software House*). Advert page 10 gives its address under *Poland*:
  *ul. M.C. Skłodowskiej 92, 59-300 Lubin*. The pre-briefing's "the word
  Metropolis is in no game file" was wrong three ways at once: behind the
  packer, behind character/attribute interleaving, and in a picture.
* **Year: 1994–1995**, as the program prints it; *Coming spring 1995!*
  twice on advert page 11 (for two other products); *(c) Metropolis 1994*
  in the sound setup; 1994 on the eight drivers. Nothing outside the object
  was used for either cell.
* **Publisher: Union Logic Software Publishing Inc.**, Nepean, Ontario —
  on the order screens, the eleven advert pages and the logo screen.
* **Programming and script: Adrian Chmielarz** — the same name that signs
  the eight sound drivers as `Adrian M.Chmielarz`.

## The font map, or why `DOBRZY;SKI`

The credit roll spells `DOBRZY;SKI` and `JAROS]AW`. `VARIA.RES` member 6
is the game's small font — 97 glyphs from 20h, `u8 height, u8 width,
height × width` bytes of 0 / 1 / 2 (transparent, ink, shadow), 7,072
bytes that tile the member exactly — and rendered (`--font 6 --out`) it
puts the Polish alphabet on the punctuation slots:

    23h # -> ę    24h $ -> ś    25h % -> ł    2Ah * -> ó    2Bh + -> Ą
    3Bh ; -> Ń    3Ch < -> ż    3Dh = -> ń    3Eh > -> ź    40h @ -> ą
    5Bh [ -> Ę    5Ch \ -> Ć    5Dh ] -> Ł    7Bh { -> Ó    7Ch | -> Ś    7Dh } -> Ż

So the roll reads *Andrzej Dobrzyński* and *Jarosław Weiss*, and the font
says what no string does: the studio wrote in Polish and shipped an English
game whose font still carries its own alphabet. `teentext.py --polish`
applies the map, read off the render glyph by glyph — it is not a code
page. Member 7 is the large font of the credits (95 glyphs, 15 pixels wide,
letters only; the digits are 1 × 1 placeholders).

## What was not read

Which message a hotspot shows, and when: the room scripts that pick them
are in the code segment and were not disassembled. The two-byte heads of
the credit pairs and the letters `P`, `i`, `\` that open their lines are
codes for the display routine, meaning not read. Whether a dialogue tree
exists beyond the linear order in the segment is not measured.
