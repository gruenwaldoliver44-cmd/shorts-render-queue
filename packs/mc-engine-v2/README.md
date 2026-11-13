# mc-engine-v2 – Money Classics Standard (Weltkrise-Video, 12./13.11.2026)

Das ist der **Mindeststandard** für jedes Longform-Video. Referenz: „What If the AI Bubble Finally Crashed the World Economy?“ (11:38, youtu.be/EobQcF2A5-I). Ablauf und Regeln: Projekt-Doc `claude/video-pipeline.md` (Base v2). Nichts darunter darf wieder schlechter werden.

## Inhalt
- `engine/` Remotion 4.0.540 + Python-DSL
  - `spec.py` DSL (S/A/R), `scenes.py` Regie aller Zeilen (GLOB, direct(), M() für MG-Seiten, Helfer mg/wo/tick/chap/hud/term/icons/chips/stat/tagl/mapw/say/wipe/glitch)
  - `build.py` Timeline + Stimmenmix + SFX (GAP, PHONE), `audio_lib.py`, `music.py`, `sfxgen2.py` (55 synthetische SFX → `sfx/`)
  - `src/Main.jsx` Renderer (Sets, Figuren, Münder, Türen mit roll/shutter, Overlays, sc.win, sc.ocam, sc.wo), `src/mg.jsx` Motion-Graphics-System „MONEY CLASSICS OPS“ (alle MG-Bausteine), `theme.js`, `ui.jsx`
  - `src/sprites.json` (inkl. Höhenfaktor SP[n][2]), `var.json` / `mouth.json` (Münder), `timeline.json`
  - `public/` Sets, Figuren (`__c` = geschlossener Mund), Vordergründe `fg_*`, Flaggen, Weltkarte, Fonts
  - `v/001–057.mp3` Stimmen, `vb_*.json` Stimmen-Batches (elevenlabs_v4), `lines.json`, `cues.json` (Musik)
  - `audit2.py` Lücken-Detektor, `stills.mjs` + `sheet.py` Kontaktbögen, `bundle.mjs`, `tools_fg.py`
- `sfxk/` Kenney-Samples (Türen, Schritte, Münzen …)
- `tools/` `cut2.py` (Bögen schneiden, NICHT erneut über fertige sprites.json laufen lassen), `seg.py`, `mo2.py` (Mundvarianten), `mpaint.py` (Mund-Reparatur), `box.json`
- `music/` `score.py`, `musik-regeln.md`, `pieces.json`, `analyse.py`
- `docs/` Skript v11/final, Produktionsplan, Checkliste, Story-Sheet, Regieplan, Kaltleser- und Faktenprüfung, Hooks, Beschreibung
- `mg-probe/` Stilprobe des MG-Systems
- `brand/` Kanal-Logo 5b (gelbes MC auf Navy) + Generator

## Wiederherstellen (geprüft 13.11.2026: build.py liefert identische Dauer 697,4 s)
```
cd engine && npm i                     # Versionen fest in package.json
python3 build.py                       # scenes.py -> src/timeline.json + work/mix
python3 ../music/score.py . cues.json work/final2.m4a   # Musik (Bibliothek: Mac ~/ShortsRenderAgent/music/lib)
node bundle.mjs && node stills.mjs .4 && python3 sheet.py 4 16
python3 audit2.py 3                    # Ziel: 0 Lücken > 4 s
```
Rendern: Bundle → tgz → 14-MB-Teile → `device_commit_files` nach `~/ShortsRenderAgent/pilot_test/film/` → Job-JSON (Vorlage 2672-wk-render). Nie Schlüssel oder signierte Links ins Repo.
