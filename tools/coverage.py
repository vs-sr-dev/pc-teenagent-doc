#!/usr/bin/env python3
"""coverage.py -- what share of an object is in a format somebody published,
stated over a named denominator.

This repository's coverage figure has always been a share of bytes whose
format has a published specification. On this object that figure is different
at every layer, so the tool takes the layer as an argument and prints the
denominator on the same line as the share. A coverage number without its
denominator is not a measurement.

    members  the twelve files the ZIP holds
    product  the files the four InstallShield containers hold, by the expanded
             size each container's own entry table declares
    tree     every file under a directory, classified BY MAGIC and not by
             extension, into FOUR buckets

THE FOURTH BUCKET, AND WHY IT HAD TO EXIST
------------------------------------------
The three buckets below were written for an object whose unopened remainder was
either vendor-specified or described by nobody at all. They do not fit an object
whose whole unopened remainder is **publicly reverse-engineered and never
specified by its vendor** -- Microsoft's ITSF, and RPG Maker's own LCF. Calling
those `published` would claim a warrant that does not exist; calling them
`neither` would deny work other people did in public and that anybody can check.
So there are four, and each has a membership test somebody who disagrees can
apply:

  SPECIFIED  a document describing the format was published by the party that
             created it, or by a standards body that adopted it, and that
             document is what an implementer works from.
  DECODED    no such document exists, and an independent published third-party
             reverse engineering does -- one this repository can name.
  DERIVED    this session worked it out of the bytes and can name no public
             account of it.
  OPAQUE     none of the above.

**The bucket describes the FORMAT's public standing, not this session's route
to it.** ITSF and LCF are DECODED here even though every field this repository
uses was derived from the bytes, because the question a bucket answers is
"could a stranger check this against something", and for those two the answer
is yes and the something is not this repository.

**And the buckets are never summed into a coverage figure.** They may be summed
into an ACCOUNTING figure -- do the bytes add up to the object -- because that
is a question about bytes. Coverage is a question about warrant, and warrants
of different kinds do not add.

A format counts as PUBLISHED when a specification exists outside this
repository: PKWARE's APPNOTE for ZIP, Microsoft's NE and PE, the MIDI
Manufacturers Association's Standard MIDI File, Microsoft's BMP and RIFF WAVE,
and plain text. It counts as DERIVED when this session worked it out of the
bytes: InstallShield's Z archive, its `_INST32I` container and its `.PKG`
manifest. It counts as NEITHER when nobody here opened it and nobody outside
has written it down: WinHelp 3.x, and RPG Maker's own `.DAT` and `.ATR`.

The three buckets are printed separately and are never merged, because
"derived by this session" is a weaker claim than "published by a vendor" and
folding them together would hide that.

    python tools/coverage.py members --members _work/members
    python tools/coverage.py product --members _work/members
    python tools/coverage.py selftest
"""
import argparse
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmb                                       # noqa: E402
import fnt                                       # noqa: E402
import forgedat                                  # noqa: E402
import hxg                                       # noqa: E402
import hxgsave                                   # noqa: E402
import is32                                      # noqa: E402
import isz                                       # noqa: E402
import nameguard                                 # noqa: E402
import pes                                       # noqa: E402
import pif                                       # noqa: E402
import res                                       # noqa: E402

# This object is the first in the collection with a file name outside Latin-1,
# and `ambiguity` mode prints file names. The box's convention -- a tool that
# prints recovered text sets its own output encoding -- had never been applied
# to NAMES, and this tool died on its own first run for exactly that reason.
nameguard.guard()

PUBLISHED = {
    "MID": "Standard MIDI File (MMA RP-001)",
    "BMP": "Windows bitmap (Microsoft)",
    "WAV": "RIFF WAVE (Microsoft and IBM)",
    "EXE": "NE and PE (Microsoft)",
    "DLL": "NE and PE (Microsoft)",
    "TXT": "plain text",
    "INI": "plain text",
    "DIZ": "plain text; CP437 and CP866 render it identically",
    "ID": "plain text",
}
DERIVED = {
    "1": "InstallShield Z archive, derived here",
    "LIB": "InstallShield Z archive, derived here",
    "INS": "InstallShield Z archive, derived here",
    "EX_": "InstallShield _INST32I container, derived here",
    "PKG": "InstallShield manifest, derived here",
}
NEITHER = {
    "HLP": "WinHelp 3.x, no published specification",
    "DAT": "RPG Maker's own, no published specification",
    "ATR": "RPG Maker's own, no published specification",
    "INS_product": "InstallShield compiled setup script, not opened here",
}


def ext_of(name):
    base = name.rsplit("\\", 1)[-1]
    if "." in base[1:]:
        return base.rsplit(".", 1)[-1].upper()
    return "(none)"


def bucket(ext, mode="members"):
    # `.INS` is a Z archive at the member layer and a compiled setup script
    # at the product layer. Same three letters, two different things, and
    # one table must not silently claim the other was opened.
    if ext == "INS" and mode == "product":
        return "neither", NEITHER["INS_product"]
    if ext in PUBLISHED:
        return "published", PUBLISHED[ext]
    if ext in DERIVED:
        return "derived", DERIVED[ext]
    if ext in NEITHER:
        return "neither", NEITHER[ext]
    return "neither", "not identified in this session"


def population(mode, members):
    rows = []
    if mode == "members":
        for n in sorted(os.listdir(members)):
            rows.append((n, os.path.getsize(os.path.join(members, n))))
        return rows, "the twelve files the ZIP holds"
    for name in ("_SETUP.1", "_SETUP.LIB", "SETUP.INS"):
        p = os.path.join(members, name)
        for e in isz.parse(open(p, "rb").read(), p)["entries"]:
            rows.append((e["name"], e["expanded"]))
    p = os.path.join(members, "_INST32I.EX_")
    for r in is32.parse(open(p, "rb").read())["records"]:
        rows.append((r["name"], r["expanded"]))
    return rows, "the files the four containers hold, at their declared " \
                 "expanded sizes"


def report(rows, label, mode="members"):
    total = sum(s for _, s in rows)
    cnt = collections.Counter()
    byt = collections.Counter()
    for n, s in rows:
        e = ext_of(n)
        cnt[e] += 1
        byt[e] += s
    print("denominator : %d files, %d bytes -- %s" % (len(rows), total, label))
    print()
    print("  %-8s %6s %12s  %-10s %s"
          % ("ext", "files", "bytes", "bucket", "format"))
    for e, c in cnt.most_common():
        b, why = bucket(e, mode)
        print("  %-8s %6d %12d  %-10s %s" % (e, c, byt[e], b, why))
    print()
    sums = collections.Counter()
    counts = collections.Counter()
    for e in cnt:
        b, _ = bucket(e, mode)
        sums[b] += byt[e]
        counts[b] += cnt[e]
    for b in ("published", "derived", "neither"):
        print("  %-10s %4d files %12d bytes   %8.4f %% of %d"
              % (b, counts[b], sums[b], 100.0 * sums[b] / total if total else 0,
                 total))
    print("  %-10s %4d files %12d bytes"
          % ("SUM", sum(counts.values()), sum(sums.values())))
    if sum(sums.values()) != total:
        print("  THE BUCKETS DO NOT SUM TO THE DENOMINATOR", file=sys.stderr)
        return 1
    return 0


# ------------------------------------------------------------------ by magic
#
# The `tree` mode classifies a file by its leading bytes, because this object
# ships two Windows executables named `.dat` and an extension table would put
# 1,498,112 bytes in the wrong row.

def _printable(b):
    if not b:
        return False
    return all(32 <= x < 127 or x in (9, 10, 13) for x in b[:512])


def _is(prefix):
    return lambda b: b.startswith(prefix)


# cp437's shading blocks and line-drawing set, which is one contiguous band.
CP437_BOX_LOW, CP437_BOX_HIGH = 0xB0, 0xDF


def _cp437_art(b):
    """Text drawn with cp437's box-drawing and shading characters.

    THE DEFECT THIS REPAIRS, WHICH IS THE THIRD OF ITS CLASS
    --------------------------------------------------------
    `pc-hexxagon-doc`'s `COME.SEE` is an advertisement for a bulletin board in
    Ohio, in English, drawn in cp437 frames. This table filed it as
    **plain text, Shift-JIS**, because `_cp932_text` asked the only question it
    can ask -- does this decode without an illegal sequence -- and the answer
    was yes. Shift-JIS gives 0xA1..0xDF to single-byte half-width katakana;
    cp437 puts its blocks and frames at 0xB0..0xDF. **Two codepages share a
    byte range and mean different things in it**, and no decode test can
    separate them, because both decodes are legal.

    What separates them is where the high bytes SIT. cp437 art uses one
    contiguous band and nothing else: on `COME.SEE`, 190 high bytes, 190 of
    them inside 0xB0..0xDF, nine distinct values, and not one Shift-JIS
    double-byte lead (0x81..0x9F, 0xE0..0xEF) anywhere in the file. Japanese
    prose written only in half-width katakana, with no kanji and no kana above
    0xDF, would satisfy this too -- **that file is possible and this test would
    misfile it**, which is said here rather than discovered later. The trade is
    deliberate: a page of frames drawn in an English BBS advert is a thing this
    collection meets, and a katakana-only Japanese document is not.

    This is the third instance of the cp437 class, after
    `pc-ilgrandegiocoditangentopoli-doc`'s `INSTALL.BAT`.
    """
    if not b:
        return False
    high = [x for x in b if x >= 0x80]
    if not high:
        return False
    if not all(CP437_BOX_LOW <= x <= CP437_BOX_HIGH for x in high):
        return False
    # and the rest has to be text at all, on the same terms as _printable
    return all(32 <= x < 127 or x in (9, 10, 13) for x in b if x < 0x80)


def _hxg(b):
    """The HXG container of HEXXAGON (Argo Games, 1993), by its arithmetic.

    The format carries no textual magic. It carries something better: a `u16`
    count, `count` records of fourteen bytes, and three closures that a file
    does not satisfy by accident -- the directory ends exactly where the data
    begins, every member's offset plus its stored length is the next member's
    offset, and the last member ends on the last byte of the file. On
    `GRAPHICS.HXG` that is 452 records and 451 chained links at residue zero
    twice.

    The bucket is **DERIVED**, and the reason is worth stating because the
    object argues the other way. `HEXXAGON.DOC` has a section called
    TECH-WEENIE STUFF in which the programmer names the four tools he wrote and
    describes his own compressor as using "a vaguely LZSS-like method". That is
    a named producer, contactable in 1993, writing about his own format -- and
    **it is still not a specification.** It names no field, no offset and no
    byte. Prose about a format is evidence; a document an implementer can work
    from is a warrant. The DERIVED test asks whether this session can name a
    public account of the format, and the answer here is no. See
    `tools/hxg.py`, whose docstring carries the grammar and the counts.

    NOTE THE WEAKER WARRANT. This classifier reads a 512-byte head, which is
    36 records and 35 links. That is the first closure and every link that
    fits, and it is NOT the third closure, which needs the file's length.
    `hxg.py --validate` is the full test; this is what a head-reading
    classifier can honestly claim, and the difference is said out loud rather
    than papered over.
    """
    return hxg.looks_like_hxg_head(b)


