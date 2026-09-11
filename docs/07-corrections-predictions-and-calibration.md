# 07 — Corrections, predictions and calibration: what the pre-briefing got wrong, five hunches scored, one term

*Measure: `python tools/rule0hook.py --report` (notes/rule0-report.txt, notes/rule0.log masked); `python _work/calib3.py --append 9.00`; `python tools/toolsdiff.py ../pc-demonsforge-doc/tools` (notes/toolsdiff.txt); `notes/selftests.txt`, run with `PYTHONIOENCODING` unset.*

## What the pre-briefing got wrong, and how each was caught

The pre-briefing's own rule was *treat every clean story as a hypothesis*.
Six of its statements fell to the bytes:

1. **"`SOUNDSET.EXE` is not packed (its strings are readable)."** It is
   LZEXE 0.91 with the same replaced marker as the engine; readable strings
   are what a 4 KB LZ stream looks like when 2,055 of its symbols are
   literals. Caught by `lzexe.py`'s selftest, which was written expecting
   it to be the negative control and found it was a second positive.
2. **"The word Metropolis is in no game file."** It is in four: the credit
   roll behind the packer, `SOUNDSET.EXE` behind the packer, `VARIA.RES`
   member 8 as pixels, `VARIA.RES` member 9 as every other byte of a
   text-mode screen. `strdump.py` sees none of those, and the pre-briefing
   trusted it. Caught by unpacking, rendering and de-interleaving.
3. **"Header offset 1Ch reads `1C 00 00 00`."** It reads `0C 0A 09 01`;
   `1C 00 00 00` is `e_lfarlc` and `e_ovno` at 18h. Caught by `xxd -l 32`.
   The conclusion (no `LZ91`) stood.
4. **"1994 is the only year the game's own bytes print."** The program
   prints `(c) 1994-1995` and the advert paints `1995`; the pre-briefing
   could not see either and said it could not.
5. **"`ADVERT.RES`'s eleven are the title, credits and order screens."**
   They are eleven advertisement pages; the title is a 320 × 68 logo in
   `VARIA.RES` and the credits are text in the program.
6. **`SOUND.SET`'s first byte "driver #4 ... SoundBlaster Pro?"** — the
   guess was right and marked as a guess; the engine reads the byte as a
   1-based member of `SDR.RES`, and member 4 is the SoundBlaster Pro
   driver. Now measured.

And one of the session's own, caught in the session: the first draft of
chapter 05 said the owner had *confirmed* the 42-room sheet coherent when
the owner had only been shown it. The sentence was rewritten as a
measurement; the owner then looked at the 54 renders and confirmed them
all, and the sentence now says both things in that order.

## The five hunches of §P.7, scored

**a.** *LZEXE 0.91 with the marker stripped and nothing else changed;
`lzexe.py` from the stub unpacks it to a closing `MZ`; the texts, a credit
and a year are in the clear.* — **True on every clause.** The 204-byte
decoder is byte-identical to the one in `SOUNDSET.EXE`, the image closes
(152,434 B, 39 relocations all inside), and the data segment holds 656
messages, the credits and `(c) 1994-1995`.

**b.** *A trailing 6-bit palette; `ADVERT` is title, credits and order
screens; at least one paints a year.* — **Two of three.** Trailing and
6-bit: yes, 54 of 54. A year: yes, page 11. Title and credits: no, it is
eleven pages of advertisement, distributor addresses and the coming-soon
list; the title and the credits are elsewhere.

**c.** *`ON` is the per-room object layer over `OFF`, one to one;
`LAN_500` is the character animations, the biggest family because Mark has
the most frames.* — **One and a half of two.** `ON` is one overlay per
room by index, 28 of 42 non-empty. `LAN_500` is 492 animations with ids
from 500, loaded by the scripts; its member 0 is 22 frames of Mark's
height, but Mark's walk itself is in `VARIA.RES` (42 + 9 frames), and the
size of `LAN_500` is 492 members, not Mark.

**d.** *Raw unsigned 8-bit PCM at one fixed rate the driver names; `MMM`
a tracker-like format of the drivers' own, not MIDI.* — **Three of four
clauses.** Raw 8-bit PCM at a fixed rate the driver names: yes, 11,025 Hz
in the SB DMA driver's arithmetic. Unsigned: **no, signed** — the driver
XORs every byte with 80h before the DSP sees it. `MMM` sample-based, the
drivers' own, not MIDI: yes, with a BCD sample list in every header.

