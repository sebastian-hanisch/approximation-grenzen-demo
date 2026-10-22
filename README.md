# Approximation und ihre Grenze: Garantie, Christofides, Nichtapproximierbarkeit – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-approximation-grenzen-demo.streamlit.app/)** -->

Sechstes Stück der **Komplexitätsklassen-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Stück 5 ([fptas-rucksack-demo](https://github.com/sebastian-hanisch/fptas-rucksack-demo)) hat gezeigt, wie Runden eine Garantie kauft; Stück 3 ([reduktionskette-demo](https://github.com/sebastian-hanisch/reduktionskette-demo)) hat die Reduktionen geliefert, aus denen hier die Grenze folgt. Dieses Stück fragt: **Wenn ein Problem NP-schwer ist, wie nah am Optimum kommt man mit einem schnellen Verfahren, was kostet die Garantie, und wann ist keine zu haben?** Vehikel ist der **Rundweg** (Handlungsreisender; exakt wie in [zuordnung-vs-rundreise-demo](https://github.com/sebastian-hanisch/zuordnung-vs-rundreise-demo), Stück 1). Anders als die Fall-Demos zeigt sie **eine Frage der Komplexitätstheorie** an einem wachsenden Beispiel.

## Warum dieses Problem

Zwei Hälften. **Mit Dreiecksungleichung** (jede Direktverbindung ist höchstens so lang wie jeder Umweg) gibt es zwei Verfahren mit **bewiesener Güte**: die **MST-Verdopplung** (höchstens das Doppelte des Optimums) und **Christofides** (höchstens das Anderthalbfache). Die Demo misst, wie weit sie tatsächlich vom Optimum entfernt sind, sucht eine schlechte Instanz und legt den Beweisschritt von Christofides („Gerüst ≤ Optimum, Paarung ≤ halbes Optimum“) an echten Zahlen offen. **Ohne Dreiecksungleichung** gibt es unter P ≠ NP **gar keine** feste Garantie: aus einem Graphen wird per Reduktion eine Rundweg-Instanz (Kosten 1 auf den Kanten, M auf den Nichtkanten), und ein Verfahren mit Faktor ρ würde bei M > ρ · n den Hamiltonkreis entscheiden. Die Demo prüft die Konstruktion an allen kleinen Graphen und zeigt, dass der Faktor einfacher Heuristiken mit M wächst. Aufwand wird in **Tabellenzellen und Zuständen** gezählt, nie in Sekunden.

## Modell

- **Punkte.** n = 5 bis 14 Punkte in der Ebene, ganzzahlige Koordinaten (eigener SplitMix64-Generator, deshalb auf jeder Plattform dieselben Instanzen); drei Verteilungen: gleichverteilt, in drei Gruppen gehäuft, schmaler Streifen (fast eine Gerade). Entfernung euklidisch (erfüllt die Dreiecksungleichung bis auf Rechenfehler unter 10^−9).
- **MST-Verdopplung.** Gerüst nach Prim, jede Kante doppelt, Eulerkreis (Hierholzer), Abkürzung (erster Besuch). Verlust höchstens 2 · Gerüst ≤ 2 · Optimum.
- **Christofides.** Gerüst, Knoten mit ungeradem Grad, **exakt billigste perfekte Paarung** per Bitmasken-DP, Eulerkreis des Vielfachgraphen, Abkürzung. Rundweg ≤ Gerüst + Paarung ≤ 3/2 · Optimum.
- **Maßstab.** Held–Karp: Tabelle über (Teilmenge ohne Punkt 0, letzter Punkt), Zellen (n − 1) · 2^(n − 1) (bei n = 14: 106.496); dazu der nächste Nachbar und Greedy-Kanten als einfache Heuristiken ohne Garantie.
- **Die Familie ohne Dreiecksungleichung.** Graph mit eingepflanztem Hamiltonkreis (verdeckte Reihenfolge) und Köderkanten (jedes weitere Paar mit der gewählten Wahrscheinlichkeit), Kosten 1 auf den Kanten, M auf allen anderen Paaren; das Optimum ist **n**, ohne es zu rechnen. Bei M ≤ 2 gilt die Dreiecksungleichung.
- Mathematik (Beweis der Garantien 2 und 3/2, Reduktion) und Annahmentabelle: Expander **📐 Mathematische Formulierung** in der App.

## Methodik

| Baustein | Datei | Anmerkung |
|---|---|---|
| Gerüst, ungerade Knoten, Paarung, Eulerkreis, Abkürzung, die zwei Verfahren, Held–Karp, nächster Nachbar, Greedy-Kanten, Hamiltonkreis-Familie | `apx_algorithm.py` | eigene Einheiten; `double_tree_tour` und `christofides_tour` setzen nur die Bausteine zusammen; Gleichstandsregeln im Kopf der Datei |
| Punktfamilien | `apx_scenario.py` | drei Verteilungen |
| SplitMix64 | `apx_rng.py` | **wörtliche Kopie** von reduktionskette-demo/red_scenario.py (Commit ba24648); Regressionstest: die ersten Werte der Konvention |
| Messreihen, Hügelsteigen, Prüfung vor der Anzeige, Verdikte | `apx_evaluation.py` | alle Verdikte als reine Funktionen |

Experimente in der App: **Wie gut sind die garantierten Verfahren wirklich?** (Knopf, rund 10 Sekunden), **Wie nah kommt man der Garantie?** (Knopf, rund 5 Sekunden), **Warum der Hamiltonkreis die Grenze zeigt**, **Wenn die Dreiecksungleichung fehlt** (beide sofort).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Messreihen: 40 feste Instanzen je Zelle (`SWEEP_SEEDS`), Optimum durch Held–Karp; Verhältnisse auf drei Stellen gerundet; die Zahlen der Presets sind Einzelinstanzen und als solche ausgewiesen.

| Frage | Befund |
|---|---|
| **Wie gut sind die Verfahren mit Garantie, gleichverteilt?** | Median / Maximum des Verhältnisses zum Optimum bei n = 6 / 8 / 10 / 12 / 14: **MST-Verdopplung** 1,082 / 1,118 / 1,172 / 1,202 / 1,222 (Maximum 1,209 / 1,375 / 1,331 / 1,362 / 1,452), **Christofides** 1,012 / 1,033 / 1,034 / 1,070 / 1,075 (Maximum 1,139 / 1,132 / 1,138 / 1,162 / 1,182), **nächster Nachbar** (ohne Garantie) 1,072 / 1,087 / 1,115 / 1,133 / 1,124 (Maximum 1,357 / 1,383 / 1,315 / 1,415 / 1,417) (`test_claim_quality_tables`). |
| **Gehäuft und Streifen** | Gehäuft (drei Gruppen): Verdopplung im Median 1,012 bis 1,049 (Maximum bis 1,307), Christofides 1,005 bis 1,026 (Maximum bis 1,112), nächster Nachbar 1,013 bis 1,061 (Maximum bis 1,193). Schmaler Streifen: alle drei im Median 1,001 bis 1,008, Maximum 1,012 bis 1,017 für Verdopplung und Christofides, **1,237 für den nächsten Nachbarn**: dort ist das Gerüst ein Weg, und beide Verfahren sind fast optimal. |
| **Halten die Garantien?** | **In allen 600 Läufen** (3 Verteilungen, 5 Größen, 40 Instanzen): ja. Das größte gemessene Verhältnis ist 1,452 (Verdopplung, Garantie 2) und 1,182 (Christofides, Garantie 1,5), beide bei gleichverteilten Punkten und n = 14 (`test_claim_the_guarantees_hold_in_all_600_runs_and_are_far_from_reached`). |
| **Ist die garantierte Verdopplung besser als eine einfache Heuristik?** | **Bei gleichverteilten Punkten nicht:** die Verdopplung war in 87 von 200 Läufen länger als der nächste Nachbar (8 / 13 / 23 / 18 / 25 bei n = 6 bis 14; bei kleinem n sind viele Läufe gleich lang), bei gehäuften in 37 von 200, auf dem Streifen in 0 von 200; im Median liegt sie bei gleichverteilten Punkten in allen fünf Größen über ihm (1,082 gegen 1,072 bei n = 6 bis 1,222 gegen 1,124 bei n = 14), bei gehäuften knapp darunter. Die Verdopplung zählt hier mit der Abkürzung über den Eulerkreis in Einfügereihenfolge; mit einer anderen gültigen Wahl des Eulerkreises können die Werte, besonders bei den gehäuften Punkten, anders ausfallen. Christofides ist im Median in keiner der 15 Zellen schlechter als Verdopplung oder nächster Nachbar (auf dem Streifen auf drei Stellen gleich gut), kann aber in einzelnen Läufen länger sein (`test_claim_doubling_is_longer_than_nearest_neighbour_in_87_of_200_uniform_runs`). |
| **Beweisgrößen** | Gleichverteilt, Median: Gerüst / Optimum 0,663 / 0,689 / 0,727 / 0,751 / 0,764 und Paarung / Optimum 0,409 / 0,377 / 0,358 / 0,378 / 0,377 (n = 6 bis 14): beide **unter ihren Schranken 1 und 1/2**; ungerade Knoten im Median 4 / 4 / 4 / 6 / 6. Auf dem Streifen sind es 0,502 bis 0,508 und 0,499 bis 0,500 mit zwei ungeraden Knoten (der Weg). |
| **Wie nah kommt eine gesuchte Instanz der Garantie?** | Hügelsteigen über die Lage von 8 Punkten (4 Neustarts, 700 Schritte): schlechteste gefundene Verhältnisse **1,572** (Verdopplung; je Neustart 1,572 / 1,524 / 1,504 / 1,556) und **1,315** (Christofides; 1,315 / 1,310 / 1,293 / 1,296): deutlich unter 2 und 1,5, aber weit über dem Zufallsmaximum bei n = 8 (1,375 und 1,132). Ein Fund einer Suche, **kein Beleg für die Schärfe der Schranke** (`test_claim_the_search_stays_below_the_guarantees`). |
| **Stimmt die Reduktion?** | Hamiltonkreis ⇔ Optimum ≤ ρ · n bei M = ρ · n + 1, geprüft für ρ = 1, 2, 3 an **allen 64 Graphen mit n = 4** (10 mit Hamiltonkreis), **allen 1.024 mit n = 5** (218) und 300 Zufallsgraphen mit n = 6 (53): 4.164 Prüfungen, **0 Abweichungen** (`test_claim_reduction_on_all_small_graphs`). |
| **Wächst der Faktor mit M?** | 12 Knoten, Köder 15 %, 40 feste Instanzen je M, Optimum n; Median der Kosten durch n bei M = 1 / 2 / 3 / 5 / 10 / 20 / 50 / 100 / 1.000: nächster Nachbar 1,0 / 1,17 / 1,33 / 1,67 / 2,5 / 4,17 / 9,17 / 17,5 / 167,5; Greedy-Kanten dasselbe; Verdopplung 1,0 / 1,29 / 1,58 / 2,17 / 3,62 / 6,54 / 15,29 / 29,88 / 292,38; Christofides wie der nächste Nachbar. **Linear in M** (ein falscher Schritt kostet M statt 1). Den Kreis fanden bei M ≥ 2 nur 3 (nächster Nachbar, Greedy), 0 (Verdopplung) und 1 (Christofides) von 40 Läufen. Die Dreiecksungleichung ist bei M ≤ 2 erfüllt (0 Verletzungen) und ab M = 3 verletzt; bei **M = 2 ist jeder Rundweg höchstens 2 · n lang** (größtes gemessenes Verhältnis 1,500): die Güte 2 ist dort trivial (`test_claim_factor_grows_with_m`). |
| **Tabellengröße** | Held–Karp: (n − 1) · 2^(n − 1) Zellen: 160 (n = 6), 4.608 (n = 10), 106.496 (n = 14) (`test_claim_table_sizes_follow_the_formula`). |
| **Presets (Einzelinstanzen)** | Optimum / Verdopplung / Christofides / nächster Nachbar (Verhältnisse) / Zustände der Paarung: Standardfall (n = 10) 3.017,5 / 1,136 / 1,080 / 1,232 / 12; Lehrbeispiel (n = 6) 2.069,5 / 1,045 / 1,022 / 1,045 / 4; Gehäufte Punkte 1.294,6 / 1,074 / 1,038 / 1,066 / 4; Schmaler Streifen 1.831,8 / 1,001 / 1,001 / 1,001 / 1; Größte Instanz (n = 14) 3.670,8 / 1,203 / 1,100 / 1,117 / 33. Eingepflanzte Instanz (Kosten durch n für nächster Nachbar / Greedy / Verdopplung / Christofides): Standardfall bei M = 10: 3,7 / 1,9 / 3,7 / 1,9; bei M = 100: 30,7 / 10,9 / 30,7 / 10,9; bei M = 2: 1,3 / 1,1 / 1,3 / 1,1 (`test_claim_presets_are_single_instances_with_these_values`). |

## Ehrliche Grenzen

- **Die Garantie beschreibt den schlimmsten Fall.** Auf Zufallsinstanzen liegen beide Verfahren weit darunter (Maximum 1,452 gegen 2 und 1,182 gegen 1,5); die gesuchte Instanz kommt näher (1,572 und 1,315), erreicht die Schranke aber nicht. **Enge Beispiele aus der Literatur** (Verhältnis → 2 bzw. → 3/2 für wachsendes n) sind nicht nachgebaut und hier nicht belegt.
- **Die Nichtexistenz einer Garantie ist keine Messung.** Die Messreihe über M zeigt vier **Heuristiken**; dass **jedes** Verfahren mit festem Faktor scheitert, steht nur unter der Annahme P ≠ NP und folgt aus der Reduktion (Sahni und Gonzalez 1976), die die Demo an kleinen Graphen prüft, nicht beweist.
- **Ohne Köder ist die Familie für drei der vier Heuristiken leicht.** Bei Köder 0 % ist die Instanz selbst ein Kreis: nächster Nachbar, Greedy-Kanten und Christofides finden ihn in 40 von 40 Läufen (Kosten n), die Verdopplung nur in 12 (bei M = 1.000, 12 Knoten); bei 5 / 15 / 30 / 50 % Köder sind es 15 / 3 / 5 / 9 (nächster Nachbar) von 40 (`test_claim_decoy_density_matters`). Der Anteil ist **nicht monoton** im Köder. Erst mit Köderkanten zeigt sich der Mechanismus, und auch dann sind es Heuristiken, nicht „jedes Verfahren“.
- **Das Optimum gibt es nur bis n = 14.** Held–Karp verdoppelt die Tabelle mit jedem Punkt; die Verhältnisse sind exakt, aber auf kleinen Instanzen gemessen (n bis 14), nicht für große.
- **Die Paarung per Bitmasken-DP** ist exakt, aber exponentiell in der Zahl der ungeraden Knoten (bei n ≤ 14 höchstens 14, im Median 4 bis 6); Christofides rechnet sie in Polynomialzeit (Blossom, siehe `weighted-blossom-demo`). Die Verfahren wurden nicht auf Laufzeit verglichen.
- **Gleichstände** (Gerüst, Paarung, Eulerkreis) folgen festen Regeln (Kopf von `apx_algorithm.py`); andere Regeln geben andere, ebenso gültige Rundwege. Die Werte von Verdopplung und Christofides in den Tabellen hängen von diesen Regeln ab, besonders von der Wahl des Eulerkreises.
- **Zellen und Zustände sind keine Laufzeit.**
- **Die gesuchte Instanz hängt vom Zufalls-Seed der Suche ab;** vier Neustarts mit je 700 Schritten sind eine kleine Suche, kein Maximum.

## Befunde und Korrekturen gegenüber dem Plan

- **H4 widerlegt für die Verdopplung:** „die garantierten Verfahren sind im Mittel besser als einfache Heuristiken“ stimmt für **Christofides**, nicht für die **MST-Verdopplung**: sie ist bei gleichverteilten Punkten im Median schlechter als der nächste Nachbar.
- **H6 nur teilweise bestätigt:** „die gesuchte Instanz erreicht die Garantie fast“: 1,572 gegen 2 und 1,315 gegen 1,5, nach kleiner Suche.
- **Die zweite Reduktionszeile wurde im Bau geändert:** Der Plan sah „G ohne eine Kante des Kreises“ vor. Mit Köderkanten (Standard 15 %) hat dieser Graph meist **noch** einen Hamiltonkreis, die Zeile zeigte dann zweimal „ja“. Jetzt behält ein Knoten nur noch **eine** Kante (Grad 1, sicher kein Hamiltonkreis).
- **Die Verdopplung läuft über denselben Eulerkreis-Baustein** wie Christofides (Hierholzer auf dem verdoppelten Gerüst, dann Abkürzung) statt über eine Tiefensuche; beide sind Abkürzungen eines Eulerkreises des verdoppelten Gerüsts, die Garantie 2 gilt für jede.
- **Garantie-Suche:** die Größe (n = 8, 4 Neustarts, 700 Schritte) wurde aus der Vormessung übernommen; die gefundenen Verhältnisse weichen ab (Vormessung 1,614 und 1,325 mit anderen Seeds, hier 1,572 und 1,315).
- **Die Hauptansicht zeigt zusätzlich „Zustände der Paarung“** (Bitmasken-DP), damit der Aufwand der Paarung neben der Held–Karp-Tabelle steht.

## Verifikation

- **Kern:** jede Einheit gegen Handrechnung an Mini-Instanzen (Manhattan-Entfernung, ganzzahlig; `tests/conftest.py`, `tests/test_algorithm.py`): Gerüst (Prim mit Gleichstandsregel), ungerade Knoten, Paarung samt Zahl der Zustände (4 bei 4 Knoten, 12 bei 6 von Hand abgezählt), Eulerkreis (Stapel von Hand), Abkürzung, beide Verfahren Schritt für Schritt, Held–Karp, nächster Nachbar, Greedy-Kanten, die Hamiltonkreis-Familie; Randfälle (n = 1 bis 3, alle Punkte gleich, ungerade Knotenzahl, nicht zusammenhängender Vielfachgraph).
- **Orakel** (`tests/test_oracle_approximation_grenzen.py`): Held–Karp gegen Brute Force (228 Instanzen, euklidisch und nicht metrisch, n bis 8) und gegen CP-SAT (12 Instanzen, `ortools`, im CI ohne ortools übersprungen); Gerüst-Gewicht gegen `networkx.minimum_spanning_edges` (30 Instanzen); Paarung gegen das Aufzählen aller Paarungen (60 Instanzen, bis 8 Knoten) und `networkx.min_weight_matching` (15, im CI ohne networkx übersprungen); Eulerkreis gegen einen unabhängigen Prüfer (jede Kante genau einmal, 90 Kreise); **die Garantien als harte Prüfung auf 360 euklidischen Instanzen** zusammen mit den Beweisgrößen (Gerüst ≤ Optimum, Paarung ≤ halbes Optimum, Rundweg ≤ Gerüst + Paarung); die Reduktion gegen Brute Force auf allen 64 Graphen mit 4 Knoten und ρ = 1, 2, 3; die eingepflanzte Familie hat das Optimum n (Held–Karp).
- **Kopie** (`tests/test_copies.py`): wortgleich mit dem Original, solange es im Portfolio-Ordner liegt, dazu die bekannten ersten Werte der SplitMix64-Konvention.
- **Prüfung vor der Anzeige:** `validation_errors` prüft jeden Rundweg, die Kosten, die Garantien (mit Toleranz), die Beweisgrößen, bei n ≤ 8 Brute Force, die Dreiecksungleichung, den eingepflanzten Kreis und die Reduktion (`tests/test_evaluation.py`, jede Meldung ausgelöst, auch an den Grenzen).
- **Verdikte** als reine Funktionen, jede Zahl im Text und jede Schwelle an handgesetzten Werten (`tests/test_verdicts.py`); **Claims:** jede Zahl dieser README (`tests/test_claims.py`).
- **Presets:** vollständig, gültige Werte, erstes Preset gleich Standard (`tests/test_presets.py`); Randfälle der Regler (`tests/test_edge_cases.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button einschließlich der beiden Messreihen, jeder Regler an den Grenzen), Permalink mit Begrenzung, Layout (ein geänderter Regler hebt die Markierung des alten Presets auf), Footer.
- **Browser:** Standardansicht, beide Messreihen per Klick, Reduktion und Faktor über M; keine Konsolenmeldung.

## Mutationsprüfung und großer Lauf

- **Großer Lauf im Scratch-Ordner (nicht im Repo):** 1.320 Held–Karp-Instanzen gegen Brute Force (euklidisch und nicht metrisch, n bis 8), 810 euklidische Instanzen (n = 4 bis 12, drei Verteilungen) mit **den Garantien und allen Beweisgrößen** als harte Prüfung, 800 Paarungen gegen das Aufzählen, 600 Eulerkreise gegen den unabhängigen Prüfer, die Reduktion auf allen Graphen mit n = 4 und 5 und 2.000 Zufallsgraphen mit n = 6 (9.264 Prüfungen), 240 eingepflanzte Instanzen (Optimum n) und 30 Hügelsteigen-Suchen: **0 Abweichungen**.
- **Mutationsprüfung** (`tools/mutate_demo.py`, über `apx_algorithm.py` und `apx_evaluation.py`, die das Werkzeug über die Orakel-Tests erreicht; Darstellung, PDF, Presets, Szenario und Oberfläche mutiert es nicht, sie sind durch Rauch-, Verdikt-, Claims- und Orakel-Tests abgesichert; die wörtliche Kopie `apx_rng.py` ist ausgenommen, ihre Tests liegen in Stück 3): **339 Stellen**, davon **289 gefangen**, 24 als **äquivalent festgehalten** (`tests/mutation_state.json`), 24 durch wortgleiche Zeilen in Nachbar-Demos gesichert und 2 mit Zeitüberschreitung (Endlosschleifen in der Greedy-Kanten-Suche, zählen nicht). Die Lücken des ersten Laufs (Eulerkreis für zwei Punkte, Rundweg ab drei Knoten, Toleranzen der Prüfungen und der Verdikte, Grenzen der Messreihen) wurden mit Grenztests geschlossen. Äquivalent sind zum Beispiel Schutzabfragen, die der Hierholzer-Baustein von allein erfüllt (n = 1), Schleifengrenzen, bei denen die letzte Runde leer ist, die Größe von M in der Reduktion (jedes M > ρ · n genügt, auch etwas kleineres) und Gleichstandsregeln in Held–Karp und im Hügelsteigen, die nur die Wahl zwischen gleich guten Lösungen ändern.


## Einordnung und Quellen (anhand der Quellen geprüft)

Nichtapproximierbarkeit des allgemeinen Rundwegs: Sahni und Gonzalez, *P-complete approximation problems*, Journal of the ACM 23 (1976), S. 555 bis 565 (geprüft; die Konstruktion mit Kosten 1 auf den Kanten und einer großen Zahl auf den Nichtkanten ist die der Demo). PTAS für den euklidischen Rundweg: Arora, *Polynomial time approximation schemes for Euclidean traveling salesman and other geometric problems*, Journal of the ACM 45 (1998), S. 753 bis 782 (geprüft). Faktor 3/2 für den metrischen Rundweg: Christofides 1976 (technischer Bericht, hier **nicht nachgeschlagen**); eine Verbesserung auf 3/2 − ε mit ε > 10^−36: Karlin, Klein und Oveis Gharan, Operations Research 2024 (laut Zusammenfassung geprüft; Beweis nicht eingesehen). Der Beweis der Garantien in der App ist die übliche Lehrbuchfassung, nicht aus einer Quelle abgeschrieben.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: eine Instanz mit drei Verfahren, Christofides Schritt für Schritt, vier Experimente, Garantien im Portfolio, Annahmentabelle, Formeln |
| `apx_algorithm.py` | Kern: Gerüst, Paarung, Eulerkreis, Abkürzung, die zwei Verfahren, Held–Karp, Heuristiken, Hamiltonkreis-Familie |
| `apx_constants.py` | Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben, Presets |
| `apx_evaluation.py` | Analyse, Messreihen, Hügelsteigen, Reduktion, Prüfung vor der Anzeige, Verdikte, Zahlenformate |
| `apx_layout.py` | Fester Kopf (Stylesheet) |
| `apx_pdf_export.py` | PDF-Bericht (fpdf2) |
| `apx_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `apx_rng.py` | wörtliche Kopie: SplitMix64 aus Stück 3 |
| `apx_scenario.py` | Punktfamilien |
| `apx_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen, Orakel, Kopie, Auswertung, Verdikte, Claims, Presets, Randfälle, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Enge Beispiele für beide Garantien:** aus der Literatur bekannt, hier weder nachgebaut noch belegt.
- **Polynomielle Paarung (Blossom) in dieser Demo:** die Bitmasken-DP genügt bis n = 14; das polynomielle Verfahren steht in `weighted-blossom-demo`.
- **PTAS für den euklidischen Rundweg und Verfahren für den Rundweg mit Kosten 1 und 2:** eigene Themen; nur als Einordnung genannt.
- **Lokale Verbesserung (2-opt) und Held–Karp-Schranke als Untergrenze für große n:** würden das Optimum für n > 14 ersetzen, sind aber ein anderes Stück.
- **Optimum über n = 14:** die exakte Tabelle wäre in der App zu groß.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
