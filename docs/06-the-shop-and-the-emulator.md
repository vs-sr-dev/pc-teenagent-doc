# 06 — The shop and the emulator: 83.5 % of the bytes, 0 % of the game, and six clocks that are none of the game's

*Measure: `python tools/hashdb.py Teenagent/goggame-1207658753.hashdb --list --check --root Teenagent` (notes/hashdb.txt); `python tools/gogmanifest.py --root Teenagent` (notes/gogmanifest.txt); `python tools/zipdir.py Teenagent/DOSBOX/dosbox-staging-release-0.82.x.zip` and `zipclocks.py`; `python tools/crossall.py _work/sha1-all.txt --collection .. --skip pc-teenagent-doc` (notes/crossall.txt); `python tools/treecensus.py Teenagent` (notes/treecensus.txt).*

## The shop, filed

GOG's furniture is 25 files and 41,211,639 bytes, and the nine GOG installs
already in the collection documented every piece of it; this section cites
them and compares.

* **`goggame-1207658753.hashdb`** — a 698-byte ZIP holding 12 + 17 × 1,056
  bytes (narrow mode), DOS date 2025-11-19 13:38:06: **17 records, the 12
  `.RES`, the 2 `.EXE`, `SOUND.SET`, `Depot.jpg`, `support.txt`; MD5 17 of
  17 match the files on disk.** GOG verifies the game and nothing else —
  not DOSBox, not its own uninstaller. The neighbours' counts, from their
  `docs\`: `pc-brokensword3-doc` 6,736 records, `pc-heretickingdoms-doc`
  56,853, `pc-twinsensquest-doc` 626, `pc-landsoflore-doc` 35,
  `pc-inquisitor-doc` 6,736 + 1 + 2 across three, `pc-brokensword4-doc` 1,
  `pc-brokensword5-doc` 2, `pc-themepark-doc` 0 (a 157-byte ZIP with no
  hashes), `pc-motoracer-doc` none at all. Seventeen is the second-smallest
  non-trivial one, and the only one whose every record is the game.
* **`goggame-galaxyFileList.ini`** — 427 declared (426 + 1 under `[ISI]`),
  10 absolute into `C:\ProgramData\GOG.com\Galaxy\support\...` (the
  packager's machine, a measurement, not a violation), 417 relative; **414
  present, 2 truly absent** (`__redist\ISI\scriptinterpreter.exe` and one
  named by an MD5), **19 present and undeclared** — the `supportData` the
  `.script` copies in: the three `.conf`, the two mapper files, the manual,
  `set_config\` — and among them **`set_config\Game Configurator.exe`,
  38,115,928 bytes, the largest file in the object, 40.9 % of it, in no
  manifest**. Residue against the walk: 0 files, 0 bytes.
* **`unins000.exe` / `.dat` / `.msg` / `.ini`** — Inno Setup, the setup-data
  string says **5.6.2 (u)**; a second pair under `DOSBOX\` says **6.4.0.1**
  and is the emulator's own. The GOG one is the same 1,343,048 bytes to the
  byte in seven other GOG installs here, and `gog.ico` (2017-09-28) and
  `support.ico` (2019-08-26) in four and five: those are the **4 of 416**
  crossings over 114 repositories, 488 lists and 173,344 tokens — all four
  the installer's furniture, none the game's, none DOSBox's.
* `goggame-1207658753.info`: product `Teenagent`, gameId 1207658753,
  `en-US` only, one play task: `DOSBOX\dosbox.exe -conf
  "..\dosboxTeenagent.conf" -conf "..\dosboxTeenagent_single.conf"
  -noconsole -c "exit"`. `Launch Teenagent.lnk`, `support.txt`,
  `goglog.ini`, an empty `Cloud_Saves\`, and **`Depot.jpg`** — 8,108 bytes
  in the verified payload, a logo reading *THE DEPOT* over a padlock,
  with no neighbour (`grep -ril "the depot" ../*/docs` finds only Steam's
  depots in `pc-academagia-doc`) and no explanation in a byte.

## The emulator, filed

**DOSBox Staging 0.82.2** — the binary says `dosbox-staging 0.82.2` and
`0.82.2 (5e2ba)`; the file name of the source ZIP says `0.82.x`; the ZIP's
comment is a different 40-hex commit, `f8c24f87…a52206be`. 393 files,
36,580,902 bytes: `dosbox.exe` and `dosbox_with_debugger.exe` (5.5 MB
each), 27 DLLs (SDL2, fluidsynth, mt32emu, opus, ...), 186 Xbox mapper
files for other games, 18 FreeDOS code pages and four keyboard drivers
(the classifier's 42 opaque files are 18 `.cpi`, 13 `.txt`, 4 `.sys`, 2
Inno `.dat`, 2 FreeDOS `.com`, `unins000.msg`, the `.lnk`, `SOUND.SET`),
37 GLSL shaders, and a
7.9 MB ZIP that is the release's **source tree**: 1,618 members,
24,809,116 bytes uncompressed, every DOS date 2025-06-17, UT field +7 h.
The two DOS-on-GOG neighbours, `pc-landsoflore-doc` and
`pc-themepark-doc`, documented DOSBox 0.74-2 with a source tarball; this
is a different generation, new to the collection, and nothing in it
crosses.

The configuration is `dosboxTeenagent.conf` (1,544 lines, Staging's
commented defaults with GOG's edits) plus two `[autoexec]` files:

    _single.conf    mount C ".."; mount C "..\cloud_saves" -t overlay;
                    imgmount d "..\game.ins" -t iso; c:; TEENAGNT.EXE
    _settings.conf  mount C ".."; c:; cls; SOUNDSET.EXE; exit

**`game.ins` is configured, was present on the packager's machine, and is
not here.** `DOSBOX\stderr.txt`, shipped, logs at 2025-11-06 09:26:59
`IMGMOUNT: Path '..\game.ins' found`; the file is in neither the tree nor
the manifest. That is the whole measurement: a CD image existed there and
was left out; what it held is not in a byte here.

## The six clocks, and the game's own

| clock | what |
|---|---|
| **1994** | eight times in `SDR.RES`, the driver author's copyright; `(c) Metropolis 1994` in `SOUNDSET.EXE` unpacked |
| **1994–1995** | `(c) 1994-1995` in the credit roll of the unpacked engine; *Coming spring 1995!* painted on advert page 11 — **the game's own year, from its bytes** ([04](04-the-words.md)) |
| 2017-09-28 / 2019-08-26 | `gog.ico` / `support.ico`, the only two mtimes the installer preserved |
| 2025-06-17 | the DOS dates of all 1,618 members of the DOSBox Staging source ZIP |
| 2025-11-06 08:51 and 09:26–09:28 | two DOSBox logs GOG shipped: the packager's runs, on a machine with an NVIDIA 577.00 driver, a 1422 × 1066 window, and `game.ins` |
| 2025-11-19 13:38:06 | the DOS date of the ZIP inside the `.hashdb`: GOG's build |
| 2026-09-11 19:49 | the mtime of 431 of 433 files: the install |

The pre-briefing left `Year` and `Studio` open. Both are closed from the
inside: 1994–1995 and Metropolis Software House, printed by the program,
painted by the data, and typed on the registered-version screen.

## What is not measured

`Depot.jpg`. `game.ins`. What the Game Configurator does beyond editing
`dosboxTeenagent.conf` by its `config_options.ini`. Whether the source ZIP
and the binary are the same commit (their hashes differ; nothing was
built to check).
