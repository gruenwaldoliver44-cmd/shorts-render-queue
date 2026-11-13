# Video-Pipeline: die Base (Stand 10.11.2026, abends)

Gilt für jedes Longform-Video. Wenn Oliver „bau ein Video“ sagt, laufen alle Tore der Reihe nach. Ein Tor gilt erst als bestanden, wenn sein Ergebnis im Videoordner liegt und die Checkliste abgehakt ist. Kein Tor wird übersprungen, auch nicht, weil ein Schritt „sich fertig anfühlt“. Zeit ist nie die Grenze.

**Regel Nummer 1 über allem: Retention.** Der Zuschauer muss in jeder Sekunde weiterschauen wollen. Nie Recherche, Zahlen oder Gerichtsverfahren herunterrattern. Jedes Video ist eine Geschichte über eine Angst, kein Bericht.

**Umschreiben heißt alles umschreiben.** Ändern Recherche oder Prüfung den Schmerzpunkt, den Hook oder den Titel, wird das GANZE Skript neu geschrieben, also Anfang, Ablauf, Mitte und Ende, und die Tore 4 bis 7 laufen komplett neu. Nie nur einen Teil flicken und den Rest vergessen.

Zu Beginn jedes Videos zusätzlich lesen, jedes Mal komplett: `spannung-handbuch.md` (Spannungstest: Hook-Block mindestens 9, jeder 30-Sekunden-Block mindestens 8, sonst kein Bau), `regel-1-spannung.md`, `skript-handbuch.md`, `musik-regeln.md`, `research-skriptkunst.md` und Olivers gespeicherte Arbeitsregeln (Memory `/projects/…/preferences.md`, über 40 Regeln, u. a.: Zuschauer nie Vorwissen unterstellen, alles klar erklären; was gesagt wird, ist sofort im Bild; Hook schnell geschnitten, nie leerer Hintergrund; Themen betreffen den Zuschauer selbst). Die Base ersetzt diese Quellen nicht, sie fasst sie nur zusammen.

## Tor 0: Neuer Chat (10.11.2026)
- Jeder Chat hat einen eigenen Rechner. Der Cartoon-Motor (Engine, Figuren, Mund-Script, Musik-Score, Stimmen-Einstellungen) lebt sonst nur im Chat, in dem er gebaut wurde, und ist nach dessen Ende weg.
- Deshalb nach jedem Video: Motor als Paket `packs/mc-engine` ins Repo shorts-render-queue pushen und das Übergabe-Doc („Stand – Money Classics“) aktualisieren.
- Neuer Chat: Übergabe-Doc lesen, Motor aus dem Repo holen, erst dann bauen. Ohne Motor im Repo: nur Skript, kein Bau.
- Chat am besten in der Desktop-App mit verbundenem Ordner `~/ShortsRenderAgent` starten, sonst gilt der Abschnitt „Übergabe zum Mac ohne verbundenen Ordner“ unten.

## Tor 1: Thema mit Beweis (topic.md)
Phase neuer Kanal, bis ein Video klar durchstartet: YouTube kennt unsere Zuschauer noch nicht und ordnet deshalb über Thema und Suche zu.
- Bevorzugt Themen, die gerade gesucht werden (vidIQ-Keywords, steigend) und die kleine Kanäle zu Ausreißern gemacht haben (Outliers bis etwa 100.000 Abos, mindestens 5-fach über Schnitt). Dazu die Konkurrenzkanäle prüfen: Michael Girdley, Build Inc., JunkBondInvestor, Money Chuck, Bagholder Association, Hungerwise.
- Harte Filter: nachgewiesene Nachfrage, keine starke Cartoon-Version vorhanden, Figuren für Szenen und Dialoge vorhanden.
- In einer klaren Nische bleiben: Geld-Katastrophen, die den Zuschauer selbst treffen könnten (Bankpleiten, gesperrtes Geld, Betrug, Zusammenbrüche, versteckte Kosten). Nicht zwischen fremden Themen springen, YouTube muss lernen, wer unser Zuschauer ist.
- Ein Thema braucht eine persönliche Angst des US-Zuschauers, ein Rätsel oder einen Schuldigen und Menschen für Szenen.
- Thema aus den Ausreißern, Winkel von uns (10.11.2026): Das Thema muss 2 bis 3 Ausreißer haben (Nachfrage), der Titel muss etwas sagen, das die bestehenden Videos nicht sagen (Gegenthese, Format-Transfer, Szenario). Kein neutraler Faktenstoff („das ist halt so“): Es muss den Zuschauer selbst treffen, der Tag, an dem es ihm passiert.
- Sättigungstest: viele neue Videos mit kaum Aufrufen bedeutet, das Thema fallen zu lassen.
- Kein Beweis, kein Video.