def _pif(b):
    """A Windows 3.x Program Information File, by its section chain.

    369 bytes of standard section, then a chain of 22-byte headers beginning
    with `MICROSOFT PIFEX`, whose lengths account for every byte of the file.
    `HEXX.PIF` is 995 bytes and closes exactly; `pc-baronbaldric-doc/docs/04`
    did the same arithmetic on a 545-byte one.

    The bucket is SPECIFIED, and the warrant is **cited and not
    re-established here**: `pc-baronbaldric-doc/docs/04` states that the PIF
    layout is published by Microsoft and reads every field from it. This
    repository holds no copy of that document and does not claim to have
    checked one. See `tools/pif.py`, which is that repository's parser.
    """
    return pif.is_pif(b)


def _hxg_board(b):
    """A HEXXAGON board file, by its own arithmetic.

    1,690 bytes of 169 ten-byte records, of which exactly 108 carry the
    off-board sentinel in word 3 -- leaving 61, which is the number of hexes
    on a Hexxagon board. **The extension does not decide anything**: these are
    called `.HXG` and so is the 626 KB container, and `_hxg` and this test
    refuse each other's files. DERIVED, for the same reason as `_hxg`: the
    game wrote these and nobody described them. See `tools/hxgsave.py`.
    """
    return hxgsave.is_board(b)


def _hxg_config(b):
    """HEXXAGON's 22-byte settings file: `HXG\\0`, seven little-endian words,
    `HXG\\0`. A format that brackets itself, and 4 + 14 + 4 = 22 with no
    residue. DERIVED. What the seven words mean is not established anywhere,
    and `hxgsave.py` says so when it prints them."""
    return hxgsave.is_config(b)


def _bmb(b, size=None):
    """A Tecnoart `.BMB` image or `.BMA` animation (BIANCO NATALE, 1994), by
    the arithmetic in `tools/bmb.py`: `u16 w`, `u16 h`, a flag byte that is
    the ASCII letter y or n, a frame count on the animation, then w x h x
    frames bytes of 8-bit pixels, a 768-byte 6-bit VGA palette if the flag
    says y, and a four- or six-byte trailer -- and the sum lands on the last
    byte of the file, on 16 of 16 files in the object.

    THE WEAKER WARRANT, STATED. A 320 x 200 `.BMB` is 64,777 bytes and this
    classifier reads a 4,096-byte head. From the head alone it can check five
    bytes: two sides that fit a VGA screen and a flag byte that is y or n.
    **That is the whole head-only test**, and it cannot tell one image from a
    strip of frames. This probe therefore asks the classifier for the file's
    length as well -- the first probe in this table to do so, and the
    mechanism is the `wants_size` mark below -- and with the length it makes
    the closure, which decides `.BMB` against `.BMA` and refuses a file one
    byte off. What it still cannot see is the palette (every byte <= 0x3F)
    and the trailer. `bmb.py --validate` is the full test.

    The bucket is DERIVED. Nobody published this format; the only account of
    it outside this repository is the symbol names the producer's linker left
    behind in `BN.EXE` (`_BMBimage_in`, `save_pal`, `x_bob`, `y_bob`), and a
    name in a symbol table is not a specification.
    """
    return bmb.looks_like_head(b, size)


_bmb.wants_size = True


def _fnt(b, size=None):
    """FONT8X12.FNT of BIANCO NATALE: 96 cells of 8 x 12 at one byte per
    pixel, three byte values, cell 0 blank. See `tools/fnt.py`. The head is
    4,096 of 9,216 bytes; with the length the probe insists on 9,216, and
    without it on the three values and the blank first cell over what it was
    given. DERIVED, for the same reason as `_bmb`."""
    return fnt.looks_like_head(b, size)


_fnt.wants_size = True


def _mz(b, size=None):
    """An MZ executable, by the header behind the two letters and not by the
    letters alone.

    THE DEFECT THIS REPAIRS, WHICH IS THE OPPOSITE OF THE LAST ONE. On
    `pc-bianconatale-doc` the `.BMB` magic was too WEAK to fire from a head
    and was given the file's length. On `pc-outrun-doc` `_is(b"MZ")` fired on
    `CORV.PES`, `CHEVY.PES` and `BEETLE.PES`, three files with sprite names,
    and the pre-briefing filed the hit as a false positive: two ASCII bytes,
    a test too STRONG. It was not a false positive. All three ARE MZ images
    -- Microsoft EXEPACK'd, Microsoft C, the game's three video engines
    (docs/03) -- and the classifier was right for the wrong reason: a test
    that fires on two letters would have said the same of a text file that
    begins "MZ". So this probe reads what the letters promise: `e_cblp` below
    512, `e_cp` above 0, a header of at least 28 bytes that also holds the
    relocation table (`e_lfarlc + 4 * e_crlc <= header`), and a declared
    image at least as long as the header and -- when the length is handed
    over -- no longer than the file. OUTRUN.EXE and the three engines pass;
    "MZ" followed by prose does not, and the selftest fires that control.
    """
    if len(b) < 0x1c or b[:2] != b"MZ":
        return False
    e_cblp, e_cp, e_crlc, e_cparhdr = struct.unpack_from("<4H", b, 2)
    e_lfarlc = struct.unpack_from("<H", b, 0x18)[0]
    hdr = e_cparhdr * 16
    if e_cblp >= 512 or e_cp == 0 or hdr < 0x1c:
        return False
    declared = (e_cp - 1) * 512 + e_cblp if e_cblp else e_cp * 512
    if declared < hdr:
        return False
    if e_lfarlc < 0x1c or e_lfarlc + 4 * e_crlc > hdr:
        return False
    if size is not None and declared > size:
        return False
    return True


_mz.wants_size = True


def _pes(b, size=None):
    """The .PES / .PCS shape container of OUT RUN (SEGA / Unlimited Software
    Inc., 1989), by `tools/pes.py`: bit 7 of byte 0 set and a stage count of
    1 or 2 under it, a first stage of pack type 1 or 2, and -- for type 2,
    which every member here uses -- a canonical Huffman count table whose
    Kraft sum is exactly 1.0 over distinct symbols. THE WEAKER WARRANT: a
    head cannot run the two decompression stages to the declared sizes;
    `pes.py --census` does, 93 of 93. DERIVED: the grammar was read out of
    the game's own decoder in the unpacked EGA engine (docs/04), and nobody
    published it."""
    return pes.looks_like_head(b, size)


_pes.wants_size = True


def _forgedat(b, size=None):
    """GAME.DAT of THE DEMON'S FORGE (Mastertronic, 1987; "Dos Driver by
    Mok"), by `tools/forgedat.py`: a 49-byte ASCII signature at 0, a boot
    sector at 0x200 carrying `* Boot error *`, and at 0x400 a directory of
    12-byte records whose bodies chain a*512+c end-to-start to an all-zero
    terminator, the last inside the file's length. The 4,096-byte head holds
    the whole 121-record directory. DERIVED: the picture grammar was read out
    of the game's own drawing interpreter (docs/03); nobody published it."""
    return forgedat.looks_like_head(b, size)


_forgedat.wants_size = True


def _res(b, size=None):
    """The .RES container of TEENAGENT (Metropolis Software House, 1994-1995;
    Union Logic Software Publishing), by `tools/res.py`: `u32 count`, then
    `count + 1` monotonic u32 offsets whose first is 4 + 4 (count + 1) and
    whose last is the file's length. The 4,096-byte head holds a directory
    of up to 1,022 members (the largest here, LAN_500.RES, has 492). A head
    cannot decode a member; `res.py --census` does, 1,053 of 1,053 named by
    kind. DERIVED: the engine's loader at code 0B0D4h reads the same two
    offsets (docs/03); nobody published the container."""
    return res.looks_like_head(b, size)


_res.wants_size = True


def _cp932_text(b):
    """Text in a multi-byte codepage, and the test is that the codec REFUSES
    other things.

    A single-byte codepage cannot fail, so cp437 or cp866 "decoding" a file is
    no evidence at all. cp932 is a multi-byte codec with illegal sequences: a
    file of 8,899 high bytes that decodes under it with no illegal sequence,
    and whose decoded text is printable, is a Shift-JIS document, and a random
    byte stream is not. That asymmetry is the whole test and it is why this
    probe names cp932 and not the single-byte candidates.
    """
    if not b or not any(x >= 0x80 for x in b):
        return False
    try:
        s = b.decode("cp932")
    except UnicodeDecodeError as e:
        # A probe reads a fixed-size head, so the last sequence may be cut in
        # half. That is the probe's fault and not the file's: retry once
        # without the truncated tail. A failure anywhere earlier is the file's
        # and stands.
        if e.start < len(b) - 2:
            return False
        try:
            s = b[:e.start].decode("cp932")
        except UnicodeDecodeError:
            return False
    return all(c.isprintable() or c in "\t\r\n　" for c in s)


# Ruby's Marshal type characters, one byte each. A document is `04 08` -- major
# 4, minor 8 -- followed by exactly one of these. Two bytes alone are far too
# weak a signature to file 503,787 bytes on, so the probe reads the third byte
# too and rejects anything the grammar cannot start with. This is the same
# discipline as the length-prefixed LCF probes below and for the same reason.
MARSHAL_TYPES = set(b"0TFilfu:;\"I[{}oUCSc/me@dM'")


def _marshal48(b):
    return len(b) >= 3 and b[0] == 0x04 and b[1] == 0x08 and b[2] in MARSHAL_TYPES


def _ogg(b):
    # RFC 3533: a page begins 'OggS', then a version byte which is 0 in every
    # Ogg ever shipped. Checking it costs one byte and stops a file that merely
    # opens with the four letters.
    return b.startswith(b"OggS") and len(b) > 4 and b[4] == 0


