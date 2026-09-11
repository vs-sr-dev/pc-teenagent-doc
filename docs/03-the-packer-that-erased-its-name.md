# 03 — The program: a packer that erased its name, read from its own stub and removed

*Measure: `python tools/dosdis.py Teenagent/TEENAGNT.EXE --at 78030 --length 0x14A --org 0x000E --targets` (notes/dosdis-lzexe-stub.txt); `python tools/lzexe.py Teenagent/TEENAGNT.EXE --unpack _work/TEENAGNT.unp.exe` (notes/lzexe-teenagnt.txt); `python tools/dospack.py Teenagent/TEENAGNT.EXE --sweep` (notes/dospack-teenagnt.txt).*

## What the sweep said, and why it was wrong by construction

`TEENAGNT.EXE` is 78,426 bytes: `e_cblp` 90, `e_cp` 154 — (154 − 1) × 512 +
90 = 78,426, nothing appended — `e_crlc` **0**, a 32-byte header, entry
130A:000E, entropy 7.8498 over the image, all 256 byte values present.
`strdump.py` prints 411 runs of five or more and every one is noise. Rule 2
of `dos-platformnotes-doc` — no relocations means a packer's stub — gets its
first positive case in four DOS objects.

`dospack.py --sweep` looked for 30 signatures and found **0 in place**; its
LZEXE test is the four bytes `LZ91` at header offset 1Ch, and at 1Ch this
file has `0C 0A 09 01`. (The pre-briefing quoted `1C 00 00 00`; that is
`e_lfarlc` + `e_ovno` at 18h, one row up in the hex dump. Both readings
agree the marker is gone.) The verdict "no packer" was the sweep being
right about markers and wrong about the file.

## The stub, all of it

The last 410 bytes of the file are one segment at 130Ah (file offset
78,016), and the entry point is 14 bytes into it. `dosdis.py` decodes the
330 bytes of code from 000Eh to 0158h with **168 instructions, 100 %
coverage, and 22 branch targets of which 19 land on instruction
boundaries** — the three that do not all land on the five bytes at 00F7h,
which are not code: they are the ASCII **`*FAB*`**, Fabrice Bellard's
signature inside the LZEXE decompressor. The packer took its name off the
header and left it in the stub.

The 14 bytes before the code are the packed program's own header:

    cs:0000  IP 0000    cs:0002  CS 0000    cs:0004  SP 0200    cs:0006  SS 19C4
    cs:0008  130Ah   paragraphs of compressed stream  (= e_cs: the stream is
                     everything between the MZ header and the stub, 77,984 B)
    cs:000A  123Fh   paragraphs the stream is moved UP before decoding
    cs:000C  019Ah   = 410, the stub's own length (`mov cx,[0Ch]; std; rep movsb`)

What the code does, in the order the listing gives it:

1. **000Eh–002Ah**: copy the stub to `ds + [0Ah]` and continue there at
   002Bh (`push bx; mov ax,2Bh; push ax; retf`).
2. **002Bh–0059h**: move the stream up by `[0Ah]` paragraphs in chunks of
   1000h paragraphs, top down (`std; rep movsw`), so that decoding can
   write from the load segment upward without overrunning its input.
3. **0069h–00F4h, the decoder**: a 16-bit bit buffer loaded by `lodsw`,
   consumed LSB-first by `shr bp,1`, reloaded after sixteen takes
   (`dec dx; jnz`). Then:

        bit 1                        literal byte  (movsb)
        bit 0, bit 0, b1, b0         length 2 + (b1 b0 via `rcl cx,1` twice),
                                     distance byte d: bh = 0FFh, bl = d
        bit 0, bit 1, word w         bh = (hi(w) >> 3) | 0E0h, bl = lo(w):
                                     a 13-bit distance; length = (hi(w) & 7) + 2,
                                     or, when that is 0, one more byte e:
                                       e = 0   end of stream
                                       e = 1   re-normalise es:di and ds:si
                                       else    length = e + 1
        copy: `mov al,es:[bx+di]; stosb; loop` -- byte by byte, so
        overlapping copies repeat their pattern

4. **00FCh–0134h, the relocation rebuilder**: `mov si,158h` names the
   list; then a byte `b ≠ 0` advances the address by `b` and adds the
   load segment to the word there; a byte 0 is followed by a word: 0
   advances by 0FFF0h without relocating, 1 ends, anything else is a
   16-bit advance with a relocation.
5. **0136h–0156h**: `di = [4]; si = [6] + loadseg; [2] += loadseg; ss:sp;
   jmp far cs:[0]` — the first eight bytes of the stub are the program's
   real entry.

