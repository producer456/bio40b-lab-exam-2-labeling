#!/usr/bin/env python3
"""Build preview/ — a self-contained second instance of the study tool whose
PRESET_KEYS come from an exported localStorage snapshot instead of gen.py.

The preview uses its own localStorage prefix so it cannot see or clobber the
live page's saved work (both are served from the same github.io origin, and
localStorage is per-origin, not per-path).

    python3 build_preview.py "~/Downloads/Bio exam pt 2 answr.json"
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'preview')
PREFIX_OLD = 'bio40b_labexam2_'
PREFIX_NEW = 'bio40b_labexam2_preview_'


def grab(src, name):
    """Pull a top-level `const NAME = <literal>;` out of data.js as Python data."""
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


def main():
    export_path = os.path.expanduser(sys.argv[1])
    data_src = open(os.path.join(HERE, 'data.js')).read()

    IMAGE_ORDER, _, _ = grab(data_src, 'IMAGE_ORDER')
    IMAGE_DATA, _, _ = grab(data_src, 'IMAGE_DATA')
    OLD_KEYS, pk_start, pk_end = grab(data_src, 'PRESET_KEYS')

    payload = json.load(open(export_path))
    markers = json.loads(payload[PREFIX_OLD + 'markers'])

    new_keys, report = {}, []
    for station in IMAGE_ORDER:
        placed = markers.get(station, [])
        # Descriptions live in the old key, not in the export — graft by term.
        funcs = {m['word']: m.get('func') for m in OLD_KEYS.get(station, [])}
        terms = set(IMAGE_DATA[station]['words'])

        pins, dropped = [], 0
        for m in placed:
            if not m.get('word'):        # never labeled — cannot be part of a key
                dropped += 1
                continue
            pins.append({
                'id': m['id'],
                'x': m['x'],
                'y': m['y'],
                'labelDx': m.get('labelDx', 0),
                'labelDy': m.get('labelDy', 5),
                'word': m['word'],
                'func': funcs.get(m['word'], ''),
            })

        if not pins:                     # nothing usable — keep the generated key
            new_keys[station] = OLD_KEYS.get(station, [])
            report.append((station, 0, dropped, sorted(terms), 'KEPT OLD KEY'))
            continue

        used = [p['word'] for p in pins]
        missing = sorted(terms - set(used))
        note = ''
        if dropped:
            note = 'dropped %d unlabeled pin(s)' % dropped
        if missing:
            note = (note + '; ' if note else '') + 'no pin for: ' + ', '.join(missing)
        new_keys[station] = pins
        report.append((station, len(pins), dropped, missing, note))

    # ---- emit preview/data.js: same file, new PRESET_KEYS, images one level up
    banner = ('// Answer key captured from the exported localStorage snapshot\n'
              '// (%s) — these are the hand-placed pins, not gen.py output.\n'
              % os.path.basename(export_path))
    out_data = data_src[:pk_start] + json.dumps(new_keys, indent=2) + data_src[pk_end:]
    # The old explanatory comment above PRESET_KEYS no longer describes the source.
    out_data = out_data.replace(
        '// Pre-verified answer key. Loaded on first run; the teacher can\n'
        '// re-pin anything and Save to override it in localStorage.\n',
        banner)
    out_data = out_data.replace('"src": "images/', '"src": "../images/')

    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'data.js'), 'w').write(out_data)

    # ---- app.js: isolate storage so the preview can't touch the live save
    app_src = open(os.path.join(HERE, 'app.js')).read()
    n = app_src.count("'" + PREFIX_OLD)
    open(os.path.join(OUT, 'app.js'), 'w').write(
        app_src.replace("'" + PREFIX_OLD, "'" + PREFIX_NEW))

    # ---- index.html: same page, plus a banner so the two are never confused
    html = open(os.path.join(HERE, 'index.html')).read()
    html = html.replace('<title>BIOL 40B — Lab Exam 2 Labeling</title>',
                        '<title>PREVIEW — BIOL 40B Lab Exam 2 Labeling</title>')
    html = html.replace('<body>', '<body>\n    <div class="preview-banner">'
                        'PREVIEW BUILD — answer key = your saved pins. '
                        'Separate storage from the live page.</div>')
    open(os.path.join(OUT, 'index.html'), 'w').write(html)

    css = open(os.path.join(HERE, 'styles.css')).read()
    css += """
/* Preview build only — keeps this instance visually distinct from the live page. */
.preview-banner {
    background: #b45309;
    color: #fff;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.02em;
    text-align: center;
    padding: 6px 12px;
}
"""
    open(os.path.join(OUT, 'styles.css'), 'w').write(css)

    # ---- report
    print('preview/ written — storage prefix %s (%d references rewritten)\n' % (PREFIX_NEW, n))
    print('%-22s %4s %s' % ('station', 'pins', 'notes'))
    for station, count, dropped, missing, note in report:
        print('%-22s %4d %s' % (station, count, note))
    total = sum(len(v) for v in new_keys.values())
    print('\n%d stations, %d pins total' % (len(new_keys), total))


if __name__ == '__main__':
    main()