# ---------------------------------------------------------------------------
# Five binary magics and two text codecs added on pc-rpgmakervxace-doc, where
# their absence put 44,113,740 bytes -- 12.8716 % of the object -- in the
# OPAQUE bucket, AND put one 328,733-byte PDF in the SPECIFIED bucket under the
# name `plain text, Shift-JIS`. That is the THIRD appearance of this table's
# defect and the FIRST in which it produced a confident wrong answer rather
# than a silence, which is a different and worse failure.
#
# THE ORDERING RULE, which is the actual repair:
#
#   every binary signature is tested before every text codec.
#
# A single-byte-per-char text codec cannot fail on arbitrary bytes, and a
# multi-byte one fails only on illegal sequences -- and a PDF header is 512
# bytes of ASCII punctuation that cp932 accepts without one. So a text probe
# placed above a binary signature does not merely miss: it CLAIMS. The rule is
# enforced by `_ordering_ok()` below and asserted in the selftest, so that a
# future edit that appends a magic after the text probes fails loudly.

def _sfnt(b):
    """A TrueType/OpenType font.

    `00 01 00 00` is sfnt version 1.0. THE HAZARD IS ONE BYTE AWAY: a Windows
    icon begins `00 00 01 00`, which is already in this table, and a careless
    probe swaps them. Both orderings are asserted in the selftest.
    """
    return (b.startswith(b"\x00\x01\x00\x00")
            or b.startswith(b"OTTO")
            or b.startswith(b"true")
            or b.startswith(b"ttcf"))


def _bmp(b):
    """A Windows bitmap.

    `BM` alone is two ASCII letters and would claim any text file beginning
    'BMW'. The header carries its own file size at offset 2 as a little-endian
    u32 and a reserved u32 of zero at offset 6; requiring the reserved field to
    be zero and the declared size to be at least the 14-byte file header makes
    the signature six bytes instead of two.
    """
    if not b.startswith(b"BM") or len(b) < 14:
        return False
    size = int.from_bytes(b[2:6], "little")
    reserved = int.from_bytes(b[6:10], "little")
    return reserved == 0 and size >= 14


def _pdf(b):
    return b.startswith(b"%PDF-")


def _zip(b):
    # PKWARE APPNOTE: local file header, central directory, or empty archive.
    return (b.startswith(b"PK\x03\x04")
            or b.startswith(b"PK\x05\x06")
            or b.startswith(b"PK\x07\x08"))


def _mpeg_audio(b):
    """MPEG-1/2 Audio, with or without an ID3v2 tag in front of it.

    An ID3v2 tag is a published container (`ID3`, a version byte below 0xFF,
    flags, and a syncsafe size whose four bytes each have bit 7 clear). A bare
    stream begins with a frame header whose first eleven bits are set. Eleven
    set bits alone occur once every 2,048 random bytes, so the probe checks the
    four fields that CANNOT hold their reserved value in a real frame: version
    01, layer 00, bitrate index 1111 and sampling rate 11 are all illegal.
    """
    if b.startswith(b"ID3") and len(b) >= 10:
        if b[3] == 0xFF or b[4] == 0xFF:
            return False
        return all(x < 0x80 for x in b[6:10])
    if len(b) >= 4 and b[0] == 0xFF and (b[1] & 0xE0) == 0xE0:
        version = (b[1] >> 3) & 0x03
        layer = (b[1] >> 1) & 0x03
        bitrate = (b[2] >> 4) & 0x0F
        rate = (b[2] >> 2) & 0x03
        return version != 1 and layer != 0 and bitrate not in (0, 15) and rate != 3
    return False


def _codec_text(codec, need_high=True):
    """A text probe for one multi-byte codec, built the same way `_cp932_text`
    is built and for the same reason: the test is that the codec REFUSES other
    things.

    WHAT THIS PROBE CANNOT NOTICE, named in advance per P19: **a codec
    accepting a file is not proof the file is in that codec.** EUC-JP and cp932
    overlap -- EUC-JP's lead bytes 0xA1..0xFE are cp932's single-byte
    half-width katakana -- so a EUC-JP document decodes under cp932 without one
    illegal sequence, into nonsense. No probe of this shape can tell them
    apart, and the order of the three text codecs in MAGICS is therefore a
    DECISION and not a measurement. `coverage.py ambiguity --root R` counts how
    many files more than one codec accepts, so that the decision's cost is a
    published number rather than a hidden one.
    """
    def probe(b):
        if not b:
            return False
        if need_high and not any(x >= 0x80 for x in b):
            return False
        try:
            s = b.decode(codec)
        except UnicodeDecodeError as e:
            if e.start < len(b) - 5:
                return False
            try:
                s = b[:e.start].decode(codec)
            except UnicodeDecodeError:
                return False
        if not s:
            return False
        # THE ONE-CHARACTER DEFECT, repaired on pc-rpgmakermv-doc.
        # U+FEFF is a byte-order mark, `'﻿'.isprintable()` is False, and
        # a UTF-8 file carrying one therefore failed this probe on its first
        # character. On that object it filed 190 files and 1,108,362 bytes as
        # OPAQUE and 0 of 190 got through, so the failure was total for that
        # population rather than partial. A leading byte-order mark is a
        # signature and not a character: it is removed before the text is
        # judged, and a U+FEFF anywhere else still counts against the file.
        if s[:1] == "﻿":
            s = s[1:]
        if not s:
            return False
        return all(c.isprintable() or c in "\t\r\n　" for c in s)
    return probe


_utf8_text = _codec_text("utf-8")
_eucjp_text = _codec_text("euc_jp")


# ---------------------------------------------------------------------------
# Five magics added on pc-rpgmakermv-doc. Four of the five are for formats no
# object in this collection had produced in seventy-nine objects -- MPEG-4
# audio, ELF, Mach-O and the Unix archive -- and together with the fifth they
# were 875,590,414 bytes of the OPAQUE bucket while the tool closed at residue
# 0 and printed a full table. Third appearance of that shape of defect.
# ---------------------------------------------------------------------------

def _mp4(b):
    """ISO/IEC 14496-12: a big-endian box size, then the four bytes `ftyp`.

    Four letters at offset 4 is a weaker signature than any other entry in this
    table, so the size word in front of them is checked too. A File Type Box
    carries a major brand, a minor version and at least one compatible brand,
    which is 16 bytes at the very least, and no File Type Box in the wild is a
    kilobyte long.
    """
    if len(b) < 12 or b[4:8] != b"ftyp":
        return False
    size = int.from_bytes(b[:4], "big")
    return 16 <= size <= 1024


def _elf(b):
    """The System V ABI's `e_ident`: the magic, then class, data and version.

    Reading three bytes past the magic costs nothing and refuses a file that
    merely opens with 7F 45 4C 46: EI_CLASS is 1 or 2, EI_DATA is 1 or 2, and
    EI_VERSION has been 1 since the standard was written.
    """
    return (len(b) >= 7 and b[:4] == b"\x7fELF"
            and b[4] in (1, 2) and b[5] in (1, 2) and b[6] == 1)