## Tor 2: Schmerz und Kommentare (pain.md)
- Transkripte und Kommentare der 3 bis 5 größten Videos zum Thema lesen: Was macht wütend oder ängstlich, was fragen die Leute?
- Die Angst des Videos in einem Satz und die 3 bis 5 Fragen, die der Zuschauer mitträgt. Das werden die offenen Schleifen.
- Den Fakt finden, den die Konkurrenz übersieht. Er trägt die letzte Enthüllung.

## Tor 2b: Die Geschichte finden, auch im langweiligsten Thema (story.md)
Jedes Thema wird spannend, wenn man diese sechs Dinge findet. Sie werden bei jedem Video aufgeschrieben, mit Quelle:
1. **Der Entscheidungsmoment:** Wann hätte jemand anders handeln können und tat es nicht? Spannung entsteht, wenn der Zuschauer das Ende kennt und trotzdem hofft.
2. **Der Widerspruch:** Was gesagt wurde und was wirklich war („die Bank sagte: alles in Ordnung“). Ironie trägt ganze Abschnitte.
3. **Das Verborgene:** Was wurde versteckt, wer wusste es, wer hat es aufgedeckt?
4. **Die Figur mit Ziel:** Ein Mensch, der etwas will und etwas verlieren kann. Nicht „die Regierung“, sondern ein Gesicht.
5. **Die Brücke zum Zuschauer:** Warum betrifft es ihn heute? Was macht er selbst genauso, was kann ihm passieren?
6. **Das überraschende Detail:** Eine Zahl, ein Satz, ein Gegenstand, den niemand kennt. Wird auf die Größe des Küchentischs übersetzt.

So werden sie gefunden:
- **Kommentare** der 3 bis 5 größten Videos zum Thema: Fragen, Wut, „das wusste ich nicht“, Korrekturen. Häufige Fragen sind offene Schleifen, Korrekturen sind übersehene Fakten.
- **Transkripte** derselben Videos: Liste, was alle erzählen. Was keiner beantwortet, ist unsere Lücke und meist unsere letzte Enthüllung.
- **Primärquellen:** Berichte, Archive, Bücher, Interviews, Nachrichten aus der Zeit. Dort stecken die menschlichen Details, die Konkurrenz-Videos weglassen.
- Beispiel für ein langweiliges Thema („die beste Kassiererin des Monats“): Entscheidungsmoment ist der Kunde, der bei ihr zahlen will. Widerspruch: Sie wird gelobt und gleichzeitig jede Sekunde gemessen. Das Verborgene: was die Kasse über jeden Kunden speichert. Brücke: Das passiert dir bei jedem Einkauf.

Erzähltechniken, aus denen das Skript gebaut wird: Ergebnis zuerst zeigen und Ursache zurückhalten, Countdown oder Uhr, Duell zweier Seiten, ein Geheimnis mit Auflösung am Ende, der Außenseiter, die Wette, die schiefgeht.