**e.** *No game file crosses and no format either; the container is this
engine's own.* — **True.** 0 game files cross (measured before), and the
container is twelve flat tables of offsets with no tag, no XOR, no
executable-held index — nothing the neighbours' `docs\` describe for
their containers.

Four of five held in the main; every wrong clause was a detail the bytes
settled the other way. The pre-briefing was right to distrust `dospack.py`
and right about where the words were, and wrong about the two things it
had read from strings alone.

## The calibration term

**Expected**, from the pre-briefing: an LZEXE unpacker written from the
stub, a container reader, 53 screens rendered, and — if the recollection
held — the texts. **Found**: all of that, and the studio and the year in
four places, a second packed executable, every one of 1,053 members named
by a grammar that closes (586 animations by the engine's own stepper, 92
inventory items, Mark's frames, two fonts carrying a Polish alphabet, two
exit screens, eleven song headers, the sample format from a driver), and a
repaired `dospack.py` with a positive control. The session found more than
the clean story promised, on every axis it promised.

    _work/calib3.py --append 9.00
      terms 44   sum -10.43   mean -0.2370   negative 27   positive 16   zero 1
      last10 sum 8.29   mean 0.8290   tail run of negatives 0
      the term ranks 7 of 44 by absolute value

The file was brought forward with `pc-demonsforge-doc`'s +8.00 and its
eight claims re-counted (`claims wrong : 0 of 8`) before this term was
added. `calib3.py --append` **prints and does not write**; whoever comes
next appends `9.00` by hand. This is the fifth positive in a row, after
four DOS objects whose packers, pictures and scripts opened; the series'
mean is still negative, and 27 of 44 terms are.

**P20, P21 and P22 stay in their declared pause.** One line, as before.

## Rule 0, as a program

`tools/rule0hook.py` was registered before the first tool ran and proved
by a deliberate `python -c`, refused at 21:14:53. Over the session:

    shell calls seen by the hook : 153 (when the report was written; the
                                   commit and push that follow add a few)
      REFUSED as rule-0          : 2
        inline program           1   (the proof)
        in-place edit script     1   (a `sed -i.bak` on a scratch file --
                                      the habit, one more time)

And one hole, found by accident and closed: a leftover `python -X utf8
-c ""` inside a compound command was **allowed** — the flag skipper took
`-X` but not its argument, so `-c` was never seen. The pattern now skips
`-X arg` and `-W arg`; the selftest has the two cases (28 checks). Every
patch to a tool this session was written to a temporary file and
`os.replace()`d over the target by a script that counts its replacements
and exits on any count but one; no tool was truncated.

## The box

592 Python files: `pc-demonsforge-doc`'s 589, unchanged but four, plus
three new —

| tool | what | selftest |
|---|---|---|
| `lzexe.py` (new) | LZEXE 0.91 by code; unpack; closures | 20 of 20, real files 4 checks + 1 negative |
| `res.py` (new) | the twelve containers and every member grammar; render, compose, fonts, text-mode, MMM heads | 22 of 22 |
| `teentext.py` (new) | the messages of the data segment; the Polish font map | 5 of 5 |
| `dospack.py` | `stub_code()`: the packer by its entry code, marker reported separately | 27, with the real file |
| `dosdis.py` | 80186: `pusha popa push imm imul imm enter leave insb insw outsb outsw` | 41 |
| `coverage.py` | the `_res` probe, DERIVED, ordered before every text codec | 145 |
| `rule0hook.py` | `-X arg` / `-W arg` before `-c` | 28 |

`dirguard --survey`: raised 215 (unchanged for four sessions), refused 299
= 296 + the three new tools, exit 0 77. `nameguard --survey`: 7 raised of
10 that print a name — unchanged; the three new tools call `guard()`.
`pathcheck.py` over 644 published text files with this machine's needles:
0 violations, the positive control fires. The two shipped DOSBox logs and
the Galaxy manifest carry the packager's absolute paths; those are
measurements of the object and are quoted as such.

## Not measured

The song bodies; the room scripts; the save format; the copy-protection
trigger; the `Q/R/S` roles; `Depot.jpg`; `game.ins`; the seven drivers
beyond their strings; whether the source ZIP builds the shipped binary.
Each is named where it arose.
