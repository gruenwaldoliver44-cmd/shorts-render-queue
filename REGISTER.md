# HARD RULES (Oliver, 30 Oct 2026, read first, every video)
1. Every video is built on a verified 1M+ view template (link + views). The script may copy its structure 1:1; no template, no start.
2. The start decides: visual hook and spoken hook in the first 1-3 s are checked against the template's first 3 s before anything else is built.
3. Benchmark is the template, never our own best video (5k views is not a target).
4. Up to 6 h per video, maximum Blender quality; the Mac may render non-stop.
5. Simple and clear: one idea, explained so a non-native 14-year-old gets it.
6. Before posting, an independent agent without my context compares hook, script, visuals and clarity against the template. Fail = no post.
7. Never repeat a topic already posted (check Metricool history).
9. BlenderKit (paid, ~80k assets, API key in the Mac's Blender addon) is ALWAYS used for every real object: download via the common_dl.py helper in earlier jobs (e.g. jobs/2113-ct43-hero.json). Code primitives only for abstract graphics. Plus Poly Haven HDRIs for lighting.
10. Blender craft: every spoken sentence is shown as a logical physical action (the object does what the words say, on the word). Detailed, real-scale scenes, cinematic camera moves that follow cause and effect, no floating cards, no generic dark void. If a still looks like it could be made by code, redo it.
11. Each channel gets its OWN concept, own reference creators and own visual language (characters/people, objects, archive, 3D: whatever fits that channel). The four videos must not look alike. Sound design and cut rhythm are part of the concept.
8. Topics are not limited to one family: pick the most fascinating topic available (strongest curiosity + share pull), then execute it perfectly. Our own data only hints at direction.

# VIDEO REGISTER: Pflicht vor JEDEM Skript und vor JEDEM Post lesen

Oliver, 30 Oct 2026: "keine Ausreden … stell sicher, dass du es nicht vergisst. Bei jedem Mal wieder."

## A. Hook-Checkliste (jeder Punkt muss JA sein, sonst neu schreiben)
1. Satz 1 = die unglaublichste WAHRE Tatsache des Themas (Zahl, Paradox, Verrat). Kein Kontext, kein Name-Dropping, keine Story-Einleitung ("X hat einem Mann ein Versprechen gegeben" = abgelehnt, FT 30 Oct).
2. Psychologischer Hebel (mind. 2): Ungerechtigkeit ("zwei Leute, gleiche Eier, einer zahlt mehr"), Gefahr für DEIN Geld/Gerät, Paradox ("um es leiser zu machen, spielt es Lärm ab"), unmöglich wirkende Zahl, Bild im Kopf ("Imagine …"), offene Schleife.
3. Zuschauer ist betroffen: "your phone / your money / you" in Satz 1 oder 2.
4. Satz 2 eskaliert sofort (oder "Because …" → Mechanismus startet, wie scroll.engineer).
5. Offene Schleife bis zum Ende: eine Zahl / ein Twist wird ausdrücklich zurückgehalten ("But here's the really clever part").
6. Letzter Satz = Kommentar-Frage oder Echo des Hooks ("Would you pay $3,000 for that?").
7. Gesprochen wie zu einem Freund. Keine Nachrichtensprecher-Sätze, keine Rätsel, keine Idiome.
8. Hook-Bild steht in Frame 0 und bewegt sich; Event + SFX in der ersten Sekunde.

## B. Kanal-Spuren (nie verwechseln)
- MT: wie komplizierte Technik in Alltagsgeräten WIRKLICH funktioniert (Mechanismus Schritt für Schritt, technisch). Vorbilder: scroll.engineer, so.thats.how, app.engineering. Gern aktueller Aufhänger ("Apple's new MacBook has…").
- CT: Geld der Zuschauer JETZT – Fallen, Bösewichte, absurde Gebühren, Trends. Keine Spartipps.
- MC: eine Person, die ein Geldsystem legal geschlagen hat (Loophole) und wie die Firma zurückschlug; große Zahl bis zum Ende halten.
- FT: Zukunft des Geldes, wildeste Hypothesen, "Imagine…"-Hooks. Keine Vergangenheits-Geschichten als Kern, keine Zahlungsmechanik-Langeweile.

## C. Visual-Checkliste
1. Harter Schnitt / neuer Blickwinkel spätestens alle 2–3 s; dazwischen läuft die Kamera immer (Push-in, Orbit, Rack-Focus).
2. Jedes Nomen / jede Zahl / jedes Verb bekommt sein Bild-Event auf dem Wort.
3. Motion-Graphics-Schicht über 3D: Monospace-Labels mit Leader-Lines und Klammer-Markern ("SCHEMATIC · NOT TO SCALE"-Stil), große weiße Zahlen-Counter, Vergleichs-Splits (A vs B), Zeitraffer.
4. Makro-Welt: ins Innere zoomen (Pixel, Chip, Molekül, Datenpaket) – das ist das Spektakel.
5. Humor/Reaktion pro Video mind. 2x (Objekt reagiert, Gag, Timing-Pause).
6. Untertitel: 1 Zeile, sauber, Wort-Highlight; nichts außerhalb 4:5.
7. Echtes Material (Logo/Produktfoto) mit Quellen-Label klein im Bild.

## D. Was nachweislich funktioniert (Praxis-Daten)
- so.thats.how (IG, 95k): Spülmaschine 8,7 Mio, Waschmaschine 1,4 Mio, Rest 5–130k → Alltagsgerät + Inneres zeigen.
- scroll.engineer DfD9E4lqq8w (Oliver-Beispiel 30 Oct): Hook "Apple's new MacBook has TWO layers of OLED pixels." → "Because the brighter an OLED gets, the faster … wear out" → Mechanismus → "That's how burn-in happens" → Lösung → "But here's the really clever part" → Ende "Would you pay almost $3,000 for that?". 78 s, Schnitt alle ~2,5 s, dunkle Makro-Welt, Monospace-Labels, große Zahlen (2,000 nits, <1ms), Quelle im Bild.
- Eigene: CT Bankomat bestes Video (24k TikTok).

## E. Abgelehnte Hooks (nie wieder so)
- FT 30 Oct: "Air Canada hat einem Mann ein Versprechen gegeben…" – langweilig, Vergangenheit.
- MC 30 Oct: Pepsi-Hook langweilig erzählt.
- MT 30 Oct: Listening – erste Sekunden langweilig.

## F. Wiederkehrende Fehler (vor Render prüfen)
- Presigned-URLs laufen nach ~8 h ab → kurz vor Upload neu holen.
- plane(): transform_apply nur Scale.
- Modifier-Count-Keys animieren nicht → Einzelobjekte + vis.
- loudnorm: aformat s16 stereo davor.
- Kein pkill -f mit eigenem Pattern.

## Posted 30 Oct 2026
- 13:55 CT Instacart (2540) IG+TT+YT. Hook: "You and your neighbor order the exact same crackers... you pay 23% more". Metrics due 1 Nov.

## G. IG analysis 30 Oct (Metricool, all reels since 12 Oct)
- Two clusters: ~1,300–2,000 views (normal) and ~100–200 (dead). Almost nothing breaks out above 3k.
- Step change around 16 Oct: CT and MC went from ~100–200 to ~1,500 when topics switched from trivia/"watch till the end" to concrete money stories. That was real progress.
- 3-s view rate is mostly 65–80%, so the hook already works OK. The ceiling is shares: almost always 0–3.
- Top CT: pump hold $150 declined for $20 (5,695), restaurant tip hold (4,245), invest 38 vs 8 years (3,775), bank drilled safe deposit box (3,435). All: the viewer's OWN money frozen or taken, in a situation they know.
- Top MT: dishwasher (3,365), smart TV screenshots (2,950). Top MC: KFC Colonel sues (2,577), Archegos (2,509), Fort Knox (2,458).
- Blender premium (24–29 Oct) did NOT beat the cheap Remotion videos. Visual effort is not the lever right now.
- Rule: topic and share trigger first (would I send this to a specific person?), visuals second.
