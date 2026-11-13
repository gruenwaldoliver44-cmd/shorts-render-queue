# Produktionsplan Weltkrise-Video („What If the AI Bubble Crashed the Whole World? Who Survives?“)

Stand 12.11.2026. Grundlage: Skript v11 (57 Zeilen, ca. 11:45). Dieser Plan wird vor jedem Bau abgehakt.

## A. Lehren aus den letzten Videos (Analyse der Banken-Timeline)
- Im Banken-Video gab es Szenen mit nur 0,4–0,6 Bildereignissen pro Sekunde: dunkler Hintergrund plus 3 Einblendungen über 10–14 s. Dazu kamen Einstellungen auf einem Set von bis zu 21 s, und Figuren standen mit nur einer Position durch eine ganze Szene. Genau so entsteht das Gefühl „steht still“.
- Im Bankpleite-Video stand eine Figur eine Minute regungslos am Bankomaten, die Zahlen flogen ohne Erklärung ein, und Angestellte kamen „aus der Wand“.
- Bei einigen Figuren waren weiße Ränder nicht sauber ausgeschnitten.
- **Neue harte Prüfwerte (gemessen, nicht gefühlt):**
  1. Spätestens alle 2 s gibt es eine sichtbare Veränderung: neues Element, Schnitt, Kamerabewegung, Figurenaktion oder Zahlenwechsel.
  2. Keine Einstellung ist länger als 8 s ohne Schnitt oder Kamerawechsel.
  3. Jede sichtbare Figur macht mindestens alle 4 s etwas: geht, dreht sich, gestikuliert, setzt sich, reagiert, oder ihr Mund spricht.
  4. Jede Zahl, die gesprochen wird, steht im passenden Feld, und zwar im Wortmoment (±6 Frames).
  5. Kein Text überlappt einen anderen und keiner läuft aus seinem Kasten. Die Prüfung läuft automatisch per DOM-Messung im Render, dazu prüfe ich die Kontaktbögen per Auge.
  6. Ausschnitt-Ränder: Jede Figur wird mit 1-px-Erosion plus Entsäumung (Defringe) freigestellt. Kontrolle als 200 %-Crop auf dunklem und hellem Grund, bevor sie ins Set kommt.
- **QA-Ablauf nach jedem Render:** Ein Skript sucht stehende Strecken über die Pixel-Differenz zwischen Frames, Schwelle 2 s. Dazu kommt ein Kontaktbogen alle 1,5 s über die ganze Länge, den ich komplett ansehe, nicht nur den Anfang. Ein unabhängiger Kritiker bewertet die Bögen ohne Kenntnis meines Plans.

## B. Recherche Motion Graphics: Werkzeuge und Entscheidung
| Option | Was es ist | Bewertung für uns |
|---|---|---|
| Remotion Agent Skills (offiziell, schon installiert) | React-Videos, Übergänge, Karten, SFX-Regeln | Basis, weil unsere Engine Remotion ist |
| remotion-motion-graphics-skill (Liam Johnston, MIT) | Gate mit Recherche, Referenz-Prüfung, unabhängigem Kritiker; „cinematic camera“: eine große Welt, durch die die Kamera fährt | Übernehme die Methode: eine zusammenhängende Welt, Bewegung zeigt Ursache und Wirkung, wenige große Fokus-Objekte, kein Erzähltext doppelt im Bild, Kritiker-Gate mit Note ≥ 8. Den „Null-Neon“-Look übernehme ich NICHT 1:1, weil du futuristisch willst. Kompromiss: Akzente flach und scharf, Glow nur auf dem einen Fokus-Element |
| HyperFrames (HeyGen, Apache-2.0) | HTML/CSS-Animationen zu MP4 | Kein Vorteil gegenüber Remotion, zweite Engine wäre unnötiges Risiko |
| AutoAE | Fertige Template-Clips gegen Credits | Kostet extra, und Template-Look passt nicht zu unserem Kanal |
| OpenMontage | Komplett-Pipeline, AGPL | Zu schwer, wir haben unsere eigene |
| d3-geo + world-atlas + flag-icons (npm, frei) | Vektor-Weltkarte offline, echte Ländergrenzen, Flaggen als SVG | Übernommen: Weltkarte als roter Faden, Kamera fliegt von Stadt zu Stadt |
| SFX | Externe SFX-Seiten sind im Netz blockiert | Eigene SFX-Familie per Synthese erzeugt: Whoosh, Swish, Tick, Ziffern-Rollen, Blip, Pop, Impact, Slam, Riser, Glitch, Scan, Warnton, Herzschlag, Münze. Dazu die vorhandene Kenney-Bibliothek (Türen, Schritte, Münzen, Glas) |

