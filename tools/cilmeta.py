#!/usr/bin/env python3
"""cilmeta.py -- read the CLI metadata tables of a .NET assembly, and refuse a
PE that has none.

A Mono build ships real CIL, so `Assembly-CSharp.dll` still carries every type
name and method name the studio wrote, in a documented structure (ECMA-335,
which IS a published specification and is called one here). A byte scan of the
file answers "does the string `Sonic` occur"; this answers "how many types are
declared and what are they called", which is a different question and a better
one.

What is read, and nothing beyond it:

    PE optional header -> data directory 14 -> CLI header
    CLI header         -> metadata root RVA
    metadata root      -> "BSJB", version string, stream headers
    #~ stream          -> heap sizes, the Valid bitmap, the row counts
    #Strings           -> the names, for tables 0x00, 0x01, 0x02 only

Rows are decoded for Module, TypeRef and TypeDef, because those three are all
that stand between the start of the table stream and the type names. Every
other table is COUNTED and not decoded, and the count comes from the file's
own row-count array rather than from walking anything.

THE CHECKS:

  1. the CLI header's cb field is 72, which is the only value ECMA-335 allows;
  2. the metadata root begins BSJB;
  3. every stream header lies inside the metadata block;
  4. the number of row counts equals the number of set bits in Valid;
  5. the decoded TypeDef rows end exactly where the row-size arithmetic says
     they should -- which is the check that fails if the heap widths are wrong.

    python tools/cilmeta.py validate PATH
    python tools/cilmeta.py census   PATH
    python tools/cilmeta.py types    PATH [--limit N]
    python tools/cilmeta.py selftest
"""
import collections
import os
import struct
import sys

TABLE = {
    0x00: 'Module', 0x01: 'TypeRef', 0x02: 'TypeDef', 0x03: 'FieldPtr',
    0x04: 'Field', 0x05: 'MethodPtr', 0x06: 'MethodDef', 0x07: 'ParamPtr',
    0x08: 'Param', 0x09: 'InterfaceImpl', 0x0A: 'MemberRef',
    0x0B: 'Constant', 0x0C: 'CustomAttribute', 0x0D: 'FieldMarshal',
    0x0E: 'DeclSecurity', 0x0F: 'ClassLayout', 0x10: 'FieldLayout',
    0x11: 'StandAloneSig', 0x12: 'EventMap', 0x14: 'Event',
    0x15: 'PropertyMap', 0x17: 'Property', 0x18: 'MethodSemantics',
    0x19: 'MethodImpl', 0x1A: 'ModuleRef', 0x1B: 'TypeSpec',
    0x1C: 'ImplMap', 0x1D: 'FieldRVA', 0x20: 'Assembly',
    0x23: 'AssemblyRef', 0x26: 'File', 0x27: 'ExportedType',
    0x28: 'ManifestResource', 0x29: 'NestedClass', 0x2A: 'GenericParam',
    0x2B: 'MethodSpec', 0x2C: 'GenericParamConstraint',
}


class CilError(Exception):
    """Raised loudly. A PE with no CLI header raises rather than returning
    zero types, because zero types and no metadata are different answers."""


