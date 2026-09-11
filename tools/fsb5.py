#!/usr/bin/env python3
"""Read FMOD Sound Bank version 5 headers: what audio a Unity build ships.

The `.resource` files beside a Unity serialized file are where AudioClip data
goes, and on this build they are FSB5 banks -- FMOD's container, which Unity
uses as its own.  That is a different answer from *Tales of Crestoria*, whose
`.aac` files hold Ogg Vorbis inside tri-Ace's own `AAC ` chunk container, and
the difference is the point: the audio pipeline came with the engine both
times, and the engine is not the same engine.

The format, as this build writes it:

    +0x00  "FSB5"
    +0x04  u32  version (0 or 1)
    +0x08  u32  sample count
    +0x0C  u32  size of the sample header block
    +0x10  u32  size of the name table
    +0x14  u32  size of the sample data
    +0x18  u32  codec
    +0x1C  8 zero bytes, 16 bytes of hash, 8 unused
    (version 0 has one extra u32 here)

then one 64-bit word per sample, bit-packed:

    bit  0        another parameter chunk follows
    bits 1..4     sample rate, as an index into a fixed table
    bit  5        channel count minus one
    bits 6..33    data offset, in units of 32 bytes
    bits 34..63   length in samples

and then, optionally, per-sample parameter chunks in the same shape, a name
table of u32 offsets followed by NUL-terminated names, and the sample data.

The positive control is free and it is the one this repository asks every
container for: the header declares `sampleHeadersSize`, `nameTableSize` and
`dataSize`, and 60 + those three must equal the file.  A reader with the layout
wrong fails that sum rather than producing plausible nonsense.

    python fsb5.py info FILE...
    python fsb5.py census DIR
    python fsb5.py --selftest

Standard library only.  Nothing here decodes audio; it reads headers.
"""

import os
import struct
import sys

RATES = [0, 8000, 11000, 11025, 16000, 22050, 24000, 32000, 44100, 48000,
         96000]

CODEC = {
    0: 'none', 1: 'PCM8', 2: 'PCM16', 3: 'PCM24', 4: 'PCM32', 5: 'PCMFLOAT',
    6: 'GCADPCM', 7: 'IMAADPCM', 8: 'VAG', 9: 'HEVAG', 10: 'XMA', 11: 'MPEG',
    12: 'CELT', 13: 'ATRAC9', 14: 'XWMA', 15: 'Vorbis', 16: 'FADPCM',
    17: 'Opus',
}

CHUNK = {1: 'channels', 2: 'frequency', 3: 'loop', 6: 'xmaseek',
         7: 'dspcoeff', 9: 'xwmadata', 10: 'vorbisdata'}


class Fsb5(object):
    def __init__(self, data, path='?'):
        if data[:4] != b'FSB5':
            raise ValueError('not an FSB5 bank')
        self.data = data
        self.path = path
        (self.version, self.n_samples, self.hdr_size, self.name_size,
         self.data_size, self.codec) = struct.unpack_from('<6I', data, 4)
        self.base = 60 if self.version == 1 else 64
        self.declared = self.base + self.hdr_size + self.name_size + self.data_size
        self.samples = []
        pos = self.base
        end = self.base + self.hdr_size
        for _ in range(self.n_samples):
            if pos + 8 > len(data):
                break
            raw = struct.unpack_from('<Q', data, pos)[0]
            pos += 8
            more = raw & 1
            rate_i = (raw >> 1) & 0xF
            chans = ((raw >> 5) & 1) + 1
            off = ((raw >> 6) & 0xFFFFFFF) * 32
            nsamp = (raw >> 34) & 0x3FFFFFFF
            chunks = []
            while more and pos + 4 <= end:
                c = struct.unpack_from('<I', data, pos)[0]
                pos += 4
                more = c & 1
                size = (c >> 1) & 0xFFFFFF
                kind = (c >> 25) & 0x7F
                body = data[pos:pos + size]
                if kind == 1 and size >= 1:
                    chans = body[0]
                elif kind == 2 and size >= 4:
                    rate_i = -1
                    self._freq = struct.unpack_from('<I', body, 0)[0]
                chunks.append((kind, size))
                pos += size
            rate = (RATES[rate_i] if 0 <= rate_i < len(RATES)
                    else getattr(self, '_freq', 0))
            self.samples.append(dict(offset=off, samples=nsamp, rate=rate,
                                     channels=chans, chunks=chunks))
        self.names = []
        if self.name_size:
            nbase = self.base + self.hdr_size
            try:
                offs = struct.unpack_from('<%dI' % self.n_samples, data, nbase)
                for o in offs:
                    p = nbase + o
                    e = data.find(b'\0', p)
                    self.names.append(data[p:e].decode('utf-8', 'replace'))
            except struct.error:
                pass
        # sizes: each sample runs to the next one's offset, the last to the end
        dbase = self.base + self.hdr_size + self.name_size
        for i, s in enumerate(self.samples):
            nxt = (self.samples[i + 1]['offset'] if i + 1 < len(self.samples)
                   else self.data_size)
            s['bytes'] = nxt - s['offset']
            s['file_offset'] = dbase + s['offset']
            s['seconds'] = s['samples'] / s['rate'] if s['rate'] else 0.0


