# Engine-Ausbau vor dem Bank-Video (keine Credits)
Vorhanden: sweat, tears, anger, hearts($), steam, rain, confetti, bills, num, stamp, chip, app (Handy), paper, quote, bars, grid, label, flash, dim, cursor, wire (Fluss), circle, pins, belt, bubble.

Neu bauen (Reihenfolge nach Wirkung, research/visual_elite.md):
1. emote: Symbol am Kopf eines Akteurs (! ? $ ... Herz, Schweiß), folgt dem Akteur (posAt + Höhe), Pop-Animation, SFX pop.
2. snap: Snap-Zoom auf ein Gesicht für 12-15 Frames (cam-Helfer in spec.py: s.snap(t, actor)).
3. Leben: Atmen (scaleY 1.0-1.012, 90-Frame-Zyklus) für jeden stehenden Akteur, Kopf-Nicken beim Sprechen (rotate ±1.5° an Lautstärke), Landestaub nach hop.
4. Text-Animationen: slam (Zahl knallt mit Schatten und Shake), strike (Wort wird durchgestrichen), marker (Highlighter-Wisch hinter Text).
5. ladder: Overlay-Leiter mit 7 Sprossen rechts, aktive Sprosse leuchtet in Level-Farbe, bleibt pro Level sichtbar.
6. split: geteilter Bildschirm links/rechts mit zwei Sets und eigener Farbstimmung.
7. grade: Farbstimmung pro Szene (filter: Tönung + Vignette) je Level: L1 kaltes Blau-Grau, L2 Neon-Grau, L3 Tageslicht, L4 warm, L5 Holz/Bernstein, L6 Goldene Stunde, L7 Gold/Marmor.
8. coins: Münzen fließen entlang eines Pfads in Gruppen (für "wer zahlt": Münzen rollen zu den 9 roten Figuren / nach oben).
9. hold: Gegenstand in der Hand eines Akteurs (folgt Hand-Anker aus box.json).
10. Übergänge: Zoom in den Bildschirm (Handy -> Szene), Wischblende.