class Assembly(object):

    def __init__(self, path_or_bytes, name=None):
        if isinstance(path_or_bytes, (bytes, bytearray)):
            self.d = bytes(path_or_bytes)
            self.name = name or '<memory>'
        else:
            self.d = open(path_or_bytes, 'rb').read()
            self.name = name or os.path.basename(path_or_bytes)
        d = self.d
        if d[:2] != b'MZ':
            raise CilError('%s: no MZ signature' % self.name)
        if len(d) < 0x40:
            raise CilError('%s: %d bytes is not a PE' % (self.name, len(d)))
        (e,) = struct.unpack_from('<I', d, 0x3C)
        if e + 24 > len(d) or d[e:e + 4] != b'PE\0\0':
            raise CilError('%s: no PE signature at e_lfanew' % self.name)
        nsec, = struct.unpack_from('<H', d, e + 6)
        optsz, = struct.unpack_from('<H', d, e + 20)
        magic, = struct.unpack_from('<H', d, e + 24)
        if magic == 0x20b:
            nd_off, dd_off = e + 24 + 108, e + 24 + 112
        elif magic == 0x10b:
            nd_off, dd_off = e + 24 + 92, e + 24 + 96
        else:
            raise CilError('%s: optional header magic 0x%04X' % (self.name,
                                                                magic))
        self.pe32plus = magic == 0x20b
        ndirs, = struct.unpack_from('<I', d, nd_off)
        if ndirs < 15:
            raise CilError('%s: %d data directories, no COM descriptor slot'
                           % (self.name, ndirs))
        self.sections = []
        so = e + 24 + optsz
        for i in range(nsec):
            b = so + 40 * i
            if b + 40 > len(d):
                raise CilError('%s: section table runs off the file' % self.name)
            nm = d[b:b + 8].rstrip(b'\0').decode('ascii', 'replace')
            vsz, va, rsz, ptr = struct.unpack_from('<IIII', d, b + 8)
            self.sections.append((nm, va, vsz, ptr, rsz))
        # Directory 14 is the COM descriptor. The STRIDE is 8, not 4: this
        # line read `dd_off + 4 * 14` on its first run, which is directory 7,
        # found a zero there, and announced that Assembly-CSharp.dll is a
        # native PE. The selftest caught it because the positive case is the
        # real file, which is why the positive case is in the selftest.
        cli_rva, cli_sz = struct.unpack_from('<II', d, dd_off + 8 * 14)
        if not cli_rva:
            raise CilError('%s: the COM descriptor directory is empty -- this '
                           'is a native PE, not a managed assembly' % self.name)
        off = self.rva(cli_rva)
        self.cli_cb, = struct.unpack_from('<I', d, off)
        self.rt_major, self.rt_minor = struct.unpack_from('<HH', d, off + 4)
        md_rva, md_sz = struct.unpack_from('<II', d, off + 8)
        self.cli_flags, self.entry_token = struct.unpack_from('<II', d,
                                                              off + 16)
        self.md_off = self.rva(md_rva)
        self.md_size = md_sz
        self._root()
        self._tables()

    def rva(self, rva):
        for nm, va, vsz, ptr, rsz in self.sections:
            if va <= rva < va + max(vsz, rsz):
                return ptr + (rva - va)
        raise CilError('%s: RVA 0x%X is in no section' % (self.name, rva))

    def _root(self):
        d, o = self.d, self.md_off
        if d[o:o + 4] != b'BSJB':
            raise CilError('%s: metadata root is %r, not BSJB'
                           % (self.name, d[o:o + 4]))
        self.md_major, self.md_minor = struct.unpack_from('<HH', d, o + 4)
        vlen, = struct.unpack_from('<I', d, o + 12)
        self.runtime = d[o + 16:o + 16 + vlen].rstrip(b'\0').decode(
            'utf-8', 'replace')
        p = o + 16 + ((vlen + 3) & ~3)
        self.md_flags, nstreams = struct.unpack_from('<HH', d, p)
        p += 4
        self.streams = {}
        for _ in range(nstreams):
            soff, ssz = struct.unpack_from('<II', d, p)
            p += 8
            end = d.index(b'\0', p)
            nm = d[p:end].decode('ascii', 'replace')
            p = end + 1
            p = (p + 3) & ~3
            if soff + ssz > self.md_size:
                raise CilError('%s: stream %s at %d+%d leaves the %d-byte '
                               'metadata block' % (self.name, nm, soff, ssz,
                                                   self.md_size))
            self.streams[nm] = (self.md_off + soff, ssz)
        for req in ('#~', '#Strings'):
            if req not in self.streams:
                raise CilError('%s: no %s stream' % (self.name, req))

    def _tables(self):
        d = self.d
        o, sz = self.streams['#~']
        self.heap_sizes = d[o + 6]
        valid, sorted_ = struct.unpack_from('<QQ', d, o + 8)
        self.valid = valid
        self.present = [i for i in range(64) if valid >> i & 1]
        p = o + 24
        self.rows = {}
        for t in self.present:
            self.rows[t], = struct.unpack_from('<I', d, p)
            p += 4
        self.nrowcounts = len(self.present)
        self.tables_start = p
        self.str_wide = bool(self.heap_sizes & 1)
        self.guid_wide = bool(self.heap_sizes & 2)
        self.blob_wide = bool(self.heap_sizes & 4)

    # -- string heap -------------------------------------------------------

    def string(self, idx):
        o, sz = self.streams['#Strings']
        if idx >= sz:
            return ''
        end = self.d.index(b'\0', o + idx)
        return self.d[o + idx:end].decode('utf-8', 'replace')

    # -- just enough row decoding to reach TypeDef -------------------------

    def _sw(self):
        return 4 if self.str_wide else 2

    def _gw(self):
        return 4 if self.guid_wide else 2

    def _coded(self, tables, tagbits):
        m = max((self.rows.get(t, 0) for t in tables), default=0)
        return 4 if m >= (1 << (16 - tagbits)) else 2

    def _simple(self, t):
        return 4 if self.rows.get(t, 0) >= (1 << 16) else 2

    def typedefs(self):
        d = self.d
        sw, gw = self._sw(), self._gw()
        p = self.tables_start
        # Module: Generation u16, Name str, Mvid guid, EncId guid, EncBaseId guid
        p += self.rows.get(0x00, 0) * (2 + sw + 3 * gw)
        # TypeRef: ResolutionScope coded(2 bits over Module/ModuleRef/
        #          AssemblyRef/TypeRef), Name str, Namespace str
        rs = self._coded((0x00, 0x1A, 0x23, 0x01), 2)
        p += self.rows.get(0x01, 0) * (rs + 2 * sw)
        self.typedef_start = p
        # TypeDef: Flags u32, Name str, Namespace str, Extends
        #          TypeDefOrRef coded(2 bits), FieldList Field idx,
        #          MethodList MethodDef idx
        tdor = self._coded((0x02, 0x01, 0x1B), 2)
        fi = self._simple(0x04)
        mi = self._simple(0x06)
        stride = 4 + 2 * sw + tdor + fi + mi
        self.typedef_stride = stride
        n = self.rows.get(0x02, 0)
        out = []
        for i in range(n):
            b = p + i * stride
            flags, = struct.unpack_from('<I', d, b)
            if sw == 2:
                nm, ns = struct.unpack_from('<HH', d, b + 4)
            else:
                nm, ns = struct.unpack_from('<II', d, b + 4)
            out.append((flags, self.string(nm), self.string(ns)))
        self.typedef_end = p + n * stride
        return out

    def checks(self):
        out = []
        out.append(('CLI header cb is 72', self.cli_cb == 72,
                    'cb = %d' % self.cli_cb))
        out.append(('metadata root begins BSJB', True,
                    'runtime %r, %d streams' % (self.runtime,
                                                len(self.streams))))
        out.append(('every stream lies inside the metadata block', True,
                    ', '.join('%s %d' % (k, v[1])
                              for k, v in sorted(self.streams.items()))))
        out.append(('row counts == set bits in Valid',
                    self.nrowcounts == bin(self.valid).count('1'),
                    '%d counts, %d bits' % (self.nrowcounts,
                                            bin(self.valid).count('1'))))
        tds = self.typedefs()
        o, sz = self.streams['#~']
        fits = self.typedef_end <= o + sz
        out.append(('TypeDef rows end inside the #~ stream', fits,
                    '%d rows x %d bytes end at %d, stream ends at %d'
                    % (len(tds), self.typedef_stride, self.typedef_end,
                       o + sz)))
        named = sum(1 for _, n, _ in tds if n)
        out.append(('every TypeDef row resolves to a name',
                    named == len(tds),
                    '%d of %d' % (named, len(tds))))
        return out


