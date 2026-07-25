# BIOL 40B — Lab Exam 2 Labeling

A free, browser-based labeling study tool for BIOL 40B Lab Exam 2
(cardiovascular and respiratory systems). 19 stations, 121 structures.

Made by students, for students — this is a study aid, not official course
material, and it is not affiliated with or endorsed by the instructor.

Everything runs client-side. No server, no build step, no accounts, no
tracking — open `index.html` and it works, including offline once loaded.

## Modes

**Student Mode** — each station shows numbered pins and a word bank. Drag a
term onto a pin, or tap a term then tap a pin.

**Only the correct term will stick.** A wrong one bounces back with a red shake
and stays in the word bank, so you can't leave a station holding a wrong answer.
Correct answers lock in green. The station scores itself once every pin is
filled, reporting first-try accuracy and how many wrong drops it took.

**Teacher Mode** — the correction mode. Every station arrives pre-pinned from a
verified answer key; this is where we fix a pin that points at the wrong thing.

- **Drag a pin** to correct where it points
- Drag a label to move it (the leader line follows its pin)
- Tap the image to add a pin; tap **X** to remove one
- Tap a term, then a pin's label, to assign it
- **Save Answer Key** commits the station
- **You Make the Answer Key** blanks the station so you can pin it from
  scratch — a harder drill than correcting, and it sticks across reloads
- **Restore Original Key** discards your edits and brings the original pins back

Work is saved to `localStorage`, so it stays on the device it was entered on.
**Export Data** / **Import Data** move a key between devices.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Generated — edit `index_template.html` instead |
| `app.js` | The labeling engine (hand-written) |
| `styles.css` | Styles (hand-written) |
| `data.js` | Generated — stations, word banks, answer key, credits |
| `images/` | Generated — cropped and downscaled figures |
| `gen.py` | The generator |

`gen.py` rebuilds `images/`, `data.js`, and `index.html` from the source
practical materials. It reads a local build script that is **not** part of this
repo, so it will not run on a fresh clone — the generated output is committed so
the app works without it.

## Image credits

Figures come from several sources under different licences — several are
CC BY 4.0 / CC BY 3.0 / CC BY-SA 4.0, which **require attribution regardless of
how the app is used**. The full list is in the "Image credits & licensing"
panel at the bottom of the page, and in `CREDITS` in `data.js`.

Some figures' sources were not individually recorded. They are labelled as such.
If you hold the rights to one of them, please open an issue — it will be
credited or removed on request.

Because the figures carry their own licences, they are **not** covered by any
licence this repository might apply to its code.

## A note for students

The answer key ships in `data.js` in plain text, since the whole app runs in the
browser. It is a study aid, not an assessment tool — nothing here is secret from
anyone willing to open the file.