## Tor 2c: Der Gedankengang des Klickers (Regel von Oliver, 10.11.2026, nach Skript V8)
Befund: Skript V8 hatte einen formal starken Hook („Dale verliert 60.000 Dollar bis Samstag“, hookscore 92), aber Oliver fand ihn befremdlich, weil er nicht bedient, was im Kopf des Klickers vorgeht. Wer auf „What happens to your money when your bank fails“ klickt, ist im Krisenmodus (Wirtschaftskrise, KI-Blase platzt, Banken fallen) und trägt eine Reihe von Fragen in einer bestimmten Reihenfolge: Was passiert? Wie schnell? Erfahre ich es per Alarm am Handy oder aus den News? Kann ich morgen noch Brot kaufen? Ist mein Geld sofort nichts mehr wert? Soll ich Krypto verkaufen, Gold bunkern? Ab jetzt gilt für jedes Skript:
- Vor dem Skript die Fragen des Klickers in seinen eigenen Worten sammeln (Reddit, Kommentare, Google-Fragen, Quora) und in der Reihenfolge aufschreiben, in der sie ihm durch den Kopf gehen. Das ist das Gerüst des Videos: Hook und Intro greifen genau diese Gedanken auf, subtil, als Situation und Bild, nie mit „ich verstehe deine Ängste“ oder „du fragst dich jetzt bestimmt“.
- Der Körper beantwortet die Fragen in logischer Reihenfolge, bei Zeit-Titeln Stunde für Stunde. Die Zeitspanne folgt der Recherche: dort aufhören, wo es nicht mehr spannend ist (2 Stunden, 24 Stunden oder ein Monat), nie künstlich strecken. Keine Anleitung und kein Thriller, sondern die logische Kette: Was passiert, wer wird abgegrenzt, was merkt der Kunde zuerst.
- Zu jeder Frage eine Anekdote aus der Vergangenheit (SVB 2023, WaMu 2008, Zypern 2013, Griechenland 2015, Argentinien 2001, 1933), und ehrlich sagen, wenn etwas noch nie passiert ist („das gab es in den USA noch nie“). Was wir nicht wissen, behaupten wir nicht; eine spätere Folge (Teil 2) darf angeteasert werden.
- Schmerzpunkte der Zuschauer generell (nicht nur zum Thema) recherchieren und als gepflegte Liste in der Pipeline halten (`research_viewers.md`): Angst, als Letzter zu erfahren, Hilflosigkeit, Geld der Familie, dem System nicht trauen, hinter Gleichaltrigen liegen.
- Reihenfolge der Freigabe: erst das Skript zu 100 % mit Oliver besprechen, erst dann Visuals planen (Szene für Szene, professionelle Motion Graphics, Skills und Kits holen, Stunden investieren), dann bauen, dann das fertige Video zeigen.

## Tor 3: Verpackung zuerst (package.md und Bilder)
- Titel unter 60 Zeichen, mit Trend-Suchbegriff und Schmerz, nach echten Ausreißer-Formen gebaut und mit vidIQ bewertet.
- Thumbnail: ein klarer Blickfang (ein Mensch mit starkem Gefühl schlägt ein Objekt), höchstens 3 bis 4 große Wörter, lesbar bei 168 Pixel, sagt etwas Konkretes (Zahl, Folge), wiederholt nie den Titel. Titel und Thumbnail zusammen machen das Thema auch für Unwissende sofort klar.
- Unser Thumbnail neben die Top 10 zum Suchbegriff in echter Feed-Größe legen. Fällt es nicht auf, neu machen.
- 3 Varianten für YouTube „Test & Compare“.
- Das Thumbnail passt zu einem Moment in den ersten 30 Sekunden.
- Olivers „ich würde nicht klicken“ ist ein Stopp, kein Feedback zum Wegerklären. Kein Skript vor seinem Okay.
- Higgsfield für Thumbnails nur etwa 5 Credits, außer er bestellt mehr. Günstiger: ein gerendertes Einzelbild des Hooks in voller Auflösung nehmen und Text darüberlegen (Bankpleite-Video, 0 Credits).

## Tor 4: Spannungstreppe vor dem Text (beats.md)
- Tabelle Minute für Minute: Welche Frage hält der Zuschauer gerade offen, welche neue öffnet sich, bevor die alte schließt? Alle 60 bis 90 Sekunden ein neuer Haken oder eine Wendung.
- Eine Figur mit Ziel läuft durch das ganze Video, keine Fallsammlung.
- Erste große Auflösung um die Mitte, sie öffnet die tiefere Frage. Die stärkste Enthüllung kommt zuletzt, ruhig erzählt.
- Unterhaltungsmomente schon hier einplanen, nicht nachträglich.
- Für jeden Abschnitt gleichzeitig planen, was gesagt und was gezeigt wird.

## Tor 5: Skript (script.txt)
Mit dem Skill yt-script: mindestens 5 Hooks, bewertet mit hookscore.py. Unter 90 Punkten wird kein Hook verwendet (Regel von Oliver 9.11.2026), dann werden neue geschrieben, bis einer 90 oder mehr hat und trotzdem natürlich klingt. Mindestens 8:00 Minuten inklusive Abspann, etwa 1.400 bis 1.900 Wörter. Die ersten 15 Sekunden bestätigen den Klick, öffnen die Frage und beweisen, dass es die Antwort gibt.