## C. Designsystem „MONEY CLASSICS OPS“
- **Welt:** tiefes Navy (#070B16 → #0C1326), feines Raster, das langsam driftet, Vignette.
- **Farben mit fester Bedeutung:**
  - Cyan #38E1FF = Geld fließt
  - Amber #FFB224 = Warnung/Kosten
  - Rot #FF3D57 = Verlust/Crash
  - Grün #2FE6A0 = Schutz/Gewinn
  - Gold #F5C451 = Gold
  - Weiß #EEF2FF = Text
- **Schrift:** Space Grotesk für Überschriften und Definitionen, JetBrains Mono für Zahlen und Labels (Zahlen rollen hoch und runter).
- **Bausteine:**
  - HUD-Panel mit Eckwinkeln
  - Geld-Zähler
  - Begriffs-Karte, die Fachwörter in einem Satz erklärt (IOU, S&P 500, Zentralbank, Zoll, Sicherheit für den Kredit)
  - Weltkarte mit Städten und Flaggen, Bögen und Pulsen
  - Preis-Durchstreichen
  - Balken und Anteile
  - Tacho
  - Icons (Haus, Auto, Karte, Brot, Schiff, Bank)
  - Kassenbon
  - Länder-Scoreboard
  - Zeitstrahl
- **Bewegung:** Einblendungen schnell in 8–12 Frames mit Ease-Out-Expo, Kamerafahrten in 14–24 Frames mit Ease-In-Out. Übergänge laufen als Scan-Linie, beim Crash kommt ein kurzer Glitch-Slice, bei Wechsel zwischen Städten ein Whip.
- **Sound:** Jede Bewegung hat ihren festen Ton. Einblendung = Pop oder Blip, Übergang = Whoosh, Zahl rollt = Ziffern-Ticks, Crash = Impact plus Glitch, Stempel/Slash = Slam, Spannung = Riser.
- **Durchgehende rote Fäden:**
  1. HUD „YOUR RETIREMENT FUND“ oben rechts, wann immer sich der Betrag ändert.
  2. Domino-Weltkarte: Jede Stadt, die fällt, bleibt rot.
  3. Kalender/Uhr: „DAY 1 · DAY 2 · WEEK 1 …“ als Kapitel-Ticker oben links.
- **Stilprobe:** /home/claude/ys/wk/mg/out/probe.mp4 (26 s), gerendert ohne Credits. Sie zeigt Uhren mit Crash, Chip-Kredit mit Preissturz, S&P-Balken mit Fonds-Zähler, Weltflug mit Begriffs-Karte „IOU“ und Zins-Tacho, der die drei Kredite teurer macht.

## D. Mischung Szene ↔ Motion Graphics (je nach Bedarf)
| Teil | Zeilen | Anteil Szene / MG | Warum |
|---|---|---|---|
| Hook | 1–3 | 20 / 80 | Weltweiter Blick, Uhren, Globus – nur MG zeigt alle Städte gleichzeitig |
| Welt am Rand + Corvane | 4–9 | 50 / 50 | Lagerhalle als echte Welt, Kreditmechanik als MG darüber |
| Tokio | 10–14 | 50 / 50 | Trader-Szene; Kreislauf Yen → Aktien und Zins → deine Kredite als MG |
| Mumbai Gold | 15–18 | 70 / 30 | Juwelier-Szene trägt, Gold-Ticker als Overlay im Laden-Bildschirm |
| Dollar + Kairo | 19–23 | 50 / 50 | Dollar-Wippe als MG, Bäckerei als Szene |
| Shanghai + Ohio Jobs | 24–28 | 60 / 40 | Schiff, Lager, Laptop-Call als Szenen, Lieferkette als MG |
| Bank | 29–33 | 60 / 40 | Bank-Tür als Szene, Schutzschild und Karte 1931 als MG |
| Zölle | 34–36 | 40 / 60 | Kassenbon als MG über der Kassen-Szene |
| Rally + Frage | 37–40 | 20 / 80 | Chart 1929 und dein Zähler als MG, die Frage groß im Bild |
| Geld wertlos? | 41–44 | 30 / 70 | Goldmünze 1933 und schrumpfender Warenkorb als MG |
| Wer gewinnt | 45–50 | 15 / 85 | Länder-Scoreboard, Weltkarte, brennendes Haus |
| Gold-Wende | 51–53 | 20 / 80 | Goldstapel neben zwei Blauwalen, Russland friert ein, Weggabelung |
| Ende | 54–57 | 50 / 50 | Zeitstrahl, Elektriker-Szene, Hotel 1944 |

## E. Shotlist pro Zeile (Zeit grob bei 187 wpm)
Schreibweise: **SZ** = Higgsfield-Szene (Figur handelt), **MG** = Motion Graphic, **OV** = MG über Szene, **K** = Kamera, **SFX**.

1. **[1] Day one…** MG: Kapitel-Ticker „DAY 1 · MONDAY“. Drei Uhren (Tokio 23:29, London 14:29, NY 09:29) springen ein. Die NY-Uhr springt im Wort „open“ auf 09:30 und wird rot. Globus mit Lichtern, Risse laufen von NY aus. Erste 5 s stumm verständlich: Uhren ticken, Risse. SFX Tick ×3, Impact plus Glitch auf „fall apart“.
2. **[2] By the end…** MG: Weltkarte zoomt raus. „A FEW COUNTRIES IN RUINS“: drei Länder werden rot. „THE MONEY IN YOUR ACCOUNT?“: dein HUD-Zähler blinkt mit „?“ auf. „ONE COUNTRY ON TOP“: eine Fahne ohne Land steigt auf einen Trümmerhaufen und wird verdeckt. SFX Riser.
3. **[3] The company is made up…** MG: Stempel-Label „SCENARIO · CORVANE IS FICTIONAL“ und darunter „EVERY STEP AFTER: REAL“, mit Datums-Chips 1929 · 1931 · 2008 · 2024 · 2026, die einklicken. SFX Pop ×5.
4. **[4] World on edge…** MG: drei Warnkarten nacheinander, jede ca. 3 s:
   - Tanker vor Hormus mit Zapfsäulen-Zähler, der steigt
   - Zins-Pfeil „FIRST HIKE IN 3 YEARS“
   - Zähler „$466B+ AI DEBT 2026“, der auf „ALMOST $500B“ rollt

   K: seitliche Fahrt von Karte zu Karte. SFX Zapfsäulen-Klick, Blip, Ziffern.
5. **[5] Corvane…** SZ Lagerhalle Virginia: Totale mit Server-Gängen, Fahrt den Gang entlang. Ein Techniker schiebt einen Wagen mit Chips. OV: Chip-Icon, Kette, Panel „LOAN $12B · SECURED BY CHIPS“, Begriffs-Karte „SECURITY = what the lender can take if you stop paying“. SFX Server-Brummen, Pop.
6. **[6] 10:17 payment…** MG: Bank-Terminal-Zeile „INCOMING $400,000,000 · CORVANE“ → Ladebalken → „NOT RECEIVED“ in Rot, Uhr 10:17. Kurzer Schnitt: Rechnung des KI-Labors „UNPAID SINCE FRI“. SFX Scan, Fehler-Ton.
7. **[7] Lenders come for the chips…** SZ Lagerhalle: Tür geht auf, drei Verleiher mit Klemmbrett kommen herein, kleben rote Etiketten auf die Server-Racks, einer schüttelt den Kopf. OV: $40.000 → Slash → $5.000. K: Push-in auf das Preisschild. SFX Tür, Schritte, Slam.
8. **[8] Reaches you…** MG: S&P-Balken mit 7 Firmen = 36 % und Begriffs-Karte „S&P 500 = the 500 biggest US companies; most retirement funds own a slice of all of them“. Dann SZ deine Küche: „Du“ (junger Mann im Arbeitshemd) sitzt mit Sandwich am Tisch und öffnet die App. Der HUD-Zähler zählt $10.000 → $9.100 („lunch“) → $8.000 („Friday“), Kalender-Chip MON 12:10 → FRI 16:00. Die Figur hört auf zu kauen. SFX Handy-Vibration, Ziffern, Blip-down.
9. **[9] Remember that number…** OV: Der Zähler wird eingefroren, ein Rahmen „REMEMBER THIS“ und ein Schloss-Symbol bleiben als offene Schleife oben rechts stehen. K: langsamer Push-in. SFX Herzschlag einmal.
10. **[10] Detour through Tokyo…** MG: Whip über die Weltkarte NY → Tokio, der Bogen zeichnet sich, die Tokio-Fahne pulsiert rot, ein Icon „YOUR CAR LOAN“ wartet am Ende der Route. SFX Whoosh, Pop.
11. **[11] Borrowed yen…** MG: Kreislauf Yen-Sack (0 %) → umtauschen → US-Aktien → Pfeil zurück; dann bricht der Kreislauf, Pfeile drängen alle gleichzeitig zum EXIT. Begriffs-Karte „YEN = Japan's money“. SFX Swish, Glitch.
12. **[12] TRADER** SZ Börsensaal Tokio: Trader steht am Pult, hämmert auf die Tastatur, dreht sich zum Nachbarn, Hände hoch. Hintergrund: rote Bildschirme. Mund spricht, Sprechblase „So who's buying?“.
13. **[13] Nobody. Aug 5 2024…** MG: Archiv-Chart Nikkei am 5.8.2024 mit −12,4 % in einem Tag, als echte Linie mit Datum. SFX Impact.
14. **[14] Comes back to you…** MG: Japan-Fahne hält einen Stapel „US IOUs“. Begriffs-Karte „IOU = government bond: America owes you this money, plus interest“. Der Stapel wird verkauft, der Zins-Tacho steigt, Chip „Q1 2026: Japan sold ~$30B“. Dann drei Icons (Haus/Auto/Karte) mit Pfeil nach oben. Beispielwerte werden nur gezeigt, wenn sie berechnet und als „EXAMPLE“ markiert sind, z. B. +1 % Zins auf $300.000 Hypothek ≈ +$200/Monat. SFX Ratschen, Münze.
15. **[15] Day three…** MG: Kapitel-Ticker „DAY 3“, Goldbarren-Icon mit Schild „SAFE?“, das kippt. SFX Riser kurz.
16. **[16] Mumbai…** SZ Juwelier: Kundin (Sari, ältere Frau) tritt durch die Ladentür, legt eine Goldkette auf die Glastheke, schaut erwartungsvoll. Der Juwelier wiegt die Kette auf der Waage. K: Fahrt über die Theke. SFX Türglocke, Klirren.
17. **[17] JEWELER** SZ: Juwelier zeigt auf den Bildschirm hinter sich, der Kurs fällt zweimal (OV im Bildschirm). Die Kundin hebt die Augenbrauen nicht, sie wird traurig über Mund und Kopf. Sprechblase „Twice, since you walked in.“
18. **[18] Gold falling because…** MG: Kette Investor mit Kredit → „PAY BACK TODAY“ → verkauft Gold, schnellstes Bargeld; dann echter Gold-Chart Jan 2026 $5.589 → Okt 2026 unter $4.000 (−29 %). Am Ende das Icon „YOUR EMERGENCY PLAN: GOLD“ mit sinkendem Pfeil. SFX Ticker, Blip-down.
19. **[19] Week one, dollars…** MG: Kapitel-Ticker „WEEK 1“, aus allen Fahnen fließen Partikel zum Dollar-Zeichen. SFX Whoosh.
20. **[20] Dollar stronger…** MG: Wippe Dollar ↔ andere Währungen (€, ¥, ₹, E£); dann Fass Öl und Weizen mit „$“-Etikett; Zapfsäule und Einkaufswagen außerhalb der USA werden teurer. SFX Ratschen.
21. **[21] Cairo feels it first** MG: Weltkarte, Whip nach Kairo, Fahne pulsiert. SFX Whoosh.
22. **[22] BAKER** SZ Bäckerei Kairo: Der Bäcker wischt die alte Zahl von der Kreidetafel und schreibt 1.100. Mehlsäcke auf dem Boden, eine Kundin im Hintergrund schüttelt den Kopf. Sprechblase.
23. **[23] 2011…** MG: gezeichnete Zeitungs-Karte „JAN 25 → FEB 11, 2011 · 18 DAYS“ (keine echten Fotos), Brot-Icon wird zur Menge. Dann Schnitt: Kalender-Einladung ploppt auf deinem Handy auf. SFX Papier, Benachrichtigung.
24. **[24] Week three Shanghai…** MG: Hafenkarte Shanghai mit Schiffspunkten, die erlöschen, Kapitel-Ticker „WEEK 3“. SZ Schiffsdeck. SFX Schiffshorn.
25. **[25] CAPTAIN** SZ: Der Kapitän sitzt mit der Crew am Klapptisch auf dem Deck, Karten in der Hand, lehnt sich zurück. Zähler „DAY 18 AT ANCHOR“ an der Brücke. Sprechblase.
26. **[26] Fewer ships…** MG: Lieferkette Schiff → LKW → Lager → Jobs, jedes Glied erlischt nacheinander. SZ Lager Ohio: Nachtschicht-Schild wird abgehängt. Zähler „2008–2010: ~8.7M JOBS LOST“. SFX Ketten-Klick.
27. **[27] MANAGER** SZ deine Küche: Laptop mit Video-Call, Manager im Fenster, Titel „Quick sync · 15 min“. „Du“ klappt langsam den Mund zu. Sprechblase.
28. **[28] Is my money safe?** MG: Frage groß im Bild, dein Konto-Icon mit Fragezeichen. SFX Herzschlag.
29. **[29] Bank in Europe…** SZ Bank Frankfurt außen: Kunden gehen auf die Glastür zu, ein Mann rüttelt an der Tür, „CLOSED“-Schild. K: über die Köpfe zur Tür. SFX Türklinke.
30. **[30] TELLER** SZ: Die Kassiererin öffnet die Tür einen Spalt, spricht, schließt sie wieder. Sprechblase.
31. **[31] Honest answer…** MG: Schutzschild über einem Konto, „FDIC INSURED UP TO $250,000 PER PERSON PER BANK · PAID BACK USUALLY WITHIN DAYS“; Europa-Schild „€100,000“. Grüne Farbe. SFX Schild-Aufbau.
32. **[32] Paycheck…** MG: Ein Gehaltszettel liegt außerhalb des Schilds und hängt an der Firma, die bei der Pleitebank ist. Chip „MARCH 2023 · SILICON VALLEY BANK“, Kalender „FRIDAY PAYDAY?“ mit Fragezeichen. SFX Warnton.
33. **[33] 1931…** MG: Europakarte im Sepia-Look 1931, Funke in Wien (Creditanstalt), Panik-Wellen laufen nach Deutschland, Schloss-Symbole auf Banken. SFX Funkenknistern, Schlösser.
34. **[34] Month three, receipt** MG: Kapitel-Ticker „MONTH 3“, dein HUD fällt auf 7.500, Kassenbon schiebt sich ins Bild. SFX Ziffern, Bon-Drucker.
35. **[35] Taxes on foreign goods…** SZ Supermarktkasse: „Du“ legt Reis und Brot aufs Band. OV: Bon mit Zeilen „IMPORT TAX“, Begriffs-Karte „TARIFF = a tax on goods from other countries, paid at the checkout“. MG Karte Indien „RICE EXPORT BAN 2023“, Reis-Preis-Pfeil nach oben. SFX Kassen-Piepen.
36. **[36] World trade −⅔…** MG: Welthandels-Balken 1929 → 1933, schrumpft auf ein Drittel; dann Schnitt Kairo: eine Menge vor der Bäckerei (SZ, gleiche Bäckerei von außen). SFX Menge leise.
37. **[37] Good news, mistake** MG: Kapitel-Ticker „MONTH 4“, grüner Pfeil „GOOD NEWS“, darunter ein rotes Warn-Dreieck, das kurz aufblitzt. SFX Riser.
38. **[38] Central banks print…** MG: Druckerpresse-Icon, Begriffs-Karte „CENTRAL BANK = the bank that prints a country's money“, Chart +20 %, dein HUD auf 9.000, TV-Banner „THE WORST IS OVER“. SFX Ziffern, Jubel kurz.
39. **[39] 1929 too…** MG: echter Dow-Chart Nov 1929 → Apr 1930 (+48 %) → Juli 1932 (−86 %), unsere Rally liegt darüber und kippt; Auktions-Hammer „CORVANE CHIPS < $5,000“; dein HUD auf 6.000. SFX Hammer, Impact.
40. **[40] Would you sell?** MG: schwarzer Grund, nur dein Zähler $6.000 und die Frage „WOULD YOU SELL?“, 2 s Puls. Dann Chart „SELL HERE“ am Tiefpunkt, ein Bildschirm-Verlust wird zu „REAL LOSS“. Das Schloss „REMEMBER“ von Zeile 9 leuchtet kurz auf. SFX Herzschlag, Stille, dann Drop.
41. **[41] Worth anything?** MG: Dollarschein, der leicht flackert, Frage-Overlay. SFX Scan.
42. **[42] Worth more first…** MG: Preisschilder im Laden sinken, Chip „1929–1933 · PRICES −25%“, Dollar wird größer. SFX Blip-down ×3.
43. **[43] 1933 gold…** MG: Goldmünze „$20.67“ wandert vom Bürger zum Staat, Stempel „1934 · $35“, Chip „+69% FOR THE GOVERNMENT · 0% FOR YOU“. SFX Münze, Slam.
44. **[44] Buys a little less…** MG: Einkaufskorb, der jedes Jahr ein Stück schrumpft (2027 · 2028 · 2029), ein leerer Briefkasten „NO LETTER“. SFX Ticks.
45. **[45] New boss…** MG: Weltkarte von oben, alle roten Städte, Kamera zieht auf. SFX Whoosh tief.
46. **[46] Five things…** MG: fünf Säulen-Icons (Essen, Energie, Fabrik, Armee, Vertrauen) als Scoreboard-Spalten. SFX Pop ×5.
47. **[47] Europe, Japan, Gulf** MG: Scoreboard-Zeilen mit Flaggen, die Energie-Spalte leuchtet Rot für EU/JP, die Essen-Spalte für den Golf. Heizkörper-Icon für Europa. SFX Karten-Flip.
48. **[48] China** MG: China-Zeile füllt sich bei Fabriken/Weizen/Gold grün, dann der Captain-Insert (SZ kurz) und rot bei Kunden/Öl. SFX Flip, Schiffshorn leise.
49. **[49] America** MG: US-Zeile füllt sich bei allen fünf Säulen. SFX Pops aufsteigend.
50. **[50] Strange part** MG: brennendes Haus mit US-Flagge, Geldpfeile aus der ganzen Welt laufen hinein; Chips „2008 · DOLLAR +20%+“ und „OCT 2026 · 18-MONTH HIGH“. SFX Feuer, Whoosh.
51. **[51] Wins this crash…** MG: Pokal mit US-Flagge, daneben ein Schatten mit Fragezeichen „NEXT TIME?“. SFX tiefer Ton.
52. **[52] Gold vs IOUs** MG: Balkenvergleich der Notenbank-Reserven Gold vs. US-Anleihen (Wende 2025); Goldbarren stapeln sich zu „~320 TONS · JUL–SEP 2026“ neben zwei Blauwal-Silhouetten. SFX Barren-Klicks.
53. **[53] Print vs can't print…** MG: Druckerpresse ↔ Goldbarren; „2022 · RUSSIA · ~$300B FROZEN“ mit Eis-Effekt; Weggabelung Dollar ↔ Gold, ein Pfeil zuckt Richtung China. SFX Eis-Knacken.
54. **[54] Back to your answer…** MG: Das Schloss „REMEMBER“ öffnet sich; zwei Zeitstrahlen 2008 (~5 Jahre) vs. 1929 (25 Jahre); drei Häkchen „CASH YOU CAN REACH · NO DEBT THAT CAN BE CALLED · DON'T SELL AT THE BOTTOM“. SZ: ein Elektriker repariert im Treppenhaus das Licht, das Licht geht an. SFX Häkchen, Schalter.
55. **[55] 1944 hotel** SZ Hotel in den Bergen 1944 (Bretton Woods) außen, dann Saal, in dem gezeichnete Delegierte mit Fahnen Platz nehmen. MG: Chip „JULY 1944 · 44 COUNTRIES · 3 WEEKS“, Dollar in die Mitte, „US: ~2/3 OF WORLD GOLD“.
56. **[56] Invitations** MG: Umschläge mit Stempel „WASHINGTON“ fliegen hinaus; ein neuer Umschlag ohne Absender kommt, der Goldstapel spiegelt sich darin. SFX Brief-Whoosh, Ausklang.
57. **[57] Which country?** MG: alle Fahnen als Abstimmungs-Leiste plus „Comment: where are you watching from?“. Endscreen.

## F. Szenen-Sets (Higgsfield, erst nach Freigabe): Raum zuerst planen
Für jedes Set wird vorher festgelegt: Bodenlinie, Türen (Position, Größe, Scharnier), Laufwege, Figurengröße relativ zur Tür (Tür ≈ 1,2 × Figurenhöhe), Kamerapunkte. Erst danach entstehen Figuren und Objekte passend dazu.

| Set | Tür / Weg | Figuren & Aktionen |
|---|---|---|
| Lagerhalle Virginia (Server-Gänge) | Rolltor rechts, Gang in die Tiefe | Techniker schiebt Wagen; drei Verleiher kommen durchs Tor, kleben Etiketten |
| Deine Küche (wiederkehrend) | Tür links, Tisch Mitte | „Du“ sitzt, isst, Handy/Laptop, steht auf |
| Börsensaal Tokio | Pult-Reihen | Trader hämmert, dreht sich, Hände hoch |
| Juwelier Mumbai | Ladentür mit Glocke, Glastheke | Kundin kommt rein und legt die Kette hin; Juwelier wiegt und zeigt auf den Bildschirm |
| Bäckerei Kairo innen + außen | Tür Straße | Bäcker an der Tafel; Kundin; Menge außen |
| Schiffsdeck Shanghai | Deck, Brücke | Kapitän und Crew am Tisch mit Karten |
| Lager Ohio (Nacht) | Hallentor | Schild „NIGHT SHIFT“ wird abgehängt |
| Bank Frankfurt außen | Glastür Mitte | Kunden in der Schlange, Mann rüttelt, Kassiererin öffnet den Spalt |
| Supermarktkasse | Band | „Du“ legt Waren aufs Band |
| Treppenhaus (Elektriker) | Leiter | Elektriker schraubt, Licht geht an |
| Hotel 1944 außen + Saal | Eingang | Delegierte setzen sich |

Figuren (je Bogen mit offenen und geschlossenen Mündern, nur der Mund bewegt sich): du, Techniker, Verleiher, Trader, Kundin, Juwelier, Bäcker, Kapitän (+Crew), Manager (Laptop), Kassiererin, Elektriker. Alle bekommen 2–4 Posen (stehen, gehen, sitzen, reagieren, traurig) und werden sauber freigestellt (Ränder prüfen).

## G. Ton
- **Stimmen:** Mark ist der Erzähler. Trader, Juwelier, Bäcker, Kapitän, Manager und Kassiererin sprechen mit menschlichen Stimmen und passendem Akzent, aber ohne Übertreibung.
- **Musik:** echte lizenzierte Kevin-MacLeod-Tracks aus der Bibliothek, die mit der Geschichte wechseln:
  1. Cipher (Hook und Welt)
  2. Interloper (Crash-Woche)
  3. Mystery Bazaar (Mumbai und Kairo, dezent)
  4. Dark Times (Bank und Zölle)
  5. Crossing the Chasm (Rally und Absturz)
  6. Long Note (die Frage)
  7. Lost Frontier (wer gewinnt)
  8. Reawakening (Ende)
- **SFX:** Familie wie in C.

## H. Budget (Higgsfield)
- Sets: ca. 13 Bilder × 2 = 26
- Figurenbögen plus geschlossene Münder: ca. 11 × 2 × 2 = 44 (Posen werden im selben Bogen erzeugt)
- Stimmen: ca. 57 Zeilen, rund 13.000 Zeichen ≈ 60
- Summe ≈ 130. Damit liegen wir knapp über dem Rahmen von 120. Einsparung: Juwelier und Bäcker teilen sich einen Figurenstil, und das Treppenhaus wird ein MG-Insert. Ziel bleiben ≤ 120. Thumbnail ≈ 5.