`tools/lzexe.py` is those five paragraphs as code, with the byte offsets
of the listing in its comments. It selects a file by the **code** — the 29
entry bytes and the 204 bytes of decoder, compared exactly — and reports
the marker as a separate line. It refuses an entry that matches with a
decoder that does not ("a variant this tool has not read").

## The closures

    stream              77,984 B = 130Ah paragraphs, header..stub  (= e_cs)
    decoded image       152,434 B (2538h paragraphs) from 77,969 of 77,984
                        stream bytes -- the 15 left are the paragraph padding
    literals / short / long / long-ext / normalise : 27,170 / 9,204 / 13,275 / 1,143 / 3
    stream ended on END code : True
    relocations         39 from 66 list bytes, 0 skips; 39 inside the image;
                        every relocated word <= 2538h
    relocated segment values : 0B52h x29, 19E4h x8, 1C79h x1, 2538h x1
    output MZ           152,626 B, header 192 B (28 + 39 x 4, padded),
                        e_cp x 512 + e_cblp = 152,626 : closes
    entry 0000:0000     inside the image; its first instruction is
                        `mov ax,0B52h; mov ds,ax; mov es,ax; jmp 0DCh`

The last line is the closure the decoder was not told about: the relocated
segment the program's first instruction loads into `ds` is the commonest
relocation value, and it is the data segment every string in chapter 04
lives in. The three `normalise` codes are where the output crossed 8 KB
boundaries the stub re-bases `es` at; in a linear buffer they write nothing.

`e_minalloc` is **reconstructed** (79 = 4707 + 4900 − 9528 paragraphs, on
the assumption that the packer kept the program's total memory demand);
`e_maxalloc`, `e_csum`, `e_ovno` are copied; the original header length is
not recoverable and is not claimed. The map of the image, from the
relocations and the stub header:

    0000h..B520h    code, 46,368 B          (`mov ax,0B52h` at 0000h)
    B520h..19C40h   data, 59,680 B          (every message; ds:0013h = `sound.set`,
                                             `off.res` ... `advert.res`, `teenage0.sav`)
    19C40h..19E40h  stack, 512 B            (ss:sp 19C4:0200)
    19E40h..25372h  two buffer segments, 19E4h and 1C79h, 46,386 B; 2538h
                    (the paragraph after the image's end) is the one
                    relocated constant above them, `mov dx,2538h` at code
                    0B30Bh -- what it is used for was not read

## SOUNDSET.EXE is packed too

The pre-briefing filed the 4,227-byte `SOUNDSET.EXE` as "not packed (its
strings are readable)". `lzexe.py` identifies it by the same 29 + 204
bytes, with the **same four bytes `0C 0A 09 01`** at 1Ch, and unpacks it
to 5,785 bytes with 4 relocations, 3,839 of 3,840 stream bytes consumed,
closing the same way. Its strings were readable because a 4 KB file
leaves most of itself as literals (2,055 literals against 840 matches);
unpacked, it says **`Sound Source Setup v1.00 (c) Metropolis 1994`** and
lists the eight sources it can save into `SOUND.SET`: Auto-detect, Gravis
UltraSound, SoundBlaster Pro, SoundBlaster, Covox, AdLib, PC Speaker, no
sound. Two files, one packer, one replaced marker: whoever built the
release ran the same tool over both.

The negative control is FreeDOS's `xcopy.exe` from the DOSBox tree, a real
MZ with one relocation: refused at the first test (`e_crlc = 1`).

## The repair to dospack.py

`dospack.py` now prints, before the sweep, **THE ENTRY STUB'S CODE**: the 29
bytes at cs:ip compared with LZEXE 0.91's, the 204 bytes after them, and
the marker at 1Ch with the verdict *"ABSENT: the packer is named by the
code, and the signature sweep below is wrong about it"*. Its selftest
builds an MZ with the entry and no marker and expects the name; changes
one byte of the entry and expects none; and, when `Teenagent\` is present,
checks the real file (27 checks, 0 failures). The sweep is unchanged — it
is still right about what it measures.

## What was not read

The 46 KB of engine code beyond what chapters 04 and 05 needed: the room
scripts and their interpreter, the dialogue logic, the save format
(`teenage0.sav`), the two anti-piracy messages' triggers (*Due to
anti-virus blockade you have to install this game from original disks* and
*Call yourself pirate, hacker, elite or whatever. But you are a THIEF.*
sit in the data segment next to a DOS error table). `farcalls.py` was not
run: the program has one code segment and no far calls to count.
