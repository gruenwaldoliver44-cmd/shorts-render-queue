# mc-engine – Money Classics Cartoon-Engine (Stand: Banken-Video, 9.11.2026)

Komplette Engine des Videos „How Banks Treat You at Every Level of Wealth ($0 to $50M)“ (9:38, privat hochgeladen 9.11.2026). Goldstandard für weitere Longform-Videos.

## Inhalt
- `engine/` – Remotion-Projekt + Python-DSL
  - `src/Main.jsx` Renderer (Sets, Figuren, Mundbewegung, Kamera, Overlays). Neu im Banken-Video: `phone`, `ladder`, `screen`, `acct`, `cmp`, `toggle`, `slam`, `strike`, `clock`, `ttl`, Emote-Glyphen an Figuren (`emo`).
  - `src/sprites.json`, `var.json` (Mund-Varianten), `mouth.json`, `timeline.json`
  - `hdr.py` (Sets, Farbstimmungen, Helfer `teller`, `cust`, `ladder`, `phone`, `screen`, `slam`, `emo`) + `body.py` (Regie pro Zeile) → `cat hdr.py body.py > scenes.py`
  - `spec.py` (DSL), `build.py` (Timeline + Stimmenmix + SFX), `audio_lib.py`, `music.py`, `stills.mjs` (Kontrollbilder)
  - `public/` alle Sets (`s_*.jpg`), Vordergrund `fg_window.png`, Figuren und Requisiten (`js_ gl_ er_ rp_ pr_ wt_ nu_ fl_ en_ wh_ ks_ kid_ ex_ pp_`), `__c`-Varianten mit geschlossenem Mund
  - `v/001–097.mp3` alle Stimmen
- `assets_src/` – Originalbögen von Higgsfield (`c_*` Figuren, `m_*` geschlossene Münder, `sets/s_*`), `jobs.txt` (Higgsfield-Job-IDs als Stilreferenz), `cut.py` (Schneiden), `seg.py`, `mo_bk.py` (Mund-Script), `box.json`
- `voices/` – `voice_settings_script.py` (Stimmen-Zuordnung V=… und Tags), `vb7/` Batch-Requests (elevenlabs_v4, max 7 pro Batch)
- `music/` – `score.py`, `musik-regeln.md`, `pieces.json`; die Cues des Videos liegen in `engine/cues.json` (MP3-Bibliothek liegt auf dem Mac in ~/ShortsRenderAgent/music/lib)
- `sfx/` – alle SFX-MP3s, die `audio_lib.py`/`build.py` erwarten
- `docs/` – finales Skript, Welt, Engine-Ausbauliste, Beschreibung, Tags

## Stimmen (elevenlabs_v4, preset)
NARRATOR Mark 27c04473-84a9-4b60-a41f-c8e8458bd4f1 (mit Emotions-Tag), JESS Zoe, GLORIA Mabel, EARL Barrett, PRUITT Sterling, KESSLER Julian, PHONE VOICE Vesper, OLD ENGINEER Gideon, WAITRESS Roxie, NURSE Kevin, FLORIST Delia, REP Hallie. Nebenrollen ohne Klammer-Tags. Telefonstimmen über `PHONE` in build.py gefiltert.

## Ablauf
1. In `engine/`: `npm install` (Remotion), Pfade anpassen: `audio_lib.py` und `build.py` lesen SFX aus `/home/claude/ys/sfxk/pick/` → auf `../sfx/` umstellen; `stills.mjs` serveUrl auf `work/bundle`.
2. `cat hdr.py body.py > scenes.py && python3 build.py`
3. Musik: `python3 ../music/score.py . cues.json work/final.m4a` (Musik ~16 dB unter Stimme)
4. `npx remotion bundle src/index.jsx --out-dir work/bundle`, Kontrollbilder: Frames in `work/all.txt`, `node stills.mjs .25`
5. Rendern auf dem Mac über die Queue (Bundle + mixm.m4a packen, Job wie 2669-bk-render2).

## Kosten Banken-Video
Higgsfield ca. 120 Credits (21 Bilder à 2, 97 Stimmzeilen ≈ 46, Thumbnails), Render auf dem Mac ca. 6 Minuten.
