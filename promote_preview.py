#!/usr/bin/env python3
"""Promote preview/data.js's PRESET_KEYS into the live data.js.

Copies only the key — image paths, IMAGE_DATA, and everything else in the live
file stay as they are.

    python3 promote_preview.py
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def grab(src, name):
    i = src.index('const %s = ' % name) + len('const %s = ' % name)
    start, oc = i, src[i]
    cc = {'{': '}', '[': ']'}[oc]
    depth, instr, esc = 0, False, False
    for j in range(i, len(src)):
        c = src[j]
        if instr:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c == oc:
            depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0:
                return json.loads(src[start:j + 1]), start, j + 1
    raise SystemExit('unterminated literal for %s' % name)


live_path = os.path.join(HERE, 'data.js')
prev_path = os.path.join(HERE, 'preview', 'data.js')

live = open(live_path).read()
prev = open(prev_path).read()

new_keys, _, _ = grab(prev, 'PRESET_KEYS')
old_keys, start, end = grab(live, 'PRESET_KEYS')
IMAGE_ORDER, _, _ = grab(live, 'IMAGE_ORDER')
IMAGE_DATA, _, _ = grab(live, 'IMAGE_DATA')

# Guard: never promote a key that is missing a station, a term, or a description.
for station in IMAGE_ORDER:
    pins = new_keys.get(station)
    if not pins:
        raise SystemExit('station %s has no pins — refusing to promote' % station)
    words = [p['word'] for p in pins]
    if len(words) != len(set(words)):
        raise SystemExit('station %s has duplicate terms — refusing' % station)
    missing = set(IMAGE_DATA[station]['words']) - set(words)
    if missing:
        raise SystemExit('station %s missing pins for %s' % (station, sorted(missing)))
    blank = [p['word'] for p in pins if not p.get('func')]
    if blank:
        raise SystemExit('station %s missing descriptions for %s' % (station, blank))

shutil.copy2(live_path, live_path + '.bak')
out = live[:start] + json.dumps(new_keys, indent=2) + live[end:]
open(live_path, 'w').write(out)

# Sanity: the promoted file must still point at the live image directory.
check, _, _ = grab(open(live_path).read(), 'IMAGE_DATA')
bad = [k for k, v in check.items() if not v['src'].startswith('images/')]
if bad:
    raise SystemExit('image src broken for %s' % bad)

moved = sum(1 for s in IMAGE_ORDER for a, b in
            zip(sorted(old_keys.get(s, []), key=lambda m: m['word']),
                sorted(new_keys[s], key=lambda m: m['word']))
            if (a['x'], a['y']) != (b['x'], b['y']))
print('promoted %d stations, %d pins (%d repositioned vs the old key)'
      % (len(new_keys), sum(len(v) for v in new_keys.values()), moved))
print('backup: data.js.bak')