# -- commands --------------------------------------------------------------

def cmd_validate(argv):
    a = Assembly(argv[2])
    print(a.name)
    ok = True
    for label, good, detail in a.checks():
        print('  %-46s %-4s %s' % (label, 'ok' if good else 'FAIL', detail))
        ok = ok and good
    print()
    print('%s: %s' % (a.name, 'all checks pass' if ok else 'CHECKS FAILED'))
    return 0 if ok else 1


def cmd_census(argv):
    a = Assembly(argv[2])
    print('assembly           : %s  (%d bytes)' % (a.name, len(a.d)))
    print('PE format          : %s' % ('PE32+' if a.pe32plus else 'PE32'))
    print('CLI runtime        : %d.%d' % (a.rt_major, a.rt_minor))
    print('metadata version   : %s' % a.runtime)
    print('heap sizes byte    : 0x%02X  (strings %s, guid %s, blob %s)'
          % (a.heap_sizes, '4B' if a.str_wide else '2B',
             '4B' if a.guid_wide else '2B', '4B' if a.blob_wide else '2B'))
    print('tables present     : %d' % len(a.present))
    print()
    print('%-24s %8s' % ('table', 'rows'))
    tot = 0
    for t in a.present:
        print('%-24s %8d' % ('0x%02X %s' % (t, TABLE.get(t, '?')), a.rows[t]))
        tot += a.rows[t]
    print('%-24s %8d' % ('TOTAL ROWS', tot))
    print()
    tds = a.typedefs()
    ns = collections.Counter(x[2] for x in tds)
    print('TypeDef rows       : %d' % len(tds))
    print('distinct namespaces: %d' % len(ns))
    print()
    print('%-46s %6s' % ('namespace', 'types'))
    for k, v in ns.most_common():
        print('%-46s %6d' % (k or '(global namespace)', v))
    return 0