Jeder Punkt muss erfüllt sein:
- [ ] Jede Minute hat eine offene Frage, ein Problem oder einen Schmerzpunkt. Keine Strecke mit bloßer Information.
- [ ] Höchstens eine große Zahl pro Abschnitt, übersetzt auf den Küchentisch, nie zwei ähnliche Zahlen hintereinander. Kein Gerichts- oder Paragrafenkram, nur was der Zuschauer fühlt.
- [ ] Humor und Leichtigkeit nach eigenem Ermessen: Alle 60 bis 120 Sekunden, wo es der Spannung hilft, ein Moment, der Sympathie schafft oder kurz durchatmen lässt (eine Nebenfigur mit trockenem Witz, ein Mini-Dialog als Anekdote, eine Reaktion, ein Bildwitz). Die Kuh, die „Muh“ sagt, und der Chef, der in die Luft springt, waren Beispiele für die Haltung, keine Vorlagen. Jeder Moment entsteht aus dem, was im Video gerade passiert, und treibt Geschichte oder Sympathie. Nie dauerhaft, nie aufgesetzt. Mit Sprecher ins Skript schreiben.
- [ ] Sympathie: Man mag mindestens eine Figur und fürchtet um sie.
- [ ] Ende: klare Antwort auf den Titel, ruhige letzte Enthüllung, Rückkehr zum Anfang, genau eine Bitte.
- [ ] Klingt nicht nach KI: konkrete Namen, Daten, Orte, gemischte Satzlängen, kein „let's dive in“, keine Weisheit am Ende jedes Abschnitts. Höchstens zwei Abschnitte enden auf einen Merksatz, der Rest endet auf einen Schnitt zu einer Figur oder eine Frage (Befund 10.11.2026: in der ersten Fassung endeten 8 von 10 Abschnitten auf eine Moral).
- [ ] Jeder Fakt wird von einer Figur gebraucht: Erzähler über stehender Figur ist die Absprungstelle. Befund Bankpleite-Skript: jeder Block, in dem Dale oder Ruth etwas wollten, bestand; jeder reine Erzähler-Block fiel durch.
- [ ] Alles gesetzt, bevor es gebraucht wird: Figuren (Ehefrau), Gegenstände (Truck, Koffer) und Orte tauchen vor ihrer Pointe auf. Zeitleiste und Geldbeträge in einer Tabelle gegenrechnen (Wochentag, Uhrzeit, wer wo ist, welche Summe wo liegt).
- [ ] Zeitstempel: Bei „Stunde für Stunde“-Titeln trägt jede Szenenkarte eine eingebrannte Uhrzeit.
- [ ] Lebende echte Personen: nur Erzählung und wörtliche Zitate, als beschriftete Silhouette oder Illustration. Verstorbene dürfen dramatisiert werden, markiert als „Dramatized“.
- [ ] Soll der Titel nach dem Schreiben anders lauten: ändern und Tor 3 neu durchlaufen.
- [ ] Einfachheit (Oliver 10.11.2026): Ein 15- bis 18-Jähriger ohne Vorwissen versteht jeden Satz; nie voraussetzen, dass der Zuschauer große Summen hat (geschrieben für den Normalo mit ein paar hundert bis ein paar tausend Dollar).

## Tor 6: Unabhängige Prüfung (review.md)
Zwei getrennte Agenten, die das Skript nicht geschrieben haben:
1. Faktenprüfer mit nur Skript und Quellen. Jede Korrektur kommt mit Ersatzzeile. Nie eine Zahl nennen, bei der Quellen sich widersprechen. Veränderliche Fakten (Urteile, Auszahlungen) am Upload-Tag nochmals prüfen.
2. Zuschauer-Kritiker mit 30-Sekunden-Tabelle: Wo würde ich wegklicken, welche Minute ist langweilig, welcher Unterhaltungsmoment wirkt erzwungen, ist der Schmerz im Hook klar? Jeder Wegklick-Punkt wird behoben, dann laufen beide Prüfungen neu.
Erfahrung 10.11.2026: Drei Runden sind normal (v1: 8 von 21 Blöcken bestanden, v2: 14 von 22, v3: 18 von 20, dann die letzten Zeilen nachgebessert). Nicht nach einer Runde aufhören.
Erst danach: Stimmen.

