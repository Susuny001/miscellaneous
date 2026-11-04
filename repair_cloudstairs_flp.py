#!/usr/bin/env python3
"""Conservative FLP repair: retain the source project's complete scaffold.

Only score data, names, channel enabled states and Playlist clips are replaced.
Channel numbers, wrapper states, init records and opaque compatibility data stay
in their original positions. Requires a complete source FLP, not the old reduced
Cloudstairs file. This module uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from compose_cloudstairs import BAR, PPQ, event, read_flp, unicode


def layout(source):
    raw = Path(source).read_bytes()
    es = read_flp(source)
    count, ppq = struct.unpack_from('<HH', raw, 10)
    starts = [k for k, (i, _) in enumerate(es) if i == 64]
    if count != len(starts) or count < 13 or ppq != PPQ:
        raise ValueError('Use the complete uploaded project or a repaired full-scaffold project; the old one-channel export is unsafe as a template.')
    first_notes = next(k for k, (i, _) in enumerate(es) if i == 65)
    first_channel = starts[0]
    # Preserve these source initialization records; the old writer dropped them.
    init_start = next(k for k in range(first_notes, first_channel) if es[k][0] == 226)
    arrange = next(k for k, (i, _) in enumerate(es) if i == 99)
    blocks = {}
    descriptions = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else arrange
        desc_start = next((k for k in range(start + 1, end) if es[k][0] == 65), end)
        channel_id = int.from_bytes(es[start][1], 'little')
        blocks[channel_id] = es[start:desc_start]
        if desc_start != end:
            descriptions.append((channel_id, es[desc_start:end]))
    if len(descriptions) != 1:
        raise ValueError('Expected one source Pattern metadata block; refusing to guess the layout.')
    description_channel, descriptions = descriptions[0]
    first_desc_end = next((k for k in range(1, len(descriptions)) if descriptions[k][0] == 65), len(descriptions))
    description_template = descriptions[:first_desc_end]
    if next((d for i, d in description_template if i == 164), None) != b'\0' * 4:
        raise ValueError('Source has custom Pattern lengths; use the unmodified uploaded project.')
    return raw[:14], es[:first_notes], es[init_start:first_channel], blocks, description_channel, description_template, es[arrange:]


def note_data(notes, start, end, channel):
    return b''.join(struct.pack('<IHHIHH8B', n['t'] - start, 0x4000, channel,
                               n['d'], n['p'], 0, 120, 0, 64, 0, 64, n['v'], 128, 128)
                    for n in notes if start <= n['t'] < end)


def repair(source, target, notes, sections, stock_piano=False):
    header, globals_, initializers, blocks, desc_channel, desc_template, tail = layout(source)
    channel = 6 if stock_piano else 12
    piano = blocks[channel]
    plugin = next(d.decode('utf-16le').rstrip('\0') for i, d in piano if i == 201)
    if plugin != ('FL Keys' if stock_piano else 'FLEX'):
        raise ValueError('Expected the original piano preset in its original channel slot.')
    output = []
    for i, data in globals_:
        if i == 156:
            data = struct.pack('<I', 100000)
        elif i == 67:
            data = struct.pack('<H', 1)
        elif i == 9:
            data = b'\0'  # Song mode
        elif i == 194:
            data = unicode('Cloudstairs - three short piano ideas')
        elif i == 202:
            data = unicode('')  # Remove the old machine-specific data directory.
        output.append((i, data))

    for s in sections:
        start = s['start_bar'] * BAR
        output.extend([(65, struct.pack('<H', s['pattern'])),
                       (224, note_data(notes, start, start + s['bars'] * BAR, channel))])
    output.extend(initializers)

    for channel_id, original_block in blocks.items():
        # The compatibility variant loads only stock FL Keys and empty disabled
        # Samplers. It contains no FLEX instance or external sample filename.
        block = original_block if not stock_piano or channel_id == channel else blocks[0]
        for i, data in block:
            if i == 64:
                data = struct.pack('<H', channel_id)
            elif i == 0:
                data = bytes([channel_id == channel])
            elif stock_piano and channel_id != channel and i == 196:
                data = unicode('')
            elif stock_piano and i == 203:
                data = unicode('Cloudstairs - FL Keys' if channel_id == channel else f'Empty {channel_id + 1:02d}')
            output.append((i, data))
        if channel_id == desc_channel:
            for s in sections:
                for i, data in desc_template:
                    if i == 250:
                        continue  # Original loop-starter name belongs to the old music.
                    if i == 65:
                        data = struct.pack('<H', s['pattern'])
                    elif i == 193:
                        data = unicode(s['name'])
                    # In particular, retain source event 164 = 0. The old writer
                    # assigned tick counts to this undocumented length field.
                    output.append((i, data))

    playlist = next(data for i, data in tail if i == 233)
    if len(playlist) % 80:
        raise ValueError('Expected source FL Studio 25 Playlist records; refusing to guess their stride.')
    clip_template = playlist[:80]
    clips = []
    for s in sections:
        clip = bytearray(clip_template)
        struct.pack_into('<IHHII', clip, 0, s['start_bar'] * BAR, 20480,
                         20480 + s['pattern'], s['bars'] * BAR, 499)
        struct.pack_into('<III', clip, 24, 0, s['bars'] * BAR, s['pattern'])
        clips.append(clip)
    for i, data in tail:
        if i == 233:
            data = b''.join(clips)
        elif i == 241:
            data = unicode('Three short piano ideas - 100 BPM')
        # Keep selection/window/mixer/plugin state verbatim; do not zero opaque
        # structures to make them resemble defaults.
        output.append((i, data))
    payload = b''.join(event(i, data) for i, data in output)
    Path(target).write_bytes(header + b'FLdt' + struct.pack('<I', len(payload)) + payload)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--score', type=Path, default=Path(__file__).with_name('Cloudstairs_score.json'))
    p.add_argument('--out', type=Path, default=Path(__file__).parent)
    args = p.parse_args()
    score = json.loads(args.score.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    for filename, stock in [('Cloudstairs_100BPM_Piano.flp', False),
                            ('Cloudstairs_100BPM_Piano_FLKeys.flp', True)]:
        target = args.out / filename
        repair(args.source, target, score['notes'], score['sections'], stock_piano=stock)
        print(target)


if __name__ == '__main__':
    main()