def cmd_info(argv):
    for path in [a for a in argv[2:] if not a.startswith('--')]:
        data = open(path, 'rb').read()
        try:
            b = Fsb5(data, path)
        except ValueError as e:
            print('%s: %s' % (path, e))
            continue
        print('=' * 72)
        print('%s   %d bytes' % (path, len(data)))
        print('=' * 72)
        print('  version            %d  (header %d bytes)' % (b.version, b.base))
        print('  samples            %d' % b.n_samples)
        print('  codec              %s (%d)'
              % (CODEC.get(b.codec, '?'), b.codec))
        print('  sample headers     %d bytes' % b.hdr_size)
        print('  name table         %d bytes, %d names read'
              % (b.name_size, len(b.names)))
        print('  sample data        %d bytes' % b.data_size)
        print('  60 + the three     %d' % b.declared)
        print('  file size          %d   %s'
              % (len(data),
                 'agrees' if b.declared == len(data) else 'DISAGREES'))
        print()
        print('  %-34s %10s %9s %5s %12s %9s'
              % ('NAME', 'SAMPLES', 'RATE', 'CH', 'BYTES', 'SECONDS'))
        for i, s in enumerate(b.samples):
            nm = b.names[i] if i < len(b.names) else '(unnamed)'
            print('  %-34s %10d %9d %5d %12d %9.2f'
                  % (nm[:34], s['samples'], s['rate'], s['channels'],
                     s['bytes'], s['seconds']))
        total = sum(s['seconds'] for s in b.samples)
        print()
        print('  %d samples, %.2f seconds of audio in total (%.2f minutes)'
              % (len(b.samples), total, total / 60))
        print()


def cmd_census(argv):
    root = argv[2]
    files = []
    for d, _s, ns in os.walk(root):
        for n in sorted(ns):
            files.append(os.path.join(d, n))
    banks = 0
    n_samp = 0
    secs = 0.0
    nbytes = 0
    ok = 0
    print('%-46s %8s %10s %10s %10s %9s'
          % ('FILE', 'SAMPLES', 'CODEC', 'BYTES', 'SIZE OK', 'SECONDS'))
    for p in files:
        try:
            data = open(p, 'rb').read(16)
        except OSError:
            continue
        if data[:4] != b'FSB5':
            continue
        data = open(p, 'rb').read()
        b = Fsb5(data, p)
        banks += 1
        n_samp += len(b.samples)
        t = sum(s['seconds'] for s in b.samples)
        secs += t
        nbytes += len(data)
        good = b.declared == len(data)
        ok += good
        print('%-46s %8d %10s %10d %10s %9.2f'
              % (os.path.relpath(p, root).replace('\\', '/')[:46],
                 len(b.samples), CODEC.get(b.codec, str(b.codec)), len(data),
                 'yes' if good else 'NO', t))
    print()
    print('%d FSB5 banks, %d samples, %d bytes, %.2f seconds (%.2f minutes)'
          % (banks, n_samp, nbytes, secs, secs / 60))
    print('%d of %d banks declare a size that matches the file on disk'
          % (ok, banks))


def selftest():
    """Build a bank by hand and read it back.

    The point is the size identity: 60 + sampleHeadersSize + nameTableSize +
    dataSize has to equal the file, and a bit-packing error in the sample word
    shows up as a wrong offset rather than as a parse failure, so the offsets
    are checked against values chosen to be unambiguous.
    """
    print('fsb5.py --selftest')
    print()
    hdrs = b''
    # sample 0: 44100 Hz (index 8), stereo, offset 0, 65536 samples
    raw = (0) | (8 << 1) | (1 << 5) | (0 << 6) | (65536 << 34)
    hdrs += struct.pack('<Q', raw)
    # sample 1: 22050 Hz (index 5), mono, offset 32*100 = 3200, 1000 samples
    raw = (0) | (5 << 1) | (0 << 5) | (100 << 6) | (1000 << 34)
    hdrs += struct.pack('<Q', raw)
    names = b''
    nt = struct.pack('<2I', 8, 8 + 5)
    names = nt + b'BGM\0' + b'\0' + b'se00\0'
    names += b'\0' * ((4 - len(names) % 4) % 4)
    body = b'\0' * 4096
    head = (b'FSB5' + struct.pack('<6I', 1, 2, len(hdrs), len(names),
                                  len(body), 15)
            + b'\0' * 8 + b'\0' * 16 + b'\0' * 8)
    blob = head + hdrs + names + body
    b = Fsb5(blob)
    checks = [
        ('file size identity', b.declared == len(blob), '%d vs %d'
         % (b.declared, len(blob))),
        ('sample count', len(b.samples) == 2, str(len(b.samples))),
        ('codec is Vorbis', CODEC.get(b.codec) == 'Vorbis', CODEC.get(b.codec)),
        ('sample 0 rate 44100', b.samples[0]['rate'] == 44100,
         str(b.samples[0]['rate'])),
        ('sample 0 stereo', b.samples[0]['channels'] == 2,
         str(b.samples[0]['channels'])),
        ('sample 0 length 65536', b.samples[0]['samples'] == 65536,
         str(b.samples[0]['samples'])),
        ('sample 1 rate 22050', b.samples[1]['rate'] == 22050,
         str(b.samples[1]['rate'])),
        ('sample 1 mono', b.samples[1]['channels'] == 1,
         str(b.samples[1]['channels'])),
        ('sample 1 offset 3200', b.samples[1]['offset'] == 3200,
         str(b.samples[1]['offset'])),
    ]
    ok = 0
    for label, good, got in checks:
        ok += good
        print('  %-28s %-12s %s' % (label, got, 'ok' if good else 'FAILED'))
    print()
    print('  %d of %d checks pass.' % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main(argv):
    if '--selftest' in argv:
        raise SystemExit(selftest())
    if len(argv) < 3:
        raise SystemExit(__doc__)
    if argv[1] == 'info':
        return cmd_info(argv)
    if argv[1] == 'census':
        return cmd_census(argv)
    raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv)