## Die ersten 5 Sekunden (Vorschau im Feed, Regel von Oliver 9.11.2026)
Auf der Startseite spielt YouTube das Video ab Sekunde 0 als Vorschau ab, meist stumm mit Untertiteln. Die meisten sehen nur diese 3 bis 5 Sekunden und entscheiden dann, ob sie klicken. Deshalb bekommen sie den größten Aufwand im ganzen Video:
- Sekunde 0 ist schon Handlung: kein Titel, kein Logo, kein Fade-in, kein ruhiges Totalbild.
- Echte Bewegung von Figuren mit sichtbarem Gefühl (rennen, zusammenzucken, springen, Mund bewegt sich), dazu Kamerafahrt. Etwa jede Sekunde etwas Neues.
- Funktioniert stumm: eine große, lesbare Zahl oder ein Wort im Bild, das das Versprechen von Titel und Thumbnail sofort bestätigt.
- Der stärkste, überraschendste Bildmoment des Videos wird hier als Vorgeschmack gezeigt (Kontrast, Gegensatz).
- Thumbnail und erste Sekunde passen sichtbar zusammen, damit der Klick bestätigt wird.
- Prüfung vor dem Rendern: Einzelbilder bei 0, 1, 2, 3, 4 und 5 Sekunden ansehen, und die ersten 5 Sekunden stumm anschauen. Steht dort irgendwo ein ruhiges Bild, wird neu gebaut.

## Tor 7: Bildplan (shots.md)
- Jeder Satz hat einen Zweck: zeigen, erklären, beweisen oder rechnen. Was gesagt wird, wird immer gezeigt. Mechanismen werden animiert (Tank, Rohr, Fluss), nicht nur beschriftet.
- Ständige Bewegung: nie ein Standbild, während gesprochen wird, nie ein Hintergrund mit Gerede darüber.
- Welt als 3D: erst Räume und Wege planen, Füße am Boden, Figuren nutzen Türen, Fahrzeuge Straßen, Dinge werden getragen.
- Einblendungen ergänzen Information, wiederholen nie das Gesprochene. Zeitungseinblendungen, Pop-ups und Einflüge bekommen jeweils einen guten, sauberen Soundeffekt, nie schräg. Lieber mehr Effekte als weniger.
- Humormomente bekommen eigene Einstellungen mit echter Mundbewegung und entstehen aus der Szene selbst.
- Plan auf die Sekunde: Für jede Zeile stehen Figur, Bewegung, Blickrichtung, Pause, Kamera und Geräusch fest, bevor gebaut wird.
- Jede Erzählzeile über 15 Sekunden braucht eine zweite Handlung oder einen Schnitt (Bankpleite: Agenten gehen durch die Motel-Tür, ein Passant geht vorbei, ein Truck fährt auf dem Highway; Georgia-Fall: Karte 6 s, dann Schnitt zurück zum Schalter mit Einblendungen). Prüfung am Kontaktbogen des gerenderten Videos (ein Bild alle 5 s): drei gleiche Bilder hintereinander sind ein Standbild.