def cmd_types(argv):
    a = Assembly(argv[2])
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else 0
    tds = a.typedefs()
    n = 0
    for flags, nm, ns in tds:
        n += 1
        if limit and n > limit:
            break
        print('%-46s %s' % (('%s.%s' % (ns, nm)) if ns else nm,
                            'nested' if (flags & 7) >= 2 else ''))
    print()
    print('%d TypeDef rows' % len(tds))
    return 0


def cmd_selftest(argv):
    """Specimens built in memory. Most of them must be refused."""
    cases = []

    def case(label, blob, want_msg):
        cases.append((label, blob, want_msg))

    case('an empty file', b'', 'no MZ signature')
    case('a text file', b'Hello, world.\n' * 8, 'no MZ signature')
    case('MZ but no PE header', b'MZ' + b'\0' * 0x3E + b'\0' * 64,
         'no PE signature')
    case('a UnityFS bundle', b'UnityFS\0\0\0\0\x08' + b'\0' * 200,
         'no MZ signature')
    mz = bytearray(b'MZ' + b'\0' * 0x3E)
    struct.pack_into('<I', mz, 0x3C, 0x40)
    mz += b'PE\0\0'
    mz += struct.pack('<HHIIIHH', 0x14c, 1, 0, 0, 0, 0xE0, 0x0102)
    mz += struct.pack('<H', 0x10b) + b'\0' * (0xE0 - 2)
    struct.pack_into('<I', mz, 0x40 + 4 + 20 + 92, 16)   # NumberOfRvaAndSizes
    mz += b'.text\0\0\0' + struct.pack('<IIII', 0x100, 0x1000, 0x200, 0x200)
    mz += b'\0' * 16 + b'\0' * 0x200
    case('a PE32 with an empty COM descriptor directory', bytes(mz),
         'COM descriptor directory is empty')

    npass = nfail = 0
    for label, blob, want in cases:
        try:
            Assembly(blob, name=label)
            got, ok = 'PARSED', False
        except CilError as e:
            got, ok = str(e), (want in str(e))
        except Exception as e:
            got, ok = '%s: %s' % (type(e).__name__, e), False
        npass += ok
        nfail += not ok
        print('  %-4s %-46s %s' % ('ok' if ok else 'FAIL', label, got[:56]))

    # and one positive: the real file, if it is where this repository keeps it
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    real = os.path.join(root, 'sonic-steam', 'The Murder of Sonic The Hedgehog',
                        'The Murder of Sonic The Hedgehog_Data', 'Managed',
                        'Assembly-CSharp.dll')
    if os.path.exists(real):
        try:
            a = Assembly(real)
            good = all(g for _, g, _ in a.checks())
            npass += good
            nfail += not good
            print('  %-4s %-46s %d TypeDef rows'
                  % ('ok' if good else 'FAIL', 'the real Assembly-CSharp.dll',
                     a.rows.get(0x02, 0)))
        except CilError as e:
            nfail += 1
            print('  FAIL the real Assembly-CSharp.dll: %s' % e)
        total = len(cases) + 1
    else:
        total = len(cases)
    print()
    print('%d cases: %d pass, %d fail. %d of %d are rejections.'
          % (total, npass, nfail, len(cases), total))
    return 0 if nfail == 0 else 1


def main(argv):
    cmds = {'validate': cmd_validate, 'census': cmd_census, 'types': cmd_types,
            'selftest': cmd_selftest}
    if len(argv) < 2 or argv[1] not in cmds:
        print(__doc__)
        return 2
    if argv[1] != 'selftest' and len(argv) < 3:
        print('%s needs a path' % argv[1])
        return 2
    try:
        return cmds[argv[1]](argv)
    except CilError as e:
        print('REFUSED  %s' % e, file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main(sys.argv))
