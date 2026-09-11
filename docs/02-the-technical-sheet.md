# 02 — The technical sheet: every figure with the command that re-derives it

*Measure: the command on each row, run from the repository root; outputs in `notes\`.*

## The object

| figure | value | command |
|---|---|---|
| files / directories / bytes | 433 / 34 / 93,184,691 | `python tools/treecensus.py Teenagent` |
| distinct SHA-1 / repeats | 416 / 17 | `python tools/hashall.py Teenagent` |
| the game (15 files) | 15,392,150 B, 16.5179 % | `python _work/families.py` (three-way split, re-counted) |
| the twelve `.RES` | 15,309,492 B, 16.4292 % | `python tools/res.py --census Teenagent` |
| DOSBox Staging (`DOSBOX\`) | 393 files, 36,580,902 B, 39.2563 % | `python _work/families.py` |
| GOG storefront + configurator | 25 files, 41,211,639 B, 44.2258 % | same |
| coverage: specified / derived / opaque | 379 / 12 / 42 files; 80.6898 / 16.4292 / 2.8811 %; residue 0 | `python tools/coverage.py tree --root Teenagent` |
| crossings with the collection | 4 of 416 over 114 repositories, 488 lists, 173,344 tokens | `python tools/crossall.py _work/sha1-all.txt --collection .. --skip pc-teenagent-doc` |
| private data / build paths | 0 personal (both controls fire); 46 drive-letter + 14 unix build-path blobs, all the packager's or the shaders' | `python tools/sift.py personal --root Teenagent`; `... buildpath` |
| protections | 0 real markers over 39 binaries; control 39 of 39 | `python tools/protscan.py Teenagent` |

## The program

| figure | value | command |
|---|---|---|
| `TEENAGNT.EXE` | 78,426 B; `e_crlc` 0; header 32; cs:ip 130A:000E; entry file offset 78,030; entropy 7.8498 | `python tools/mz.py Teenagent/TEENAGNT.EXE`; `python tools/dospack.py Teenagent/TEENAGNT.EXE --sweep` |
| signature sweep | 0 of 30 in place, 1 stray `RB`; **by code: LZEXE 0.91, marker `0C 0A 09 01` absent** | same `dospack.py` (repaired: `stub_code()`) |
| the stub | 330 bytes of code, 168 instructions, 100 % decoded, 22 branch targets, 3 landing in `*FAB*` | `python tools/dosdis.py Teenagent/TEENAGNT.EXE --at 78030 --length 0x14A --org 0x000E --targets` |
| stub data at cs:0 | IP 0000, CS 0000, SP 0200, SS 19C4, stream 130Ah paragraphs, shift 123Fh, stub 019Ah = 410 B | `python tools/lzexe.py Teenagent/TEENAGNT.EXE` |
| unpacked | 152,434 B image (2538h paragraphs) from 77,969 of 77,984 stream bytes; literals 27,170, short 9,204, long 13,275, long-ext 1,143, normalise 3; END reached | `python tools/lzexe.py Teenagent/TEENAGNT.EXE --unpack _work/TEENAGNT.unp.exe` |
| relocations | 39 from 66 list bytes, 0 skips; all inside; every relocated word ≤ 2538h; values 0B52h x29, 19E4h x8, 1C79h x1, 2538h x1 | same (`relocated segment values` line); `python tools/mz.py _work/TEENAGNT.unp.exe --relocs` (39 of 39 inside the image) |
| output MZ | 152,626 B, header 192, closes on its size; `e_minalloc` reconstructed 79 = 4707 + 4900 − 9528 | same |
| segments | code 0000h (46,368 B), data 0B52h (59,680 B), stack 19C4:0200, buffers 19E4h and 1C79h to 2538h | `python tools/dosdis.py _work/TEENAGNT.unp.exe --at 192 --length 12 --org 0` (`mov ax,0B52h; mov ds,ax`) |
| `SOUNDSET.EXE` | 4,227 B, also LZEXE 0.91, same replaced marker; unpacks to 5,785 B, 4 relocations, 3,839 of 3,840 stream bytes | `python tools/lzexe.py Teenagent/SOUNDSET.EXE --unpack _work/SOUNDSET.unp.exe` |
| negative control | FreeDOS `xcopy.exe` refused (`e_crlc = 1`) | `python tools/lzexe.py --refuse Teenagent/DOSBOX/resources/drives/y/dos/xcopy.exe` |
| `SOUND.SET` | `04 20 02 07 01` = SDR member 4 (1-based) = SoundBlaster Pro driver v1.26, port 220h, IRQ 7, DMA 1 | `python tools/dosdis.py _work/TEENAGNT.unp.exe --at $((192+0xAA75)) --length 0x40 --org 0xAA75` |

## The words

| figure | value | command |
|---|---|---|
| messages / lines / words / characters | 656 / 1,217 / 4,338 / 23,418 in the data segment 0B520h..19C40h (59,168 B walked) | `python tools/teentext.py _work/TEENAGNT.unp.exe --count` |
| messages with a coded head byte | 285 | same |
| the credits | 39 lines from `programming / ADRIAN CHMIELARZ` to `(c) 1994-1995` at 19937h | `python tools/teentext.py _work/TEENAGNT.unp.exe --polish --grep METROPOLIS` |
| file names the engine opens | `sound.set`, 12 `.res`, `teenage0.sav` at ds:0013h | `python tools/strdump.py _work/TEENAGNT.unp.exe --min 6` |
| the font map | 16 punctuation slots → Polish letters, read off `VARIA.RES` member 6 | `python tools/res.py Teenagent/VARIA.RES --font 6 --out _work/font6.png` |

## The containers

| figure | value | command |
|---|---|---|
| twelve directories | `u32 count` + `count+1` offsets; first = 4+4(count+1); last = length; 12 of 12 close, residue 0; 1,053 members | `python tools/res.py --census Teenagent` |
| the engine reads them the same way | `open; lseek 4·cx; read 8; size = next − this; lseek; read; close` at code 0B0D4h | `python tools/dosdis.py _work/TEENAGNT.unp.exe --at $((192+0xB0D4)) --length 0x74 --org 0xB0D4` |
| screens | 54 of 64,768 B = 320×200 + 768; palette TRAILING, 6-bit (all ≤ 63): ADVERT 11, OFF 42, UNLOGIC 1 | `python tools/res.py Teenagent/OFF.RES Teenagent/ADVERT.RES Teenagent/UNLOGIC.RES --render _work/screens` |
| sprites | 124: ONS 113, UNLOGIC 10, VARIA 1 — `w, h, screen offset, w·h pixels`, FFh transparent, stride 320 | blitter: `python tools/dosdis.py _work/TEENAGNT.unp.exe --at $((192+0x1B10)) --length 0x2D --org 0x1B10` |
| overlays | 31: ON 28 (+14 empty of 42), VARIA 3 — `u8 n, u16 off[n], n sprites`; 6 of VARIA[3]'s 92 entries are sequences | `python tools/res.py Teenagent/ON.RES --list`; `... VARIA.RES --entries 3` |
| animations | 586: LAN_000 94 (+74 empty of 168 = 42 rooms × 4 slots), LAN_500 492 (ids 500+); stepper grammar; 1 of 660 with one trailing byte | stepper: `python tools/dosdis.py _work/TEENAGNT.unp.exe --at $((192+0x2D8B)) --length 0xFA --org 0x2D8B`; `python tools/res.py Teenagent/LAN_500.RES --frames 1` |
| a room composed | OFF + ON + LAN_000 slots at step 0, e.g. room 20 | `python tools/res.py --room 20 --out _work/room20.png` |
| fonts | VARIA[6] 97 glyphs, VARIA[7] 95; `u8 h, u8 w, h·w` of 0/1/2; tile the member | `python tools/res.py Teenagent/VARIA.RES --font 6`; `--font 7` |
| text-mode screens | VARIA[9] registered, VARIA[10] shareware; 3,680 = 80×23×2 | `python tools/res.py Teenagent/VARIA.RES --textmode 9`; `--textmode 10` |
| music headers | 11 of 11 `MMM`; 3..7 BCD sample numbers each; 51 distinct = SAM_MMM's 51; Q/R/S tags | `python tools/res.py Teenagent/MMM.RES --mmm` |
| samples | signed 8-bit PCM (`xor [bx],8080h` before DMA), 11,025 Hz (`div` by 2·2B11h → time constant 167) | `python tools/dosdis.py _work/sdr/SDR.006 --at 0x50 --length 803 --org 0x50 --targets` after `python tools/res.py Teenagent/SDR.RES --extract _work/sdr` |
| drivers | 8: GUS 2,264 B, AdLib 743, SB 4,759, SB Pro 4,766, PC Speaker 718, none 51, SB DMA 883, Covox 441 | `python tools/res.py Teenagent/SDR.RES --list` |

## The shop and the emulator

| figure | value | command |
|---|---|---|
| `goggame-1207658753.hashdb` | 17 records × 1,056 B (narrow), MD5 17 of 17 match | `python tools/hashdb.py Teenagent/goggame-1207658753.hashdb --list --check --root Teenagent` |
| `goggame-galaxyFileList.ini` | 427 declared (426 + 1 ISI), 10 absolute, 417 relative; 414 present, 2 absent, 19 present-undeclared (41,083,424 B) | `python tools/gogmanifest.py --root Teenagent` |
| DOSBox Staging source ZIP | 1,618 members, 24,809,116 B uncompressed, every DOS date 2025-06-17, comment a 40-hex commit | `python tools/zipdir.py Teenagent/DOSBOX/dosbox-staging-release-0.82.x.zip`; `zipclocks.py` |
| the absent CD image | `imgmount d "..\game.ins" -t iso` in `dosboxTeenagent_single.conf`; `IMGMOUNT: Path '..\game.ins' found` in `DOSBOX\stderr.txt` at 2025-11-06 09:26:59; not on disk, not in the manifest | `grep -n game.ins Teenagent/DOSBOX/stderr.txt Teenagent/dosbox*.conf` |

## The box

| figure | value | command |
|---|---|---|
| tools | 592 `.py` = 589 of `pc-demonsforge-doc` + `lzexe.py`, `res.py`, `teentext.py`; 4 modified (`coverage.py`, `dosdis.py`, `dospack.py`, `rule0hook.py`) | `python tools/toolsdiff.py ../pc-demonsforge-doc/tools` |
| selftests, `PYTHONIOENCODING` unset | lzexe 20/20, res 22/22, teentext 5/5, dospack 27, dosdis 41, coverage 145, rule0hook 28, dirguard 13, nameguard 13, pathcheck 10, toolsdiff 9 — 0 failures | `notes/selftests.txt` |
| dirguard survey | raised 215, refused 299 (296 + 3), exit 0 77 | `python tools/dirguard.py --survey` |
| rule 0 | 2 refusals in the session, 1 hole found and closed (`-X utf8 -c`) | `python tools/rule0hook.py --report` |
| absolute paths of this machine | 0 violations over 644 text files, positive control fires | `python tools/pathcheck.py --needle …` (needles masked) |