## Bild-Prüfpunkte aus dem Banken-Video (Oliver, 10.11.2026), Pflicht vor jedem Render
- Größenverhältnisse: Figuren sind nie kleiner als Stühle, Schalter oder Türen; wer sitzt, sitzt wirklich auf dem Stuhl. Kontaktbogen je Set mit Bodenlinie und Größenmaß, bevor eine Figur gebaut wird.
- Niemand fliegt: Jede Ortsveränderung ist ein Gehen, Fahren oder ein Schnitt. Der Einzug in die Bank am Anfang des Banken-Videos war unlogisch; so etwas wird an den Einzelbildern vor dem Render geprüft.
- Beim Sprechen bewegt sich ausschließlich der Mund, nie das Auge; jede sprechende Figur hat einen bewegten Mund, keine Ausnahme (Banken-Video: bei der älteren Angestellten bewegte sich das Auge, andere Münder standen still). Mund-Varianten mit `mo2.py` (Unterschied nur im unteren Gesichtsband), danach Gesichts-Crops bei 15 fps aus dem Render prüfen.
- Sprechblasen mit dem Gesagten hin und wieder zusätzlich zum Mund, für kurze Repliken.
- Sets mit gemalten Schildern oder Uhren prüfen: `s_atm` hatte ein OPEN-Schild, nach 18 Uhr falsch. Lösung: Kopie `s_atmc` mit übermaltem Schild (CLOSED), nur der Samstag nutzt OPEN.
- Figuren „hinter Glas“ nur innerhalb der Glasfläche bewegen (Start und Ziel im Fensterausschnitt), sonst laufen sie sichtbar über die Fassade.
- Einblendungen (chip, doc, pic, line) liegen im Bildschirm-Koordinatensystem, nicht in der Welt: Zoomt die Kamera, wandern die Figuren, die Einblendung bleibt. Positionen am gerenderten Einzelbild nachmessen, nie aus Welt-Koordinaten raten.
- Beschriftungen gehören an das Objekt, nicht an die Figur daneben (Fassung 2: „temporarily unavailable“ stand auf dem Mann statt auf dem Bankomaten). Türen: Wer durch eine Tür geht, geht durch eine geöffnete Tür (Türanimation vor dem Durchgang), nie durch eine geschlossene.
- Oliver sieht das fertige Skript und gibt es frei, bevor irgendetwas gebaut wird.


## Regel aus dem Bankpleite-Video, Fassung 1 und 2 (Oliver, 10.11.2026, beide nach unter einer Minute abgebrochen)
Die erste Fassung war visuell ein Flop, obwohl jedes Einzelbild „stimmte“: Dale stand eine Minute regungslos am Bankomaten, während Zahlen einflogen; Angestellte tauchten in der Wand auf statt durch Türen zu kommen. Die zweite Fassung hatte Motion Graphics, aber sie sahen amateurhaft aus (falsch platzierte Labels, Figur durch geschlossene Tür, verwirrende Grafiken). Ab jetzt gilt für jede Sekunde der Laufzeit:
- Was gesagt wird, zeigt das Bild als Erklärung, nicht als eingeblendete Zahl: Mechanismus (Geld fließt von A nach B), Ablauf (Zeitstrahl), Größe (Stapel, Raster), Ort (Karte mit Route), Vergleich (zwei Stapel nebeneinander), Schutz (Schirm über dem versicherten Teil), Verlust (Stapelspitze wird rot und fliegt als IOU davon).
- Sobald eine Figur nichts zu tun hat, bekommt sie eine Handlung (geht, fährt, trägt, öffnet eine Tür, setzt sich, verlässt den Raum, reagiert) oder es kommt ein Schnitt zu einer Motion-Graphic oder einer Nebenfigur. Schnitt oder neue Einstellung alle 3 bis 6 Sekunden, ein sichtbares Ereignis alle 1 bis 3 Sekunden.
- Motion Graphics müssen professionell aussehen: ein Raster, eine Schriftfamilie, gemessene Positionen, saubere Ein- und Ausblendungen mit Easing, nie überlappende Labels, nie mehr als eine Information pro Sekunde. Vor der Regie Skills/Kits für Motion Graphics holen (Remotion-Skills, Design-Systeme) und ein Beispielbild jeder Grafik als Standbild prüfen, bevor es ins Video kommt.
- Motor-Bausteine dafür: `stack`, `map`, `tl`, `flow`, `shield`, `boxes` (neu), dazu `phone`, `screen`, `acct`, `num`, `cmp`, `doc`, `paper`, `pic`, `wire`, `bills`, `clock`, `stamp`, `slam`, `chip`. Fehlt ein Baustein, wird er in `src/Main.jsx` gebaut, bevor die Regie geschrieben wird.
- Jede Bewegung und jede Einblendung bekommt einen Soundeffekt.
- Pflichtprüfung nach dem Render: `out/motion.py` auf der 720p-Vorschau (Frame-Differenz bei 5 fps). Jede stehende Strecke ab 2 Sekunden wird angesehen; ab 4 Sekunden wird neu gebaut. Dazu Kontaktbogen alle 3 Sekunden über das ganze Video, nicht nur den Anfang.
- Einblendungen (chip, doc, stack, map …) liegen im Bildschirm-Raum; Positionen bei gezoomter Kamera mit `screen = 960 + (welt − cx) · z` umrechnen.
- Figuren an Türen stehen auf der Türschwelle (im ATM-Set y≈690, h≈500), nicht unten auf dem Gehweg vor der Tür.
- Vor dem vollen Render: die ersten 60 Sekunden rendern und Oliver zeigen (Tor 8b).

