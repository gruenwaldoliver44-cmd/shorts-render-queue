# Themen-Scout – Mittwoch, 18.11.2026 (Lauf 04:18 UTC)

Datenlage: Apify-Abruf von 13 Beobachtungskanälen (130 Videos, rund 0,13 USD). vidIQ: ein `vidiq_outliers`-Aufruf (5 Credits, Guthaben danach 0). Datenbank jetzt 286 Videos von 15 Kanälen (64 aktualisiert, 66 neu). Fünf Videos ohne brauchbare Werte ausgelassen (Gemeinschaftsvideos, der Abruf lieferte 0 Aufrufe und kein Alter): vier von Money With Ricky, eines von Tom – Lazy Real Estate.

Neu in der Datenbank aus der vidIQ-Suche: **BROKE AMERICA** (2.800 Abos, fünf Videos mit 63.000–187.000 Aufrufen in 20 Tagen) und **Finance District** (1.200 Abos, „The Housing Market Is Now Worse Than 2008“ 147.000). Startdatum beider Kanäle ist nicht geprüft, das Feld bleibt leer.

## 1. Felder mit Beleg (mind. zwei Kanäle unter 50.000 Abos, Video über 30.000 in 60 Tagen)

| Feld | Belegvideos (Kanal, Aufrufe, video_id) |
|---|---|
| **Haus** | Jimmy Rogan 160.000 (ohoIG0r8QVE) · Finance District 147.000 (V5bsgzoKquw) · Explained Like You're Five 121.000 (nuBFWl3BctU) und 45.000 (mxF7JhCnL5s) · PENNY 44.000 (WYE_t61pUio) |
| **Preise/Inflation** | Jimmy Rogan 112.000 (3ht1Cg2CrGs), 65.000 (8KKj9VstG7o), 32.000 (I2ZEVaPB_oc) · BROKE AMERICA 97.900 (1TIkEo_w8m8) · Explained Like You're Five 71.000 (k5vPXpUT6iQ) |
| **Vom Gehalt leben, Auto, Raten** | BROKE AMERICA 187.200 (g95Xj1CPthI), 71.100 (DL4yiJzbbo4) · The Last Level 179.000 (nVNwwf1dQNU), 79.000 (hrke2JyMIKI) · Money With Ricky 158.000 (cpDqWRfBh-A) · Money Mechanics 145.000 (aZktpwxt62M), 38.000 (u0cEMgEiFtY), 37.000 (iPieS7Ozs6s) |
| **Rente (neu)** | Jimmy Rogan 39.000 (zBKroCMzJq4) · Tom – Lazy Real Estate 32.000 (0ur6P7-DLWA) · The Last Level 30.000 (twmvJ6SH5yY) |