_MACHO_THIN = (b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe",
               b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe")
_MACHO_FAT = (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca")


def _macho(b):
    """Mach-O, in its four thin forms and its two fat ones.

    THE ONE-BYTE HAZARD OF THIS OBJECT, and it is a four-byte one: the
    universal binary's magic **0xCAFEBABE is also a Java class file's**. They
    are separated by the next four bytes and by nothing else. Mach-O puts
    `nfat_arch` there -- the number of architectures in the archive, which is
    one or two in practice and has never been twenty. A class file puts
    `minor_version` then `major_version`, read together as a big-endian word;
    `major_version` has been at least 45 since Java 1.0 in 1996, so the
    smallest class file value is 45 and the ranges do not touch.

    A tool that filed a Java class file as a Mach-O executable would be wrong
    in a way that no byte count would reveal, which is why this is a check and
    not a comment.
    """
    if len(b) < 8:
        return False
    if b[:4] in _MACHO_THIN:
        return True
    if b[:4] in _MACHO_FAT:
        order = "big" if b[0] == 0xCA else "little"
        return 1 <= int.from_bytes(b[4:8], order) <= 20
    return False


def _ar(b):
    """The Unix archive, POSIX.1-2017 and SVR4, unchanged since 1978."""
    return b.startswith(b"!<arch>\n")


def _chromium_pak(b):
    """Chromium's `.pak` resource container, checked by its own arithmetic.

    The whole signature is a small integer in the first four bytes, which on
    its own would match a great many files. What makes it a signature is that
    the header declares how many entries follow and the entry table's first
    offset must therefore be exactly where the header ends:

        v4   9 + (resources + 1) * 6
        v5  12 + (resources + 1) * 6 + aliases * 4

    Both layouts end with a sentinel entry, which is where the `+ 1` comes
    from, and both index tables are (u16 id, u32 offset). On this object that
    equation holds on 222 of 222 files, so the probe is a structural check and
    not a four-byte guess.

    The bucket is DECODED and the argument is in docs/04: the format is read by
    published source and by several independent third-party implementations,
    and no specification of it exists.
    """
    if len(b) < 20:
        return False
    ver = int.from_bytes(b[:4], "little")
    if ver == 5:
        if b[4] != 1 or b[5:8] != b"\x00\x00\x00":
            return False
        nres = int.from_bytes(b[8:10], "little")
        nali = int.from_bytes(b[10:12], "little")
        if nres == 0:
            return False
        return int.from_bytes(b[14:18], "little") == 12 + (nres + 1) * 6 \
            + nali * 4
    if ver == 4:
        nres = int.from_bytes(b[4:8], "little")
        if b[8] != 1 or nres == 0 or nres > (1 << 20):
            return False
        return int.from_bytes(b[11:15], "little") == 9 + (nres + 1) * 6
    return False


# One magic added on pc-ilgrandegiocoditangentopoli-doc, where its absence put
# 413,058 bytes -- 89.5389 % of the object, the largest opaque share this
# table has ever left standing as a fraction -- in the OPAQUE bucket while the
# tool closed at residue 0 and printed a full table. Fourth appearance of that
# shape of defect, and the first one where the missing format had no
# specification, no vendor and no name outside this repository.
# ---------------------------------------------------------------------------

def _px(b):
    """The `PX` screen format of *Il grande gioco di Tangentopoli*.

    Two letters would be a guess: `PX` turns up by chance in a few kilobytes.
    What makes this a signature is that the geometry is stated TWICE, once in
    the raw header and once inside the compressed stream, and the probe
    decodes far enough to compare them.

        +0   2B   'PX'
        +2   u16  width          +4   u16  height
        +6   ...  a run-length stream, `FF <count> <byte>` or a literal,
                  whose first ten decoded bytes are five little-endian words
                  and whose fourth and fifth words repeat width and height

    Reading ten bytes out of the stream costs nothing and refuses a file whose
    first two bytes happen to spell `PX`. The format has no published
    description, no vendor and no named producer, so the bucket is DECODED and
    the argument for it is in docs/03 -- the DECODED test asks whether the
    PRODUCER published a description, and this object has no producer who
    could have.
    """
    if len(b) < 32 or b[:2] != b"PX":
        return False
    width = b[2] | (b[3] << 8)
    height = b[4] | (b[5] << 8)
    if not (0 < width <= 4096 and 0 < height <= 4096):
        return False
    out = bytearray()
    pos = 6
    while pos < len(b) and len(out) < 10:
        if b[pos] == 0xFF:
            if pos + 2 >= len(b):
                return False
            out.extend(bytes([b[pos + 2]]) * b[pos + 1])
            pos += 3
        else:
            out.append(b[pos])
            pos += 1
    if len(out) < 10:
        return False
    return (out[6] | (out[7] << 8)) == width and \
           (out[8] | (out[9] << 8)) == height


def _ilbm(b):
    """EA IFF 85 / ILBM, and the signature is a STRUCTURE and not four letters.

    `FORM` on its own is a four-byte string that occurs by accident, so what
    is checked here is the whole opening grammar: `FORM`, a big-endian length,
    a known form type, and then a first chunk whose own length fits inside
    that length. Electronic Arts published this in January 1985 and there have
    been independent readers of it for thirty years, so the bucket is
    SPECIFIED -- which is the exact opposite of the `_px` argument three
    entries below, where the format had no vendor who could have published
    anything. `tools/ilbm.py` is this repository's reader.
    """
    if len(b) < 20 or b[:4] != b"FORM":
        return False
    if b[8:12] not in (b"ILBM", b"PBM "):
        return False
    declared = int.from_bytes(b[4:8], "big")
    if declared < 12 or declared > (1 << 31):
        return False
    first = int.from_bytes(b[16:20], "big")
    return 8 <= first + 8 <= declared


def _carte40(b):
    """`CARTE.IMG`: forty Italian cards, four planes of 64 x 101, plane-major.

    THIS ENTRY HAS NO MAGIC NUMBER AND SAYS SO. The file has no header of any
    kind, so what is tested is the SHAPE of its first plane: eight-byte rows,
    a blank first row, and then five rows each of which is one contiguous run
    of set bits whose left edge only moves left and whose right edge only
    moves right. That is the top edge of a rounded rectangle 64 pixels
    across, which is what the top of a playing card looks like from inside.

    The bucket is **DERIVED**, which is the weakest of the three and the right
    one: there is no vendor, no document and no producer -- so SPECIFIED is
    out and so is DECODED, whose test asks whether the producer published a
    description -- and the only warrant this file has is this session's own
    reader, `tools/carte.py`, whose argument is that 129,280 divides by forty
    at residue zero and that the pictures that come out are a Neapolitan deck.

    `--selftest` requires this to REFUSE every other file in the object,
    because a shape test that fires on a palette is worth nothing.
    """
    if len(b) < 48:
        return False
    rows = [b[i * 8:(i + 1) * 8] for i in range(6)]
    if any(byte for byte in rows[0]):
        return False
    left = right = None
    for row in rows[1:]:
        bits = "".join(format(byte, "08b") for byte in row)
        one = bits.find("1")
        if one < 0:
            return False
        last = bits.rfind("1")
        if "0" in bits[one:last]:       # not a single contiguous run
            return False
        if left is not None and (one > left or last < right):
            return False
        left, right = one, last
    return right - left + 1 >= 56


MAGICS = [
    (_mz, "specified", "PE / MZ executable (Microsoft) -- header arithmetic checked, not the two letters alone"),
    (_ilbm, "specified", "EA IFF 85 / ILBM (Electronic Arts, published 1985)"),
    (_carte40, "derived",
     "40-card planar sheet -- NO signature; selected by the shape of its "
     "first card and read only by this session"),
    (_px, "decoded",
     "PX 320x200 screen -- no specification, no vendor, no named producer; "
     "read on this object"),
    (_is(b"\x89PNG\r\n\x1a\n"), "specified", "PNG (W3C / ISO 15948)"),
    (lambda b: b.startswith(b"RIFF") and b[8:12] == b"WAVE",
     "specified", "RIFF WAVE (Microsoft and IBM)"),
    (_is(b"MThd"), "specified", "Standard MIDI File (MMA RP-001)"),
    (_is(b"\x00\x00\x01\x00"), "specified", "Windows icon"),
    (_is(b"ITSF"), "decoded",
     "Microsoft ITSF -- no vendor specification; chmlib and 7-Zip"),
    (lambda b: b[:1] == b"\x0b" and b[1:12] == b"LcfDataBase",
     "decoded", "LCF database -- no vendor specification; the EasyRPG project"),
    # Three magics added on pc-rpgmaker2003-doc, where their absence put
    # 67,623 bytes in the OPAQUE bucket and the tool still closed at residue 0
    # and printed a full table. A classifier that is silently wrong is worse
    # than one that refuses, so these are here with the same length-prefixed
    # shape as LcfDataBase above and not a substring search.
    (lambda b: b[:1] == b"\x0a" and b[1:11] == b"LcfMapUnit",
     "decoded", "LCF map unit -- no vendor specification; the EasyRPG project"),
    (lambda b: b[:1] == b"\x0a" and b[1:11] == b"LcfMapTree",
     "decoded", "LCF map tree -- no vendor specification; the EasyRPG project"),
    (_is(b"8BPS"), "specified", "Adobe Photoshop PSD (Adobe, published)"),
    # Three magics added on pc-rpgmakerxp-doc, where their absence put
    # 10,966,146 bytes -- 40.7430 % of the object -- in the OPAQUE bucket while
    # the tool closed at residue 0 and printed a full table. Second appearance
    # of that defect and 162 times the first. Two of the three are for formats
    # this box has had readers for since long before the object arrived
    # (`oggmeta.py`, `jpeg.py`): the gap was in this table and nowhere else.
    (_ogg, "specified", "Ogg container (IETF RFC 3533; Vorbis I by Xiph.Org)"),
    (_is(b"\xff\xd8\xff"), "specified",
     "JPEG / JFIF (ITU-T T.81; ISO/IEC 10918)"),
    # The bucket is argued in docs/04 and not chosen here: Ruby publishes a
    # description of this format in its own source tree (doc/marshal.rdoc), and
    # the DECODED bucket's membership test begins "no such document exists".
    # The RGSS object model the format CARRIES is a separate question with a
    # separate answer, exactly as a PNG's subject matter is separate from PNG.
    (_marshal48, "specified",
     "Ruby Marshal 4.8 object serialisation (Ruby, doc/marshal.rdoc)"),
    # Five binary magics added on pc-rpgmakervxace-doc. Every one of these
    # formats is published, and two of them (ZIP, BMP) already had readers in
    # this box -- `zaccount.py` and `bmp.py` -- while the table that decides
    # what is readable had not been told. That is the gap, and it is in this
    # list and nowhere else.
    (_mpeg_audio, "specified",
     "MPEG-1/2 Audio (ISO/IEC 11172-3); ID3v2 tag (id3.org)"),
    (_sfnt, "specified",
     "sfnt / TrueType outline font (Apple; Microsoft OpenType)"),
    (_bmp, "specified", "Windows BMP (Microsoft, published)"),
    (_pdf, "specified", "PDF (ISO 32000; Adobe)"),
    (_zip, "specified", "ZIP archive (PKWARE APPNOTE)"),
    # Five magics added on pc-rpgmakermv-doc. Four of the formats had never
    # appeared in this collection; the fifth is the first DECODED candidate
    # since pc-rpgmaker2003-doc and its bucket is argued in docs/04.
    (_mp4, "specified",
     "MPEG-4 / ISO base media (ISO/IEC 14496-12; 14496-14 for M4A)"),
    (_elf, "specified", "ELF (System V ABI / Tool Interface Standard 1.2)"),
    (_macho, "specified", "Mach-O (Apple, OS X ABI Mach-O File Format)"),
    (_ar, "specified", "Unix archive (POSIX.1-2017 ar; SVR4 variant)"),
    (_chromium_pak, "decoded",
     "Chromium .pak resource container -- no specification; the Chromium "
     "source and third-party readers"),
    # Added on pc-hexxagon-doc, where its absence put 626,424 bytes --
    # 48.2668 % of the object -- in the OPAQUE bucket. The bucket is DERIVED
    # and the argument is in `_hxg`'s docstring and in docs/04: the producer
    # wrote three paragraphs about his own compressor in the user manual, and
    # prose is not a specification.
    (_hxg, "derived",
     "HXG resource container (Argo Games, 1993) -- NO signature and no "
     "published description; selected by three arithmetic closures and read "
     "only by this session"),
    (_hxg_board, "derived",
     "HEXXAGON board -- 169 ten-byte cells of which 108 are off-board "
     "sentinels, leaving the 61 hexes of the game; written by the program"),
    (_hxg_config, "derived",
     "HEXXAGON settings -- 22 bytes bracketed by HXG\\0 at both ends; "
     "written by the program"),
    (_pif, "specified",
     "Windows 3.x Program Information File (Microsoft; layout cited from "
     "pc-baronbaldric-doc/docs/04, not re-established here)"),
    # Added on pc-bianconatale-doc, where their absence put 1,366,363 bytes
    # -- 95.1162 % of the object, the lowest opening figure this collection
    # has measured -- in the OPAQUE bucket. Both are DERIVED, both are
    # arithmetic and not a signature, and both ask for the file's length
    # because their closure is what selects them and a head cannot see it.
    (_bmb, "derived",
     "Tecnoart .BMB image / .BMA frame strip (BIANCO NATALE, 1994) -- NO "
     "signature and no published description; 5- or 7-byte header, raw "
     "8-bit pixels, optional 6-bit VGA palette, closing on the length; "
     "read only by this session"),
    (_fnt, "derived",
     "Tecnoart 8 x 12 font, 96 cells at one byte per pixel (BIANCO NATALE, "
     "1994) -- no signature; read only by this session"),
    # Added on pc-outrun-doc: 93 files, 306,825 bytes, 51.2416 % of that
    # object, two compression stages deep. The probe reads the outer header
    # and the Huffman table; the closure is pes.py's.
    (_pes, "derived",
     "OUT RUN .PES/.PCS shape container (SEGA / Unlimited Software Inc., "
     "1989) -- packed bit, stage count, canonical Huffman table with Kraft "
     "sum 1; two-stage grammar read from the game's own decoder by pes.py"),
    # Added on pc-demonsforge-doc: one file, 164,352 bytes, 72.6768 % of that
    # object -- a 160 KB self-booting diskette behind Mok's signature sector.
    # The probe closes the directory chain; forgedat.py decodes the pictures.
    (_forgedat, "derived",
     "THE DEMON'S FORGE GAME.DAT (Mastertronic, 1987; Dos Driver by Mok) -- "
     "signature sector, boot sector, 12-byte directory records chaining "
     "a*512+c to a zero terminator; vector-picture grammar read from the "
     "game's own interpreter by forgedat.py"),
    # Added on pc-teenagent-doc: twelve files, 15,309,492 bytes, 16.4292 % of
    # that object. The probe closes the directory on the length; res.py reads
    # the members (screens, sprites, overlays, animations, fonts, music
    # headers, drivers) with the grammar read from the unpacked engine.
    (_res, "derived",
     "TEENAGENT .RES container (Metropolis Software House, 1994-1995) -- "
     "u32 count, count+1 monotonic offsets, first 4+4(count+1), last = the "
     "length; member grammars read from the game's own engine by res.py"),
    # ------------------------------------------------------------------
    # EVERYTHING BELOW THIS LINE IS A TEXT CODEC AND NOTHING BINARY MAY BE
    # ADDED AFTER IT. `_ordering_ok()` enforces this and the selftest asserts
    # it. The 328,733-byte PDF that this table filed as `plain text, Shift-JIS`
    # is what the rule is made of.
    # ------------------------------------------------------------------
    (_printable, "specified", "plain text, ASCII"),
    # This must stand BEFORE _cp932_text and does: cp437's box-drawing band
    # 0xB0..0xDF sits inside Shift-JIS's single-byte half-width katakana range
    # 0xA1..0xDF, both decodes are legal, and the file that provoked this is
    # an English BBS advertisement filed as Japanese. See `_cp437_art`.
    (_cp437_art, "specified",
     "plain text, cp437 with box-drawing art (IBM PC codepage 437)"),
    (_utf8_text, "specified", "plain text, UTF-8 (Unicode; IETF RFC 3629)"),
    (_eucjp_text, "specified",
     "plain text, EUC-JP (JIS X 0208; Unix Japanese encoding)"),
    (_cp932_text, "specified",
     "plain text, Shift-JIS (JIS X 0208; Microsoft cp932)"),
]

# The probes that are text codecs, by identity. Anything not in this set is a
# binary signature and must sort before all of them.
TEXT_PROBES = (_printable, _cp437_art, _utf8_text, _eucjp_text, _cp932_text)


def _ordering_ok(magics=None):
    """Every binary signature is tested before every text codec.

    Returns True when the rule holds. This is not decoration: the whole repair
    of the misfiled PDF is that a signature which was absent is now present AND
    is tested first. A future edit that appends `(_is(b"CAFEBABE"), ...)` to
    the end of MAGICS would be silently shadowed by three text probes, and this
    is the check that refuses to let that happen quietly.
    """
    seen_text = False
    for probe, _buck, _name in (magics if magics is not None else MAGICS):
        if probe in TEXT_PROBES:
            seen_text = True
        elif seen_text:
            return False
    return True


# How much of a file the classifier looks at.
#
# This was 512 and is 4,096, and the reason is a class of magic 512 cannot
# serve. Some formats close on their own LENGTH -- HEXXAGON's board file is
# 1,690 bytes of 169 records and a file of 1,700 is not one -- and a probe
# handed a fixed-size head cannot tell 1,690 bytes from the first 1,690 bytes
# of something longer. Reading MORE than the format's size settles it for
# free: ask for 4,096 and get 1,690 back, and the file is 1,690 bytes.
#
# It costs eight times the bytes per file and buys the length closures. It
# does not help formats larger than the head -- `_hxg` documents the weaker
# warrant it has to live with -- and raising it further would only move the
# same line.
#
# THE LENGTH, AS A SECOND CHANNEL. Added on pc-bianconatale-doc, where a
# 64,777-byte `.BMB` closes on its length and nothing in a 4,096-byte head
# can see that. A probe marked `wants_size = True` is called as
# `probe(head, size)` with the file's length; every other probe is called as
# before, with the head alone, and `classify(blob)` with no length still
# works for every caller that has it (`chpak.py` is one). The length is not
# the head, it is a property of the file, and a probe that uses it says so in
# its docstring together with what it still cannot see. Nothing was removed.
HEAD = 4096


def classify(blob, size=None):
    for probe, buck, name in MAGICS:
        try:
            if getattr(probe, "wants_size", False):
                hit = probe(blob, size)
            else:
                hit = probe(blob)
            if hit:
                return buck, name
        except (IndexError, TypeError):
            continue
    return "opaque", "not identified by any signature this tool knows"


def tree_rows(root):
    rows = []
    for dp, dn, fn in os.walk(root):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                head = fh.read(HEAD)
            size = os.path.getsize(p)
            buck, name = classify(head, size)
            rows.append((os.path.relpath(p, root).replace(os.sep, "/"),
                         size, buck, name))
    if not rows:
        sys.exit("coverage: no files under %r -- refusing to report a clean "
                 "table over an empty population" % root)
    return rows


def report_tree(root):
    rows = tree_rows(root)
    total = sum(r[1] for r in rows)
    cnt = collections.Counter()
    byt = collections.Counter()
    for _, size, buck, name in rows:
        cnt[(buck, name)] += 1
        byt[(buck, name)] += size
    print("denominator : %d files, %d bytes -- every file under %s, "
          "classified BY MAGIC" % (len(rows), total, root))
    print()
    print("  %-10s %6s %12s %10s  %s"
          % ("bucket", "files", "bytes", "share", "format"))
    order = {"specified": 0, "decoded": 1, "derived": 2, "opaque": 3}
    for (buck, name), c in sorted(cnt.items(),
                                  key=lambda kv: (order[kv[0][0]],
                                                  -byt[kv[0]])):
        print("  %-10s %6d %12d %9.4f %%  %s"
              % (buck, c, byt[(buck, name)],
                 100.0 * byt[(buck, name)] / total, name))
    print()
    sums = collections.Counter()
    counts = collections.Counter()
    for (buck, name), c in cnt.items():
        sums[buck] += byt[(buck, name)]
        counts[buck] += c
    for b in ("specified", "decoded", "derived", "opaque"):
        print("  %-10s %4d files %12d bytes   %8.4f %% of %d"
              % (b, counts[b], sums[b], 100.0 * sums[b] / total if total else 0,
                 total))
    print("  %-10s %4d files %12d bytes   %8.4f %%"
          % ("SUM", sum(counts.values()), sum(sums.values()),
             100.0 * sum(sums.values()) / total))
    print("  against the denominator %d          RESIDUE %d"
          % (total, sum(sums.values()) - total))
    print()
    print("  The SUM row is an ACCOUNTING figure and not a coverage figure.")
    print("  It answers 'do the bytes add up to the object'. It does not")
    print("  answer 'how much of this can be checked against something outside")
    print("  it', because SPECIFIED and DECODED carry warrants of different")
    print("  strength and DERIVED carries none but this session's.")
    if sum(sums.values()) != total:
        print("  THE BUCKETS DO NOT SUM TO THE DENOMINATOR", file=sys.stderr)
        return 1
    return 0


def selftest():
    checks = []
    checks.append(("every extension falls in exactly one bucket",
                   len(set(PUBLISHED) & set(DERIVED)) == 0
                   and len(set(PUBLISHED) & set(NEITHER)) == 0
                   and len(set(DERIVED) & set(NEITHER)) == 0, ""))
    checks.append(("an unknown extension is not counted as published",
                   bucket("QQQ")[0] == "neither", str(bucket("QQQ"))))
    checks.append(("INS is derived at the member layer and neither at the "
                   "product layer",
                   bucket("INS")[0] == "derived"
                   and bucket("INS", "product")[0] == "neither", ""))
    checks.append(("a name with a path separator takes the last component",
                   ext_of("themes\\global\\a.BMP") == "BMP", ""))
    checks.append(("a dotfile is not given an extension",
                   ext_of(".profile") == "(none)", ext_of(".profile")))
    checks.append(("a name with no dot is not given an extension",
                   ext_of("README") == "(none)", ""))
    checks.append(("HLP is NOT counted as published",
                   bucket("HLP")[0] == "neither", ""))
    checks.append(("the Z archive is derived and not published",
                   bucket("1")[0] == "derived", ""))
    # -- ILBM and the 40-card sheet, added on pc-rovescino-doc --------------
    _bmhd = bytes(20)
    _ilbm_head = (b"FORM" + (100).to_bytes(4, "big") + b"ILBM"
                  + b"BMHD" + (20).to_bytes(4, "big") + _bmhd)
    checks.append(("an ILBM is SPECIFIED",
                   classify(_ilbm_head)[0] == "specified", ""))
    checks.append(("a PBM  is SPECIFIED too",
                   classify(_ilbm_head.replace(b"ILBM", b"PBM ", 1))[0]
                   == "specified", ""))
    checks.append(("FORM with an unknown type is NOT an ILBM",
                   classify(b"FORM" + (100).to_bytes(4, "big") + b"AIFF"
                            + bytes(20))[0] != "specified"
                   or "ILBM" not in classify(
                       b"FORM" + (100).to_bytes(4, "big") + b"AIFF"
                       + bytes(20))[1], ""))
    checks.append(("the word FORM in the middle of a file is not an ILBM",
                   not _ilbm(b"xxFORM" + (100).to_bytes(4, "big") + b"ILBM"
                             + bytes(20)), ""))
    # The 40-card shape test: the real top edge, then five refusals built to
    # look like near misses. A shape test that cannot say no is not a test.
    _card = (bytes(8)
             + bytes.fromhex("0fffffffffffffe0")
             + bytes.fromhex("3ffffffffffffff8")
             + bytes.fromhex("3ffffffffffffff8")
             + bytes.fromhex("7ffffffffffffffc")
             + bytes.fromhex("7ffffffffffffffc"))
    checks.append(("the top edge of a card is DERIVED",
                   classify(_card)[0] == "derived", ""))
    checks.append(("a card whose first row is not blank is refused",
                   not _carte40(b"\x01" + _card[1:]), ""))
    checks.append(("a band that NARROWS is refused",
                   not _carte40(bytes(8)
                                + bytes.fromhex("7ffffffffffffffc")
                                + bytes.fromhex("3ffffffffffffff8")
                                + bytes.fromhex("3ffffffffffffff8")
                                + bytes.fromhex("0fffffffffffffe0")
                                + bytes.fromhex("0fffffffffffffe0")), ""))
    checks.append(("a row with a hole in it is refused",
                   not _carte40(bytes(8)
                                + bytes.fromhex("0ffffff00fffffe0")[:8]
                                + _card[16:]), ""))
    checks.append(("forty-eight zero bytes are refused",
                   not _carte40(bytes(48)), ""))
    checks.append(("a narrow band is refused",
                   not _carte40(bytes(8) + bytes.fromhex("0000ff0000000000")
                                * 5), ""))
    # The four-bucket classifier, which is new and is the point of `tree`.
    # An MZ header whose arithmetic holds: 144 bytes in the last page, one
    # page, no relocations, a 32-byte header, relocation table at 0x1c.
    _mz_head = (b"MZ" + struct.pack("<13H", 144, 1, 0, 2, 0, 0xffff, 0, 0x80,
                                    0, 0, 0, 0x1c, 0) + bytes(36))
    checks.append(("an MZ header whose arithmetic holds is SPECIFIED",
                   classify(_mz_head)[0] == "specified", ""))
    checks.append(("an MZP stub is SPECIFIED too: the P is e_cblp's low byte",
                   classify(b"MZP\x00" + _mz_head[4:])[0] == "specified", ""))
    # The repair made on pc-outrun-doc: the letters alone no longer fire.
    checks.append(("MZ followed by prose is OPAQUE: two letters are not a header",
                   classify(b"MZ is also two letters, and this is a sentence "
                            b"that begins with them" + bytes(20))[0]
                   == "opaque", ""))
    checks.append(("an MZ header declaring more image than the file has is "
                   "OPAQUE", classify(_mz_head, 100)[0] == "opaque", ""))
    checks.append(("an MZ header whose relocation table overruns its header "
                   "is OPAQUE",
                   classify(b"MZ" + struct.pack("<13H", 144, 1, 9, 2, 0, 0xffff,
                                                 0, 0x80, 0, 0, 0, 0x1c, 0)
                            + bytes(36))[0] == "opaque", ""))
    checks.append(("the MZ header of OUTRUN.EXE, quoted, is SPECIFIED at its "
                   "length 17,832",
                   classify(bytes.fromhex("4d5ab0001b00010020000000ffff2303"
                                          "8000000000000000220000000100fb20")
                            + bytes(32), 17832)[0] == "specified", ""))
    checks.append(("the MZ header of CORV.PES, quoted, is SPECIFIED at its "
                   "length 75,747: the classifier was right about it",
                   classify(bytes.fromhex("4d5ae30194000000" "2200e504e504b715"
                                          "800000001200e811" "1e00000001000000")
                            + bytes(32), 75747)[0] == "specified", ""))
    checks.append(("a PNG is SPECIFIED",
                   classify(b"\x89PNG\r\n\x1a\n" + bytes(20))[0]
                   == "specified", ""))
    checks.append(("a RIFF that is not WAVE is not counted as WAVE",
                   classify(b"RIFF\x00\x00\x00\x00AVI ")[1]
                   != "RIFF WAVE (Microsoft and IBM)", ""))
    checks.append(("a RIFF WAVE is SPECIFIED",
                   classify(b"RIFF\x00\x00\x00\x00WAVEfmt ")[0]
                   == "specified", ""))
    checks.append(("an ITSF container is DECODED, not specified",
                   classify(b"ITSF\x03\x00\x00\x00" + bytes(40))[0]
                   == "decoded", ""))
    checks.append(("an LCF database is DECODED, not specified",
                   classify(b"\x0bLcfDataBase\x0b\xae\x11")[0]
                   == "decoded", ""))
    checks.append(("a file merely CONTAINING LcfDataBase is not one",
                   classify(b"xxxx\x0bLcfDataBase")[0] != "decoded", ""))
    checks.append(("an LcfMapUnit is DECODED",
                   classify(b"\x0aLcfMapUnit\x01\x01\x04")[0]
                   == "decoded", ""))
    checks.append(("an LcfMapTree is DECODED",
                   classify(b"\x0aLcfMapTree\x04\x00\x01")[0]
                   == "decoded", ""))
    checks.append(("the two map variants are told apart",
                   classify(b"\x0aLcfMapUnit\x01")[1]
                   != classify(b"\x0aLcfMapTree\x04")[1], ""))
    checks.append(("a wrong length prefix on LcfMapUnit is not one",
                   classify(b"\x0bLcfMapUnit\x01")[0] != "decoded", ""))
    checks.append(("a PSD is SPECIFIED, because Adobe published the format",
                   classify(b"8BPS\x00\x01" + bytes(20))[0]
                   == "specified", ""))
    checks.append(("a PSD is named as Adobe's",
                   "Adobe" in classify(b"8BPS\x00\x01" + bytes(20))[1], ""))
    # The three magics added on pc-rpgmakerxp-doc. Two of these checks MUST
    # fail on their fixtures, because a magic that cannot say no is not a
    # magic: the first version of the Marshal probe was two bytes long and
    # would have accepted any file at all that happened to begin 04 08.
    checks.append(("an Ogg page is SPECIFIED",
                   classify(b"OggS\x00\x02" + bytes(20))[0] == "specified",
                   ""))
    checks.append(("an Ogg is named as the IETF's and Xiph.Org's",
                   "RFC 3533" in classify(b"OggS\x00\x02" + bytes(20))[1],
                   ""))
    checks.append(("a file merely CONTAINING OggS is not an Ogg",
                   classify(b"xxxxOggS\x00\x02")[0] != "specified"
                   or "Ogg" not in classify(b"xxxxOggS\x00\x02")[1], ""))
    checks.append(("OggS with a non-zero version byte is not an Ogg",
                   "Ogg" not in classify(b"OggS\x09\x02" + bytes(20))[1], ""))
    checks.append(("a JPEG is SPECIFIED",
                   classify(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")[0]
                   == "specified", ""))
    checks.append(("a JPEG is named as ITU-T T.81 / ISO 10918",
                   "T.81" in classify(b"\xff\xd8\xff\xe0")[1], ""))
    checks.append(("FF D8 without the third byte is not a JPEG",
                   "JPEG" not in classify(b"\xff\xd8\x00\x00")[1], ""))
    checks.append(("a Ruby Marshal 4.8 array is SPECIFIED",
                   classify(b"\x04\x08[\x0e")[0] == "specified", ""))
    checks.append(("a Ruby Marshal 4.8 object and hash are the same format",
                   classify(b"\x04\x08o:\x0f")[1]
                   == classify(b"\x04\x08{\x06")[1], ""))
    checks.append(("Marshal is named as Ruby's own",
                   "Ruby" in classify(b"\x04\x08[\x0e")[1], ""))
    checks.append(("04 08 followed by a byte the grammar cannot start with "
                   "is NOT Marshal",
                   "Marshal" not in classify(b"\x04\x08\x99\x01")[1], ""))
    checks.append(("a two-byte file of 04 08 is not Marshal either",
                   "Marshal" not in classify(b"\x04\x08")[1], ""))
    checks.append(("a Marshal minor other than 8 is not claimed as 4.8",
                   "Marshal" not in classify(b"\x04\x07[\x0e")[1], ""))
    checks.append(("plain text is SPECIFIED",
                   classify(b"383730\n")[0] == "specified", ""))
    checks.append(("Shift-JIS text is SPECIFIED, not opaque",
                   classify("Ｍｉｃｃｏ (Feb.3,2003)".encode("cp932"))[0]
                   == "specified", ""))
    checks.append(("and it is named as Shift-JIS rather than as ASCII",
                   "Shift-JIS" in
                   classify("Ｍｉｃｃｏ".encode("cp932"))[1], ""))
    checks.append(("a byte string cp932 REFUSES is not called text",
                   _cp932_text(bytes([0x81, 0x20, 0xFF, 0x81])) is False, ""))
    checks.append(("a head cut mid-sequence is still recognised as text",
                   _cp932_text("Ｍｉｃｃｏ".encode("cp932")[:-1]) is True, ""))
    checks.append(("but a bad sequence in the MIDDLE is not forgiven",
                   _cp932_text("Ｍ".encode("cp932") + b"\xff\xfe"
                               + "ｏｏｏ".encode("cp932")) is False, ""))
    checks.append(("pure ASCII does not reach the Shift-JIS probe",
                   _cp932_text(b"hello") is False, ""))
    # ------------------------------------------------------------------
    # The five binary magics and two text codecs added on
    # pc-rpgmakervxace-doc. Six of these twenty-two checks assert a REFUSAL or
    # a non-confusion rather than an acceptance, because the defect this
    # repairs was not a probe that said no: it was a probe that said yes.
    checks.append(("THE ORDERING RULE: every binary signature is tested "
                   "before every text codec",
                   _ordering_ok() is True, ""))
    checks.append(("and the rule is falsifiable -- a binary probe moved "
                   "below a text codec is REFUSED",
                   _ordering_ok([(_printable, "specified", "t"),
                                 (_pdf, "specified", "b")]) is False, ""))
    checks.append(("THE MISFILING: a PDF header is a PDF and not Shift-JIS "
                   "text",
                   classify(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n")[1]
                   .startswith("PDF"), ""))
    checks.append(("and the cp932 probe WOULD have taken it, which is why "
                   "the order matters",
                   _cp932_text(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\n"
                               + "Ｍ".encode("cp932")) is True, ""))
    checks.append(("an sfnt font is SPECIFIED",
                   classify(b"\x00\x01\x00\x00\x00\x0e\x00\x80")[0]
                   == "specified", ""))
    checks.append(("THE ONE-BYTE HAZARD: 00 01 00 00 is a font",
                   "sfnt" in classify(b"\x00\x01\x00\x00" + bytes(12))[1], ""))
    checks.append(("THE ONE-BYTE HAZARD: 00 00 01 00 is an icon and is NOT "
                   "called a font",
                   classify(b"\x00\x00\x01\x00" + bytes(12))[1]
                   == "Windows icon", ""))
    checks.append(("an OpenType CFF font is SPECIFIED too",
                   "sfnt" in classify(b"OTTO" + bytes(12))[1], ""))
    checks.append(("a BMP is SPECIFIED",
                   classify(b"BM\x36\x10\x00\x00\x00\x00\x00\x00\x36\x00"
                            b"\x00\x00")[0] == "specified", ""))
    checks.append(("'BMW' followed by text is NOT claimed as a BMP",
                   "BMP" not in classify(b"BMW cars are made in Munich, "
                                         b"and this is a text file.\n")[1],
                   ""))
    checks.append(("a BMP whose reserved u32 is not zero is REFUSED",
                   _bmp(b"BM\x36\x10\x00\x00\x01\x00\x00\x00\x36\x00\x00\x00")
                   is False, ""))
    checks.append(("a ZIP local header is SPECIFIED",
                   classify(b"PK\x03\x04\x14\x00\x00\x00\x08\x00")[0]
                   == "specified", ""))
    checks.append(("an empty ZIP end-of-central-directory is one too",
                   "ZIP" in classify(b"PK\x05\x06" + bytes(18))[1], ""))
    checks.append(("'PKZIP is a program' is NOT claimed as a ZIP",
                   "ZIP" not in classify(b"PKZIP is a program written by "
                                         b"Phil Katz.\n")[1], ""))
    checks.append(("an ID3v2.3 tag is MPEG audio",
                   "MPEG" in classify(b"ID3\x03\x00\x00\x00\x00\x1f\x76"
                                      + bytes(8))[1], ""))
    checks.append(("an ID3 tag whose size bytes are not syncsafe is REFUSED",
                   _mpeg_audio(b"ID3\x03\x00\x00\x00\x00\xff\x76") is False,
                   ""))
    checks.append(("a bare MPEG frame sync is MPEG audio",
                   "MPEG" in classify(b"\xff\xfb\x90\x64" + bytes(20))[1], ""))
    checks.append(("eleven set bits with an ILLEGAL layer are REFUSED",
                   _mpeg_audio(b"\xff\xe1\x90\x64") is False, ""))
    checks.append(("eleven set bits with bitrate index 1111 are REFUSED",
                   _mpeg_audio(b"\xff\xfb\xf0\x64") is False, ""))
    checks.append(("UTF-8 text with a multi-byte character is SPECIFIED",
                   classify("Grassland|草原|Prairie|Wiese|Prado\n"
                            .encode("utf-8"))[0] == "specified", ""))
    checks.append(("and it is named UTF-8 rather than Shift-JIS",
                   "UTF-8" in classify("草原|Prairie\n".encode("utf-8"))[1],
                   ""))
    checks.append(("EUC-JP text is SPECIFIED and named EUC-JP",
                   "EUC-JP" in classify("日本語のテキストです。\n"
                                        .encode("euc_jp"))[1], ""))
    checks.append(("a byte string UTF-8 refuses is not called UTF-8",
                   _utf8_text(bytes([0xC3, 0x28, 0xA0, 0xA1])) is False, ""))
    checks.append(("pure ASCII does not reach the UTF-8 probe",
                   _utf8_text(b"hello") is False, ""))
    # --- the byte-order-mark repair, pc-rpgmakermv-doc -------------------
    # Two checks, and the first one FAILS without the one-line repair. That is
    # the whole point: the defect was invisible because nothing asserted the
    # negative. `'﻿'.isprintable()` is False and the probe demanded that
    # every character be printable.
    _bom = "﻿".encode("utf-8")
    checks.append(("U+FEFF is not printable, which is what caused the defect",
                   "﻿".isprintable() is False, ""))
    checks.append(("THE REPAIR: UTF-8 text WITH a byte-order mark is "
                   "SPECIFIED", classify(_bom + "草原|Prairie\n"
                                         .encode("utf-8"))[0] == "specified",
                   "0 of 190 got through before this"))
    checks.append(("and it is still named UTF-8",
                   "UTF-8" in classify(_bom + "草原|Prairie\n"
                                       .encode("utf-8"))[1], ""))
    checks.append(("a BOM followed by ASCII is UTF-8 and not ASCII, because "
                   "the mark is a high byte",
                   classify(_bom + b"hello world\n")[1]
                   == "plain text, UTF-8 (Unicode; IETF RFC 3629)", ""))
    checks.append(("the same text WITHOUT a mark is still accepted",
                   classify("草原|Prairie\n".encode("utf-8"))[0]
                   == "specified", ""))
    checks.append(("a BOM followed by BINARY is still refused -- the repair "
                   "strips a signature, it does not excuse a file",
                   _utf8_text(_bom + bytes([0, 1, 2, 3, 27, 200])) is False,
                   ""))
    checks.append(("a lone byte-order mark and nothing else is NOT text",
                   _utf8_text(_bom) is False, ""))
    checks.append(("a U+FEFF in the MIDDLE of a file still counts against it",
                   _utf8_text("ok".encode("utf-8") + _bom
                              + "more".encode("utf-8")) is False, ""))
    # --- MPEG-4, ELF, Mach-O, ar, .pak -----------------------------------
    checks.append(("an MPEG-4 file type box is SPECIFIED",
                   classify(b"\x00\x00\x00\x20ftypM4A \x00\x00\x00\x00"
                            b"M4A mp42isom")[0] == "specified", ""))
    checks.append(("and `mp42` as major brand is the same format",
                   "MPEG-4" in classify(b"\x00\x00\x00\x18ftypmp42"
                                        b"\x00\x00\x00\x00mp42isom")[1], ""))
    checks.append(("`ftyp` at offset 4 with an ABSURD size word is REFUSED",
                   _mp4(b"\x7f\xff\xff\xffftypM4A \x00\x00\x00\x00") is False,
                   "the size is the check, not the four letters"))
    checks.append(("an ELF64 shared object is SPECIFIED",
                   classify(b"\x7fELF\x02\x01\x01\x00" + bytes(8))[0]
                   == "specified", ""))
    checks.append(("an ELF whose EI_VERSION is not 1 is REFUSED",
                   _elf(b"\x7fELF\x02\x01\x09\x00") is False, ""))
    checks.append(("an ELF whose EI_CLASS is 0 is REFUSED",
                   _elf(b"\x7fELF\x00\x01\x01\x00") is False, ""))
    checks.append(("a 64-bit Mach-O is SPECIFIED",
                   classify(b"\xcf\xfa\xed\xfe\x07\x00\x00\x01"
                            + bytes(8))[0] == "specified", ""))
    checks.append(("a 32-bit big-endian Mach-O is too",
                   "Mach-O" in classify(b"\xfe\xed\xfa\xce"
                                        + bytes(12))[1], ""))
    checks.append(("THE FOUR-BYTE HAZARD: a Mach-O universal binary with "
                   "nfat_arch 2 is a Mach-O",
                   "Mach-O" in classify(b"\xca\xfe\xba\xbe\x00\x00\x00\x02"
                                        + bytes(8))[1], ""))
    checks.append(("and a JAVA CLASS FILE, major 52, is NOT called a Mach-O",
                   "Mach-O" not in classify(b"\xca\xfe\xba\xbe\x00\x00\x004"
                                            + bytes(8))[1],
                   "0xCAFEBABE is both; nfat_arch <= 20 < 45 <= major"),)
    checks.append(("nor is a class file at Java 1.0's major 45",
                   _macho(b"\xca\xfe\xba\xbe\x00\x00\x00\x2d" + bytes(8))
                   is False, ""))
    checks.append(("a Unix archive is SPECIFIED",
                   classify(b"!<arch>\n/               0           0     0"
                            b"     0       8         `\n")[0] == "specified",
                   ""))
    checks.append(("`!<arch>` without the newline is REFUSED",
                   _ar(b"!<arch> not really") is False, ""))
    checks.append(("a Chromium .pak v5 whose entry table starts where the "
                   "header ends is DECODED",
                   classify(b"\x05\x00\x00\x00\x01\x00\x00\x00"
                            b"\x02\x00\x01\x00"
                            b"\x90\x01\x22\x00\x00\x00" + bytes(8))[0]
                   == "decoded", "12 + 3*6 + 1*4 = 34 = 0x22"),)
    checks.append(("a .pak v4 does the same arithmetic without aliases",
                   classify(b"\x04\x00\x00\x00\x02\x00\x00\x00\x01"
                            b"\x90\x01\x1b\x00\x00\x00" + bytes(8))[0]
                   == "decoded", "9 + 3*6 = 27 = 0x1b"),)
    checks.append(("a .pak whose first offset does NOT match the header is "
                   "REFUSED",
                   _chromium_pak(b"\x05\x00\x00\x00\x01\x00\x00\x00"
                                 b"\x02\x00\x01\x00"
                                 b"\x90\x01\x63\x00\x00\x00" + bytes(8))
                   is False, "this is the whole signature"))
    checks.append(("a four-byte little-endian 5 followed by nothing "
                   "structural is REFUSED",
                   _chromium_pak(b"\x05\x00\x00\x00" + bytes(24)) is False,
                   ""))
    checks.append(("a .pak of version 3 is REFUSED",
                   _chromium_pak(b"\x03\x00\x00\x00\x01\x00\x00\x00"
                                 b"\x02\x00\x01\x00"
                                 b"\x90\x01\x22\x00\x00\x00") is False, ""))
    # --- PX, added on pc-ilgrandegiocoditangentopoli-doc ------------------
    # The signature is two letters plus an arithmetic agreement, so the checks
    # that matter are the REFUSALS: three of the six below must say no, and
    # the first of them is a file that begins `PX` and is not one.
    _pxgood = (b"PX\x40\x01\xc8\x00"
               b"\xf7\xff\x05\x00\x40\x01\xc8"
               b"\xff\x06\x00" + bytes(64))
    checks.append(("a PX whose stream repeats its own geometry is DECODED",
                   classify(_pxgood)[0] == "decoded",
                   "320 and 200 in the header, 320 and 200 in the preamble"))
    checks.append(("a file that merely BEGINS `PX` is REFUSED",
                   _px(b"PX" + bytes(60)) is False,
                   "this is the whole point of decoding ten bytes"))
    checks.append(("a PX whose preamble geometry DISAGREES is REFUSED",
                   _px(b"PX\x40\x01\xc8\x00"
                       b"\xf7\xff\x05\x00\x41\x01\xc8"
                       b"\xff\x06\x00" + bytes(64)) is False,
                   "321 in the preamble against 320 in the header"))
    checks.append(("a PX with a zero dimension is REFUSED",
                   _px(b"PX\x00\x00\xc8\x00" + bytes(60)) is False, ""))
    checks.append(("a PX too short to decode ten bytes is REFUSED",
                   _px(b"PX\x40\x01\xc8\x00\xff") is False, ""))
    checks.append(("PX is tested before every text codec",
                   _ordering_ok() is True,
                   "a binary magic appended after the codecs is shadowed"))

    # -- the two Tecnoart formats, and the length channel ------------------
    _screen = b"\x40\x01\xc8\x00y" + bytes(4091)
    checks.append(("a 320 x 200 y head with its 64,777-byte length is DERIVED",
                   classify(_screen, 64777)[0] == "derived", ""))
    checks.append(("and is named as a Tecnoart picture",
                   "Tecnoart .BMB" in classify(_screen, 64777)[1], ""))
    checks.append(("the same head with a length one byte off is OPAQUE",
                   classify(_screen, 64778)[0] == "opaque", ""))
    checks.append(("the same head with NO length passes on five bytes only, "
                   "the head-only warrant",
                   classify(_screen)[0] == "derived", ""))
    _strip = b"\x39\x00\x30\x00y\x56\x00" + bytes(4089)
    checks.append(("a 57 x 48 head with count 86 and length 236,077 is the "
                   "animation", classify(_strip, 236077)[0] == "derived", ""))
    checks.append(("a flag byte that is not y or n is OPAQUE",
                   classify(b"\x40\x01\xc8\x00x" + bytes(4091), 64777)[0]
                   == "opaque", ""))
    checks.append(("an MZ head with a picture's length is still the "
                   "executable when its header holds, because MZ is tested "
                   "first",
                   classify(_mz_head + bytes(4096 - len(_mz_head)), 64777)[0]
                   == "specified", ""))
    checks.append(("but MZ\\x36\\x01y over zeros -- the two letters and no "
                   "header behind them -- is now OPAQUE, not the executable",
                   classify(b"MZ\x36\x01y" + bytes(4091), 64777)[0]
                   == "opaque", ""))
    _font = bytes([1]) * 4096
    checks.append(("a blank-celled three-value head at length 9,216 is the "
                   "font", "font" in classify(_font, 9216)[1], ""))
    checks.append(("the same head at another length is OPAQUE",
                   classify(_font, 9217)[0] == "opaque", ""))
    checks.append(("the font probe is tested after the picture probe and "
                   "before every text codec",
                   _ordering_ok() is True
                   and [m[0] for m in MAGICS].index(_bmb)
                   < [m[0] for m in MAGICS].index(_fnt), ""))
    checks.append(("exactly six probes ask for the length, and all say so",
                   sorted(m[0].__name__ for m in MAGICS
                          if getattr(m[0], "wants_size", False))
                   == ["_bmb", "_fnt", "_forgedat", "_mz", "_pes", "_res"], ""))
    # -- the .RES probe, added on pc-teenagent-doc -------------------------
    # A head built here: three members of 10, 0 and 5 bytes.
    _res_head = struct.pack("<I4I", 3, 20, 30, 30, 35) + bytes(15)
    checks.append(("a .RES directory of 3 that closes on its length is DERIVED",
                   classify(_res_head, 35)[1].startswith("TEENAGENT .RES"), ""))
    checks.append(("the same head at the wrong length is OPAQUE",
                   classify(_res_head, 36)[0] == "opaque", ""))
    checks.append(("the same head with a non-monotonic offset is OPAQUE",
                   classify(_res_head[:12] + struct.pack("<I", 19)
                            + _res_head[16:], 35)[0] == "opaque", ""))
    checks.append(("the same head with the first offset off by one is OPAQUE",
                   classify(_res_head[:4] + struct.pack("<I", 21)
                            + _res_head[8:], 35)[0] == "opaque", ""))
    checks.append(("the .RES probe is tested after the GAME.DAT probe and "
                   "before every text codec",
                   _ordering_ok() is True
                   and [m[0] for m in MAGICS].index(_forgedat)
                   < [m[0] for m in MAGICS].index(_res), ""))
    # -- the GAME.DAT probe, added on pc-demonsforge-doc -------------------
    # A head built here: signature, boot strings, two chained records and a
    # terminator; the bodies are 100 + 50 bytes from 2048 on.
    _df_head = bytearray(forgedat.SIGNATURE.ljust(512, b"\0"))
    _df_head += (b"\xb8\xc0\x07" + b"\0" * 40 + b"* Boot error *\0Strike any key to reboot\0").ljust(512, b"\0")
    _df_head += struct.pack("<HHHHB3s", 4, 4, 0, 100, 2, b"R1\0")
    _df_head += struct.pack("<HHHHB3s", 4, 4, 100, 150, 3, b"STR")
    _df_head += b"\0" * 12
    _df_head = bytes(_df_head.ljust(4096, b"\0"))
    checks.append(("a GAME.DAT head whose two records chain and end inside "
                   "the length is DERIVED",
                   classify(_df_head, 2198)[1].startswith("THE DEMON'S FORGE"), ""))
    checks.append(("the same head at a length short of its last body is OPAQUE",
                   classify(_df_head, 2100)[0] == "opaque", ""))
    checks.append(("the same head with the second record's start moved off "
                   "the first's end is OPAQUE",
                   classify(_df_head[:0x400 + 12 + 4] + b"\x65" + _df_head[0x400 + 12 + 5:], 2198)[0]
                   == "opaque", ""))
    checks.append(("the same head without the boot strings is OPAQUE",
                   classify(_df_head[:0x200] + bytes(512) + _df_head[0x400:], 2198)[0] == "opaque", ""))
    checks.append(("the GAME.DAT probe is tested after the .PES probe and "
                   "before every text codec",
                   _ordering_ok() is True
                   and [m[0] for m in MAGICS].index(_pes)
                   < [m[0] for m in MAGICS].index(_forgedat), ""))
    # -- the .PES / .PCS probe, added on pc-outrun-doc --------------------
    # The 96-byte header of STUMP.PES, quoted: 82, final 564, two stages,
    # type 2, out 411, nine counts (Kraft 1.0), 78 distinct symbols.
    _pes_head = bytes.fromhex(
        "82340200029b01000900010002061008131a000114020307081630050a0b0c0e0f"
        "1017182048505368707311151a34408087bf04131b1c28313233357f8fc0cfe7f0"
        "f7fcfeff06090d12191d373a3f444c6065698388979fa0a6acbbc7e0eff8")
    checks.append(("the 96-byte header of STUMP.PES, quoted, is DERIVED at "
                   "its length 360",
                   classify(_pes_head + bytes(264), 360)[1]
                   .startswith("OUT RUN .PES"), ""))
    checks.append(("the same head with one Huffman count changed (Kraft sum "
                   "not 1) is OPAQUE",
                   classify(_pes_head[:9] + b"\x01" + _pes_head[10:]
                            + bytes(264), 360)[0] == "opaque", ""))
    checks.append(("the same head at a length far above its declared final "
                   "size is OPAQUE",
                   classify(_pes_head + bytes(264), 5000)[0] == "opaque", ""))
    checks.append(("a stage count of 3 under the packed bit is OPAQUE",
                   classify(b"\x83" + _pes_head[1:] + bytes(264), 360)[0]
                   == "opaque", ""))
    checks.append(("a pack type of 3 at +4 is OPAQUE",
                   classify(_pes_head[:4] + b"\x03" + _pes_head[5:]
                            + bytes(264), 360)[0] == "opaque", ""))
    checks.append(("the .PES probe is tested after the font probe and before "
                   "every text codec",
                   _ordering_ok() is True
                   and [m[0] for m in MAGICS].index(_fnt)
                   < [m[0] for m in MAGICS].index(_pes), ""))
    checks.append(("a probe that does not ask for the length is never "
                   "handed one: the ZIP magic still fires with a length",
                   classify(b"PK\x03\x04\x14\x00\x00\x00\x08\x00", 1000)[0]
                   == "specified", ""))

    checks.append(("a random binary is OPAQUE",
                   classify(bytes([7, 200, 3, 99, 250]))[0] == "opaque", ""))
    checks.append(("an empty file is OPAQUE and does not crash",
                   classify(b"")[0] == "opaque", ""))
    checks.append(("the classifier emits only bucket names the report knows",
                   {m[1] for m in MAGICS} | {"opaque"}
                   <= {"specified", "decoded", "derived", "opaque"}, ""))
    width = max(len(c[0]) for c in checks)
    failed = 0
    for label, ok, note in checks:
        print("  %-*s  %s   %s" % (width, label, "ok  " if ok else "FAIL",
                                   note))
        if not ok:
            failed += 1
    print()
    print("%d checks, %d failures" % (len(checks), failed))
    return 1 if failed else 0


def report_ambiguity(root):
    """How many files more than one text codec accepts.

    The order of the three text codecs in MAGICS is a decision, not a
    measurement: EUC-JP's lead bytes are cp932's half-width katakana, so a
    EUC-JP document decodes under cp932 into nonsense without one illegal
    sequence. This mode publishes the cost of that decision instead of hiding
    it, which is the only honest thing a probe of this shape can do.
    """
    probes = (("utf-8", _utf8_text), ("euc_jp", _eucjp_text),
              ("cp932", _cp932_text))
    rows, multi = [], 0
    for dp, _dn, fn in os.walk(root):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                head = fh.read(HEAD)
            takers = [n for n, pr in probes if pr(head)]
            if not takers:
                continue
            rows.append((os.path.relpath(p, root).replace(os.sep, "/"),
                         takers))
            if len(takers) > 1:
                multi += 1
    if not rows:
        sys.exit("coverage: no file under %r is accepted by any multi-byte "
                 "text codec -- refusing to report a clean ambiguity table "
                 "over an empty population" % root)
    print("files accepted by at least one multi-byte text codec : %d" %
          len(rows))
    print("files accepted by MORE THAN ONE                      : %d" % multi)
    print()
    combos = {}
    for _p, takers in rows:
        combos["+".join(takers)] = combos.get("+".join(takers), 0) + 1
    for k in sorted(combos, key=lambda k: (-combos[k], k)):
        print("  %-24s %4d" % (k, combos[k]))
    print()
    print("  the codec MAGICS names first wins, and that order is a decision:")
    print("  utf-8, then euc_jp, then cp932. Every file in a row with a '+'")
    print("  in it could have been filed under another name.")
    for p, takers in rows:
        if len(takers) > 1:
            print("    %-58s %s" % (p, "+".join(takers)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", choices=("members", "product", "tree",
                                     "ambiguity", "selftest"))
    ap.add_argument("--members", default="_work/members")
    ap.add_argument("--root")
    args = ap.parse_args()
    if args.mode == "selftest":
        return selftest()
    if args.mode == "ambiguity":
        if not args.root:
            sys.exit("coverage: ambiguity mode needs --root")
        return report_ambiguity(args.root)
    if args.mode == "tree":
        if not args.root:
            sys.exit("coverage: tree mode needs --root")
        return report_tree(args.root)
    rows, label = population(args.mode, args.members)
    return report(rows, label, args.mode)


if __name__ == "__main__":
    sys.exit(main())