## Pflicht bei jeder Änderung
Wird irgendetwas geändert, vom ganzen Skript bis zu einem Satz, läuft diese Liste komplett neu, nicht nur für die geänderte Stelle:
- Hält jede Minute noch eine offene Frage?
- Stimmt der Schmerzpunkt im Hook noch?
- Sind die Unterhaltungsmomente noch da und passen sie zur Welt?
- Wird alles Gesagte gezeigt, mit Bewegung in einer 3D-Welt, Füße am Boden, Türen, Straßen?
- Passen Titel und Thumbnail noch zum Anfang?
- Faktenprüfung für jede neue Behauptung.

## Tor 8: Bauen
- Engine: die neueste aus dem Repo-Paket `packs/mc-engine` holen (früher `/home/claude/ys/pa/eng`). Sets und Figuren über Higgsfield nano_banana_pro mit Stilreferenz. Keine KI-Videoclips.
- Stimmen elevenlabs_v4: Mark immer Erzähler. Nebenstimmen professionell, menschlich, emotional, nie flüsternd, keine Klammer-Tags bei Nebenrollen. Höchstens 7 pro Batch.
- Münder: echter bewegter Mund oder keiner, nie ein weißer Fleck.
- Musik: echte lizenzfreie Stücke passend zur Geschichte (score.py, Kevin-MacLeod-Bibliothek), nie generiert.
- Credit-Budget etwa 100 bis 120 pro Video, dort, wo es das Bild klar verbessert, nichts Unbestelltes. Stand 10.11.2026: etwa 375 Credits übrig, Nachfüllung in 5 Tagen.
- Kontaktbögen der Standbilder und Boden-Prüfung vor jedem vollen Rendering. Nach dem Rendering Bewegung messen: keine stehenden Strecken, während gesprochen wird.

## Tor 8b: Render-zuerst-Prüfung der ersten 45 Sekunden
- Vor dem vollen Rendering 0:00 bis 0:45 rendern, stumm und mit Ton neben die ersten 45 Sekunden der zwei besten Konkurrenzvideos legen. Ein unabhängiger Prüfer wählt, wo er weiterschauen würde. Besteht unser Anfang nicht, wird er neu gebaut.
- Oliver sieht diese 45 Sekunden zusammen mit Titel und Thumbnail, bevor der Rest gerendert wird.

## Tor 9: Rendern, zeigen, hochladen
- Rendern auf dem MacBook über die Queue. Dauer, Lautheit und Bildbogen prüfen. Keine Computersteuerung am Mac, manuelle Schritte beschreibe ich Oliver.
- Immer Oliver zeigen vor dem Upload. Hochladen privat über Higgsfield-Medien und Metricool. Nie öffentlich ohne sein Go, er stellt selbst öffentlich. Sagt er „sofort hochladen“, dann sofort.
- Beschreibung höchstens 5.000 Zeichen mit Quellen und CC-BY-Musikhinweis, Tags höchstens 500 Zeichen, Suchbegriffe in beiden. KI-Inhalt angeben, nicht für Kinder, Kategorie Bildung.
- Nie Schlüssel oder signierte Links in die Queue.