Nur ein Kanal, deshalb höchstens Testplatz: **Staatsschulden** (PENNY 1,1 Mio., TmlvDH0ZFB4), KI-Blase/Nvidia (PENNY 164.000, 111.000, 101.000, 43.000), Wahl/Kongress (Explained Like You're Five 278.000, 91.000, 84.000).
Hinweis: Die vidIQ-Suche zeigte zu Staatsschulden zwei weitere kleine Kanäle mit Treffern (Finance Stack, 8.000 Abos, 193.800 Aufrufe am 13.11.; Macro Tradecraft, 3.500 Abos, 106.200). Sie stehen noch nicht in der Datenbank; mit ihnen wäre Staatsschulden ein reguläres Feld.

### Stärkster Anlass je Feld (letzte 7 Tage)

| Feld | Anlass | Datum | Zwei Quellen? |
|---|---|---|---|
| Preise/Inflation | Erzeugerpreise Oktober +6,5 % zum Vorjahr, größter Anstieg seit November 2022; Markt rechnet zu knapp 90 % mit Fed-Zinserhöhung im Dezember | 13.11. | ja |
| Vom Gehalt leben | New York Fed: Haushaltsschulden 19,1 Billionen Dollar, 5,0 % im Verzug (Bericht ist 8 Tage alt, deshalb nur Klasse Z) | 10.11. | ja |
| Staatsschulden | Höchstes Oktober-Defizit bisher: 404 Mrd. Dollar | 12.11. | ja |
| Haus | NAHB-Index fällt auf 25, tiefster Stand seit April 2012; 46 % der Bauträger senken Preise | 17.11. | nein, nur eine Quelle für die November-Werte geprüft |
| Rente | Medicare Teil B 2027: 209,40 Dollar im Monat (+6,50); Rentenerhöhung 3,6 % | 17.11. | ja, kein Kandidat gebaut (Feld steht nicht im Sendeplan) |

Nicht als Zahl verwendbar: Die Verbraucherpreise für Oktober (10.11., +0,4 % zum Vormonat) haben keine amtliche Jahresrate, weil die Daten vom Oktober 2025 fehlen; Schätzungen liegen zwischen 3,8 % und rund 4 %. Beim Hypothekenzins widersprechen sich die Quellen (Freddie Mac 7,11 %, andere Erhebungen 7,3–7,6 %, eine Meldung spricht von fallenden Zinsen), deshalb ohne Zahl.

## 2. Kandidaten mit FREIGABE

### Kandidat 1 – Preise/Inflation (Feld von heute)

```json
{
  "titel": "Wholesale Prices Are Up 6.5%. Is It 1979 Again? (Explained Like You're 5)",
  "thumb_text": "1979 AGAIN?",
  "klasse": "N",
  "cluster": "preise",
  "anlass": {"was": "BLS-Erzeugerpreise Oktober 2026: +6,5 % zum Vorjahr, größter 12-Monats-Anstieg seit November 2022; Markt rechnet mit Fed-Zinserhöhung im Dezember", "datum": "2026-11-13", "url": "https://www.joltjournal.com/finance/producer-price-index-october-2026/"},
  "zahl": {"wert": "PPI +6,5 % zum Vorjahr (Oktober 2026), nach 6,3 % im September", "url": "https://www.investmentnews.com/equities/ppi-still-uncomfortably-high-as-december-rate-hike-looms/269002"},
  "belege": ["3ht1Cg2CrGs", "8KKj9VstG7o", "I2ZEVaPB_oc", "k5vPXpUT6iQ", "1TIkEo_w8m8"],
  "szene": "Rick klebt in seinem Laden zum dritten Mal in diesem Jahr neue Preisschilder, weil sein Großhändler wieder teurer liefert; Danny steht mit dem Einkaufszettel davor, Maya rechnet vor, wann der Aufschlag an der Kasse ankommt.",
  "folge": ["Fed-Entscheidung im Dezember: Zinserhöhung mitten in der Teuerung und was sie mit Kreditkarte und Hypothek macht", "Verbraucherpreise November (BLS, 10.12.): kommt der Großhandelsaufschlag an der Supermarktkasse an?"]
}
```

```
KANDIDAT: Wholesale Prices Are Up 6.5%. Is It 1979 Again? (Explained Like You're 5)
Cluster: preise | Klasse: N | geprueft am 2026-11-18
 [OK ] 1 Klasse N oder Z
        Klasse N (E=Erklaerstueck/Firma/Person/Geschichte und R=Ratgeber sind gesperrt: 1 Treffer in 34 Videos)
 [OK ] 2 Belege: >=2 Videos >=30.000 von >=2 kleinen Kanaelen, <=60 Tage (Testplatz: 1 Video >=100.000, hoechstens 1x pro 7 Tage)
        Jimmy Rogan 112,000 (1mo ago); Jimmy Rogan 65,000 (2w ago); Jimmy Rogan 32,000 (12d ago); Explained Like You´re Five 71,000 (2w ago); BROKE AMERICA 97,900 (13d ago)
 [OK ] 3 Anlass mit Quelle, hoechstens 7 Tage alt
        BLS-Erzeugerpreise Oktober 2026: +6,5 % zum Vorjahr, größter 12-Monats-Anstieg seit November 2022; Markt rechnet mit Fed-Zinserhöhung im Dezember | 2026-11-13 = 5 Tage | https://www.joltjournal.com/finance/producer-price-index-october-2026/
 [OK ] 4 Belegte Zahl, im Titel oder Thumbnail
        PPI +6,5 % zum Vorjahr (Oktober 2026), nach 6,3 % im September | https://www.investmentnews.com/equities/ppi-still-uncomfortably-high-as-december-rate-hike-looms/269002
 [OK ] 5 Titel: <=60 Zeichen vor der Klammer, Gegenwartsform/Frage, kein Portraet-Muster
        47 Zeichen | Muster: Are | Sperrwort: keins
 [OK ] 6 Kein kopierter Titel, kein eigenes Thema doppelt
        aehnlichster fremder Titel 0.62: Who Does America Owe $40 Trillion? (Explained Like | eigener 0.36
 [OK ] 7 Thumbnail-Text: 1-3 Woerter, Zahl oder Frage zum Anlass
        1979 AGAIN?
 [OK ] 8 In Dannys Stadt spielbar (Szene benannt)
        Rick klebt in seinem Laden zum dritten Mal in diesem Jahr neue Preisschilder, weil sein Gr
 [OK ] 9 Zwei Folgewinkel fuer den Fall eines Treffers
        Fed-Entscheidung im Dezember: Zinserhöhung mitten in der Teuerung und was sie mit Kreditkarte und Hypothek macht / Verbraucherpreise November (BLS, 10.12.): kommt der Großhandelsaufschlag an der Supermarktkasse an?

ERGEBNIS: FREIGABE
```

**Classic:** 1979. Zweiter Ölschock, die Preise steigen zweistellig; Paul Volcker wird im August Fed-Chef und hebt am 6. Oktober 1979 in einer Sondersitzung am Samstag die Zinsen. Erzählbar als Entscheidung eines Menschen, und sie spiegelt die erwartete Zinserhöhung im Dezember.

**Quellen:** [BLS, CPI Oktober 2026](https://www.bls.gov/news.release/cpi.nr0.htm) · [Jolt Journal, PPI +6,5 %](https://www.joltjournal.com/finance/producer-price-index-october-2026/) · [InvestmentNews, PPI und Dezember-Erhöhung](https://www.investmentnews.com/equities/ppi-still-uncomfortably-high-as-december-rate-hike-looms/269002) · [Voice for Liberty, CPI ohne Jahresrate](https://www.wichitaliberty.org/economics/october-2026-cpi-report-inflation/) · [Yahoo Finance, Benzin 3,81 Dollar](https://finance.yahoo.com/energy/articles/gas-prices-national-average-falls-184514323.html)

Für das Skript beachten: Der Monatswert der Erzeugerpreise lag mit +0,3 % unter der Prognose; die 6,5 % sind die Jahresrate. Der Termin der Fed-Sitzung (9.12.) stammt nur aus einer Überschrift und muss im Faktencheck bestätigt werden.

### Kandidat 2 – Vom Gehalt leben (Feld für Donnerstag)

```json
{
  "titel": "Americans Now Owe $19.1 Trillion. Who Is Falling Behind? (Explained Like You're 5)",
  "thumb_text": "$19.1 TRILLION?",
  "klasse": "Z",
  "cluster": "vom-gehalt-leben",
  "anlass": {"was": "New York Fed, Quartalsbericht Q3 2026: Haushaltsschulden 19,1 Billionen Dollar (+334 Mrd. im Quartal), 5,0 % der Schulden im Zahlungsverzug, Autokredite 1,734 Billionen", "datum": "2026-11-10", "url": "https://www.newyorkfed.org/newsevents/news/research/2026/20261110"},
  "zahl": {"wert": "19,1 Billionen Dollar Haushaltsschulden (Q3 2026)", "url": "https://bankingjournal.aba.com/2026/11/new-york-fed-total-household-debt-reached-19-1t-in-q3/"},
  "belege": ["nVNwwf1dQNU", "hrke2JyMIKI", "aZktpwxt62M", "iPieS7Ozs6s", "u0cEMgEiFtY", "cpDqWRfBh-A", "g95Xj1CPthI", "DL4yiJzbbo4"],
  "szene": "Zahltag in Dannys Stadt: Danny legt am Küchentisch seinen Lohnzettel neben Autorate, Kreditkarte und Miete; Rick verkauft nebenan einen Pick-up auf 84 Monate, Maya zeigt an einer Wippe, wer zuerst kippt.",
  "folge": ["Autokredite: 1,7 Billionen Dollar und warum fast jeder dritte Eintausch mehr Schulden als Wert hat", "Kreditkarten nach dem Weihnachtsgeschäft: der nächste New-York-Fed-Bericht im Februar als Prüftermin"]
}
```

```
KANDIDAT: Americans Now Owe $19.1 Trillion. Who Is Falling Behind? (Explained Like You're 5)
Cluster: vom-gehalt-leben | Klasse: Z | geprueft am 2026-11-18
 [OK ] 1 Klasse N oder Z
        Klasse Z (E=Erklaerstueck/Firma/Person/Geschichte und R=Ratgeber sind gesperrt: 1 Treffer in 34 Videos)
 [OK ] 2 Belege: >=2 Videos >=30.000 von >=2 kleinen Kanaelen, <=60 Tage (Testplatz: 1 Video >=100.000, hoechstens 1x pro 7 Tage)
        The Last Level 179,000 (1mo ago); The Last Level 79,000 (3w ago); Money Mechanics 145,000 (2w ago); Money Mechanics 37,000 (4w ago); Money Mechanics 38,000 (4d ago); Money With Ricky 158,000 (7d ago); BROKE AMERICA 187,200 (18d ago); BROKE AMERICA 71,100 (12d ago)
 [OK ] 3 Anlass mit Quelle, hoechstens 14 Tage alt
        New York Fed, Quartalsbericht Q3 2026: Haushaltsschulden 19,1 Billionen Dollar (+334 Mrd. im Quartal), 5,0 % der Schulden im Zahlungsverzug, Autokredite 1,734 Billionen | 2026-11-10 = 8 Tage | https://www.newyorkfed.org/newsevents/news/research/2026/20261110
 [OK ] 4 Belegte Zahl, im Titel oder Thumbnail
        19,1 Billionen Dollar Haushaltsschulden (Q3 2026) | https://bankingjournal.aba.com/2026/11/new-york-fed-total-household-debt-reached-19-1t-in-q3/
 [OK ] 5 Titel: <=60 Zeichen vor der Klammer, Gegenwartsform/Frage, kein Portraet-Muster
        56 Zeichen | Muster: Now | Sperrwort: keins
 [OK ] 6 Kein kopierter Titel, kein eigenes Thema doppelt
        aehnlichster fremder Titel 0.68: Who Does America Owe $40 Trillion? (Explained Like | eigener 0.38
 [OK ] 7 Thumbnail-Text: 1-3 Woerter, Zahl oder Frage zum Anlass
        $19.1 TRILLION?
 [OK ] 8 In Dannys Stadt spielbar (Szene benannt)
        Zahltag in Dannys Stadt: Danny legt am Küchentisch seinen Lohnzettel neben Autorate, Kredi
 [OK ] 9 Zwei Folgewinkel fuer den Fall eines Treffers
        Autokredite: 1,7 Billionen Dollar und warum fast jeder dritte Eintausch mehr Schulden als Wert hat / Kreditkarten nach dem Weihnachtsgeschäft: der nächste New-York-Fed-Bericht im Februar als Prüftermin

ERGEBNIS: FREIGABE
```

**Classic:** Die 1920er-Jahre. General Motors gründet 1919 die Finanztochter GMAC, „Buy now, pay later“ wird normal, Ende des Jahrzehnts wird die Mehrheit der Autos auf Raten gekauft, bis 1929 die Einkommen wegbrechen.

**Quellen:** [New York Fed, Pressemitteilung 10.11.](https://www.newyorkfed.org/newsevents/news/research/2026/20261110) · [ABA Banking Journal](https://bankingjournal.aba.com/2026/11/new-york-fed-total-household-debt-reached-19-1t-in-q3/) (nur Überschrift geprüft, Seite ließ sich nicht öffnen) · [Money Under 30](https://www.moneyunder30.com/household-debt-record-2026/) · [24/7 Wall St., Autokredite mit Altschulden](https://247wallst.com/investing/2026/11/17/americans-are-taking-out-57235-car-loans-this-hidden-debt-trap-explains-why/)

Für das Skript beachten: Die New York Fed selbst nennt die 19,1 Billionen nicht „Rekord“. Die Verzugsquoten laufen auseinander (Autokredite leicht schlechter, Kreditkarten und Studienkredite besser als vor einem Jahr), das Wort „Rekord“ deshalb vermeiden.

### Kandidat 3 – Testplatz Staatsschulden (Feld für Freitag)

```json
{
  "titel": "The U.S. Just Spent $404 Billion It Doesn't Have. Who Pays? (Explained Like You're 5)",
  "thumb_text": "−$404 BILLION",
  "klasse": "N",
  "cluster": "staatsschulden",
  "testplatz": true,
  "anlass": {
    "was": "Monthly Treasury Statement vom 12.11.2026: Haushaltsdefizit Oktober 404 Mrd. Dollar, höchstes Oktober-Defizit bisher (Ausgaben 773 Mrd., Einnahmen 369 Mrd., Nettozinsen 103 Mrd.)",
    "datum": "2026-11-12",
    "url": "https://247wallst.com/investing/2026/11/13/the-u-s-just-ran-its-biggest-october-deficit-ever-404-billion/"
  },
  "zahl": {
    "wert": "404 Mrd. Dollar Defizit im Oktober 2026",
    "url": "https://www.roic.ai/news/us-october-budget-deficit-hits-record-404-billion-as-spending-surges-receipts-fall-11-12-2026"
  },
  "belege": [
    "TmlvDH0ZFB4"
  ],
  "szene": "Im Rathaus von Dannys Stadt legt der Kämmerer die Oktober-Abrechnung auf den Tisch: 773 Münzen ausgegeben, 369 eingenommen; Danny fragt, wer die Lücke füllt, Maya zeigt auf die Schuldscheine in Ricks Tresor.",
  "folge": [
    "Zinsen: 103 Milliarden Dollar in einem Monat und was das mit Hypotheken- und Sparzinsen macht",
    "Monthly Treasury Statement für November (Mitte Dezember): wird aus dem Rekordmonat ein Rekordjahr?"
  ]
}
```

```
KANDIDAT: The U.S. Just Spent $404 Billion It Doesn't Have. Who Pays? (Explained Like You're 5)
Cluster: staatsschulden | Klasse: N | geprueft am 2026-11-18
 [OK ] 1 Klasse N oder Z
        Klasse N (E=Erklaerstueck/Firma/Person/Geschichte und R=Ratgeber sind gesperrt: 1 Treffer in 34 Videos)
 [OK ] 2 Belege: >=2 Videos >=30.000 von >=2 kleinen Kanaelen, <=60 Tage (Testplatz: 1 Video >=100.000, hoechstens 1x pro 7 Tage)
        TESTPLATZ | PENNY 1,100,000 (3w ago)
 [OK ] 3 Anlass mit Quelle, hoechstens 7 Tage alt
        Monthly Treasury Statement vom 12.11.2026: Haushaltsdefizit Oktober 404 Mrd. Dollar, höchstes Oktober-Defizit bisher (Ausgaben 773 Mrd., Einnahmen 369 Mrd., Nettozinsen 103 Mrd.) | 2026-11-12 = 6 Tage | https://247wallst.com/investing/2026/11/13/the-u-s-just-ran-its-biggest-october-deficit-ever-404-billion/
 [OK ] 4 Belegte Zahl, im Titel oder Thumbnail
        404 Mrd. Dollar Defizit im Oktober 2026 | https://www.roic.ai/news/us-october-budget-deficit-hits-record-404-billion-as-spending-surges-receipts-fall-11-12-2026
 [OK ] 5 Titel: <=60 Zeichen vor der Klammer, Gegenwartsform/Frage, kein Portraet-Muster
        59 Zeichen | Muster: Just | Sperrwort: keins
 [OK ] 6 Kein kopierter Titel, kein eigenes Thema doppelt
        aehnlichster fremder Titel 0.58: Who Does America Owe $40 Trillion? (Explained Like | eigener 0.36
 [OK ] 7 Thumbnail-Text: 1-3 Woerter, Zahl oder Frage zum Anlass
        −$404 BILLION
 [OK ] 8 In Dannys Stadt spielbar (Szene benannt)
        Im Rathaus von Dannys Stadt legt der Kämmerer die Oktober-Abrechnung auf den Tisch: 773 Mü
 [OK ] 9 Zwei Folgewinkel fuer den Fall eines Treffers
        Zinsen: 103 Milliarden Dollar in einem Monat und was das mit Hypotheken- und Sparzinsen macht / Monthly Treasury Statement für November (Mitte Dezember): wird aus dem Rekordmonat ein Rekordjahr?

ERGEBNIS: FREIGABE
```

**Classic:** 1946. Nach dem Zweiten Weltkrieg liegt die US-Staatsschuld über der Wirtschaftsleistung eines ganzen Jahres; wer hat sie bezahlt, und wie lange hat es gedauert?

**Quellen:** [24/7 Wall St., Oktober-Defizit](https://247wallst.com/investing/2026/11/13/the-u-s-just-ran-its-biggest-october-deficit-ever-404-billion/) · [ROIC.ai, Meldung vom 12.11.](https://www.roic.ai/news/us-october-budget-deficit-hits-record-404-billion-as-spending-surges-receipts-fall-11-12-2026) (nur Überschrift geprüft) · [AZ Free News, Schuldenstand 40,55 Billionen](https://azfreenews.com/2026/11/u-s-national-debt-surpasses-40-5-trillion-up-2-46-trillion-in-one-year/)

Hinweis zur Prüfung: Dieser Kandidat lief zuerst mit dem Titelanfang „America Just Lost $404 Billion …“ und bekam die Freigabe. Ich habe den Titel zurückgezogen, weil ein Defizit kein Verlust ist, und den Logeintrag dazu gelöscht, damit der Testplatz nicht doppelt gezählt wird. Die Ausgabe oben gehört zum jetzigen Titel.

## 3. Sendeplan heute

Laut Abschnitt 5 der Strategie ist am Mittwoch, 18.11., **Preise/Inflation** an der Reihe. Dazu passt **Kandidat 1**. Donnerstag (Vom Gehalt leben) passt Kandidat 2, Freitag (Testplatz Staatsschulden) Kandidat 3; beide prüft der Scout morgen und übermorgen neu.

## 4. Abgelehnt

- Haus, Bauträger senken Preise (NAHB 17.11.): Titel mit 66 Zeichen zu lang (Punkt 5), dazu die November-Werte nur in einer Quelle bestätigt. Nicht nachgebessert, weil Haus erst am Samstag wieder an der Reihe ist.

## 5. Neue Muster bei Titeln (Thumbnails in diesem Lauf nicht angesehen)

- PENNY tauscht Titel nach der Veröffentlichung: Der Nvidia-Treffer (111.000) heißt jetzt „The Dinner That Cost Jensen Huang Nvidia“, ohne Klammer; zwei schwächere Videos haben die Klammer neu bekommen. In der Datenbank stehen weiter die ersten Titel.
- Money Mechanics (Kanal von 2021) stellt nachträglich auf „How Are [Gruppe] Affording $X on a $Y Salary?“ um (38.000 in 4 Tagen); Money With Ricky holt mit demselben Rahmen für Kanada 158.000 in 7 Tagen. Der Rahmen trifft mit einer genau benannten Gruppe und einem Fahrzeug, nicht mit „Americans“ allgemein.
- „The Economics of Owning an Electric Vehicle in [Land]“: Aussie Money Fix 208.000 in 4 Tagen, Money With Ricky zieht für Kanada nach.
- Derselbe Titel „How Many Retirees Actually Have $500,000? (NEW Fed Data)“ trifft bei zwei Kanälen (39.000 und 29.000). Der Zusatz „(NEW Fed Data)“ ist ein Anlass-Signal im Titel.
- Explained Like You're Five: die letzten zehn Videos alle unter 8.000; PENNY hat mit einem Grundlagenvideo („Once You Understand the Economy …“) 20.000 nach einem Tag, mehr als bei Klasse E sonst.
