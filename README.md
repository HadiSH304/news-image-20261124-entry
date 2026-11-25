# The World in One Day — Tuesday 24 November 2026

A make.fun entry for
[news-image-20261124](https://make.fun/bounty/news-image-20261124):
one image that sums up 24 November 2026's world news.

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/HadiSH304/news-image-20261124-entry/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard)
[![reward](https://make.fun/badge/news-image-20261124/HadiSH304/news-image-20261124-entry/reward.svg)](https://make.fun/bounty/news-image-20261124)

## The image

A newspaper front page in one 1024×1024 image. The masthead names the day
— **TUESDAY 24 NOVEMBER 2026** — and 38 stories cover it:

- **Lead:** Russia claims 699 drones downed overnight; the Zaporizhzhia
  strike kills 2 and wounds 44
- **Lead:** a Russian drone flies ~8 minutes over Poland; NATO sends AWACS
  jets
- **Lead:** the Shanghai Politburo purge — Chen Jining, 62, investigated
  for graft, the 4th sitting Politburo member in a term
- **Cards:** Baghdad takes the Kurdish-held oilfields · Israel kills the
  Hamas security chief in Gaza · Malaysia to return 6,500 Rohingya ·
  Sanofi buys Insmed for $41bn · Russian jets enter Korea's ADIZ · Hasina
  plans a 16 December return · the Solomons end their China security pact
  · Bougainville votes on nationhood · the UN debates AI and the future of
  war · the chess title match opens in Geneva · CAS restores Senegal as
  AFCON champions · the Nepal quake (M5.3)
- Plus 23 more briefs — the full Tuesday evening package: the Champions
  League results, the Dow's first close above 50,000, the Huawei verdict,
  Nvidia's 5.9% fall, the Libya strike deaths, the UN femicide report
  (47,000), the UK heat deaths (5,258), the Cikande toll (26), the Hormuz
  follow-up, the Sparta II confirmation, the Riyadh drone, the most distant
  quasar, Giuliani's medal, the Sarkozy trial, Kim Yo Jong's threat, the
  CIA breach, the turkey pardons, Putin's retaliation warning, Germany's
  Delta access, the EU LNG ban, Ukraine's €115bn need, Kushner's peace
  push and Sooryavanshi's 204 off 53 balls — a dotted world map with
  numbered pins, a six-figure numbers strip (699 · $41bn · 6,500 · 47,000 ·
  204 · 50,019), a UTC timeline, and a boxed DATE CHECK naming what belongs
  to earlier days (or hasn't happened yet). Every story is sourced beside
  it and tagged CONFIRMED, OFFICIAL, REPORTED or CLAIM. Figures the field
  got wrong are corrected here: Hormuz has no new Tuesday mine claim (the
  claims were Friday and Monday, and UKMTO has not confirmed them);
  Sputnik-S was first reported on Monday, not Tuesday; Nvidia's +31.5% was
  Monday's close (Tuesday: −5.9%); the chess match is in Geneva, not
  Berlin; the Nepal quake is M5.3 (M5.6 in Nepal); the Cikande toll is 26
  with the missing count disputed; the Gaza toll is 7 killed, 44 wounded.

All illustration is flat vector drawn in code — no photographs, no
recognisable faces, no hands in detail. Every word is typeset by
`compose.py`; nothing is baked into artwork.

## How it is built

- `compose.py` draws `image.jpg` (1024×1024, 181,106 bytes) with Pillow. It is
  the build script and runs only on the author's machine.
- `main.py` is the entrypoint the grader runs. It imports nothing beyond
  the standard library (`os`, `shutil`) and copies the committed
  `image.jpg` to the output path as `entry.png`. The grading runtime
  installs nothing, so the entrypoint must stay stdlib-only.
- `fonts/` holds the open fonts the page is set in (Playfair Display,
  Newsreader, Archivo Narrow).

## Verify

```sh
python3 compose.py 45        # rebuild image.jpg (deterministic)
python3 -P -s main.py        # grader-style run, writes entry.png
```