## Übergabe zum Mac ohne verbundenen Ordner (Erfahrung 10.11.2026, Bankpleite-Video)
- Ist der Ordner `~/ShortsRenderAgent` nicht mit dem Chat verbunden, scheitern Repo-Push (`add_repo`) und Ordnerfreigabe zunächst an der automatischen Prüfung. Sagt Oliver ausdrücklich „mach es“, die Ordnerfreigabe erneut anfordern (`device_request_folder_access` mit Grund); das hat funktioniert.
- Mit Ordnerzugriff: Paket (`bundle` mit `public`, `mixv.m4a`, Musik) per `device_commit_files` nach `pilot_test/film/` legen. Den Job nicht per git pushen, sondern über die GitHub-Contents-API mit dem Token aus `~/ShortsRenderAgent/token` direkt aus `device_bash` anlegen (Job-JSON mit `node -e` schreiben, dann `curl -X PUT …/contents/jobs/<id>.json`). Der Agent holt den Job in ≤60 s.
- Dateien, die über die Brücke auf den Mac kommen, bekommen eine zusätzliche `uuid`-Box (md5 ändert sich, Datei bleibt gültig). md5-Prüfung im Job mit dem Wert, den `device_bash` auf dem Mac liefert.
- Das ffmpeg aus `npx remotion` auf dem Mac kennt weder `-filter_complex_script` noch `sidechaincompress`/`loudnorm`. Musik deshalb im Container vertonen: Stücke aus `music/lib` per `device_stage_files` holen, `score.py` laufen lassen (letzter Cue wird auf die Videolänge beschnitten), `mixm.m4a` zurück auf den Mac. Ergebnis Bankpleite: Musik 17 dB unter der Stimme, in Pausen 4,5 dB lauter, −14,9 LUFS.
- Render-Zeiten auf dem Mac: 10-Minuten-Video etwa 5 Minuten, 720p-Vorschau 1 Minute. Vorschau per `device_stage_files` holen und hier mit ffmpeg prüfen (Dauer, Lautheit, Kontaktbogen alle 5 s, Mund-Crops bei 15 fps).

## Tor 10: Lernen (learn.md)
- Nach 48 Stunden und 7 Tagen: Impressionen, Klickrate, Haltekurve, Traffic-Quellen. Null Impressionen nach einem Tag: zuerst Sichtbarkeit, Zielgruppe, Altersbeschränkung und Ansprüche prüfen.
- Jede Korrektur, die Oliver während eines Videos gibt, wird als neue Zeile in diese Base eingetragen, damit sie nie wieder verloren geht.
- vidIQ-Credits: Stand 10.11.2026 noch 345 bis 4.12. Pro Video höchstens etwa 40 Credits (2 Outlier-Suchen, 1 Suche, 1 Kommentar-Abruf, 2 Titel-Scores). Transkripte über YTPuller (3 Credits), Fakten über Web-Suche.

## Sprachregel und Kalt-Zuschauer-Test (Regel von Oliver 9.11.2026)
- Geschrieben wird, wie ein Mensch erzählt: ganze, verbundene Sätze mit "because", "so", "which means", "and that's when". Keine Stakkato-Ketten ("It could have said no. It said yes."), keine Satzfetzen ohne Verb, keine KI-Pausen.
- Jede Zahl hat ihre Einheit und ihren Besitzer ("thirty-five dollars to a bank fee", "fifty million dollars in the bank"). Nie "you lose 35" ohne zu sagen, was und an wen.
- Kontext zuerst: Jeder Satz muss für jemanden verständlich sein, der nichts weiß und gerade erst reingeklickt hat. Erst sagen, was passiert, dann den Witz.
- Logische Brücken: Jeder Satz folgt aus dem vorherigen. Wenn ein Sprung nötig ist, wird er angesagt ("Let's start at the bottom, with how that fee happened").
- Vorbild sind die Gewinner (z. B. Dark Ledger: "The number on your screen has a minus sign in front of it. You stare at it like it might disappear if you blink.").
- Pflichtprüfung vor jeder Freigabe: ein unabhängiger Kalt-Zuschauer-Agent liest das Skript als normaler Zuschauer ohne Vorwissen, laut gesprochen im Kopf, und markiert jedes "Hä?" (unklar, fehlender Kontext, Zahl ohne Einheit), jede Stelle, die künstlich oder nach KI klingt, und jede Stelle, an der er wegklicken würde. Null offene Markierungen, sonst kein Weiterbau.

## Thumbnail-Regel für Stufen-/Level-Videos (Oliver 9.11.2026)
- Das Thumbnail muss die Stufen zeigen: 3 bis 4 Felder von links nach rechts, oben in jedem Feld der Betrag groß (z. B. −$59 · $5K · $1M · $50M), Hintergrund wird von grau zu gold reicher, in jedem Feld dieselbe Figur oder Situation auf der jeweiligen Stufe. Vorbild: die erfolgreichen „Every Level“-Thumbnails (Memeable Data, The Analyst, jack pockets).
- Ein Zwei-Seiten-Vergleich mit Textzeile („SAME BANK“) hat ihm nicht gefallen.
