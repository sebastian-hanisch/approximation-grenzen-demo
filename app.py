"""Approximation und ihre Grenze: Garantie, Christofides, Nichtapproximierbarkeit - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Sechstes Stück der Komplexitätsklassen-Reihe: wie nah am Optimum ein schnelles Verfahren kommt, was die Garantie kostet und wann keine zu haben ist. Aufwand in Tabellenzellen und Zuständen, nie in Sekunden.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import apx_algorithm as A
import apx_constants as C
from apx_evaluation import (
    ALL_METHODS,
    Settings,
    analyse,
    fmt_factor,
    fmt_int,
    fmt_median,
    fmt_num,
    fmt_ratio,
    reduction_all,
    search_worst_case,
    sweep_m,
    sweep_quality,
    validation_errors,
    verdict_m,
    verdict_proof,
    verdict_quality,
    verdict_reduction,
    verdict_reduction_all,
    verdict_run,
    verdict_search,
)
from apx_layout import dunkles_design, kopf_css
from apx_pdf_export import build_pdf
from apx_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from apx_visualization import (
    build_christofides_map,
    build_graph,
    build_m,
    build_proof_bars,
    build_quality,
    build_ratio_bars,
    build_tour_map,
)

st.set_page_config(page_title="Approximation und ihre Grenze – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _quality(family):
    return sweep_quality(family)


@st.cache_data(show_spinner=False)
def _search():
    return [search_worst_case("dt"), search_worst_case("chr")]


@st.cache_data(show_spinner=False)
def _m_sweep():
    return sweep_m()


@st.cache_data(show_spinner=False)
def _reduction_all():
    return reduction_all()


@st.cache_data(show_spinner=False)
def _pdf(settings):
    return build_pdf(analyse(settings))


def _md_table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def _route(tour):
    return " → ".join(str(v) for v in list(tour) + [tour[0]])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in apx_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧭 Approximation und ihre Grenze: Garantie, Christofides, Nichtapproximierbarkeit")
st.markdown(
    """
Wenn ein Problem NP-schwer ist, bleibt die Frage: **wie nah am Optimum** kommt man mit einem schnellen Verfahren, und wann ist **keine Garantie** zu haben? Die Demo geht dem am **Rundweg** (Handlungsreisender) nach.
Mit **Dreiecksungleichung** (jede Direktverbindung ist höchstens so lang wie jeder Umweg) gibt es zwei Verfahren mit **bewiesener Güte**: die **MST-Verdopplung** (höchstens das Doppelte des Optimums) und **Christofides**
(höchstens das Anderthalbfache). **Ohne** sie kippt es: aus einem Graphen wird per Reduktion eine Rundweg-Instanz, und ein Verfahren mit fester Garantie würde den Hamiltonkreis entscheiden; die Heuristiken scheitern dort
an einem Faktor, der mit den Kosten M der Nichtkanten wächst. Aufwand wird in **Tabellenzellen und Zuständen** gezählt, nicht in Sekunden.
Sechstes Stück der Komplexitätsklassen-Reihe; die Fall-Demos behandeln einzelne Anwendungen, hier steht eine Frage der Komplexitätstheorie im Mittelpunkt.

Weiter unten: die Experimente **🔬 Wie gut sind die garantierten Verfahren wirklich?**, **🔬 Wie nah kommt man der Garantie?**, **🔬 Warum der Hamiltonkreis die Grenze zeigt** und **🔬 Wenn die Dreiecksungleichung fehlt**,
dann **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("Vier Klassen, zwei Fragen", expanded=True):
    st.markdown(
        """
1. **Wie gut kann man sein?** Der Faktor ρ eines Verfahrens ist das schlechteste Verhältnis „Kosten des Verfahrens durch Optimum“ über alle Instanzen. **FPTAS**: jedes ε (Rucksack, Stück 5). **PTAS**: jedes ε, aber der Aufwand wächst
   stark mit 1 / ε (euklidischer Rundweg, Arora 1998). **APX**: ein fester Faktor (metrischer Rundweg: 3/2 nach Christofides). **Nicht in APX** (unter P ≠ NP): überhaupt kein fester Faktor (allgemeiner Rundweg, Sahni und Gonzalez 1976).
2. **Was trägt die Garantie?** Beim metrischen Rundweg die Dreiecksungleichung: sie erlaubt das Abkürzen, ohne dass die Strecke länger wird. Fehlt sie, kostet ein falscher Schritt beliebig viel.
3. **Wo steht die Demo?** Sie baut die beiden Verfahren mit Garantie, misst, wie weit sie tatsächlich vom Optimum entfernt sind, sucht eine schlechte Instanz und zeigt die Reduktion, die die Grenze erklärt. Bewiesen wird nichts: die Sätze stehen in der Literatur.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Punkte (Rundweg mit Dreiecksungleichung)**")
    n = st.slider("Punkte n", *bounds("n_slider"), key="n_slider", help="Auslieferstellen in der Ebene. Bis 14 Punkte rechnet die App das Optimum exakt (Held–Karp). Auch die Reduktion unten verwendet n.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Punkte generieren", width="stretch", on_click=randomize_seed)
    family = st.selectbox("Verteilung der Punkte", list(C.FAMILIES), format_func=C.FAMILIES.get, key="family_select", help="Gleichverteilt, in drei Gruppen gehäuft oder auf einem schmalen Streifen (fast eine Gerade).")
    method = st.selectbox("Verfahren in der Karte", list(C.METHODS), format_func=C.METHODS.get, key="method_select", help="Dieser Rundweg wird in der Karte durchgezogen gezeichnet, das Optimum gestrichelt.")
    st.markdown("**Ohne Dreiecksungleichung (Experimente 3 und 4)**")
    rho = st.select_slider("Angenommener Faktor ρ", options=list(C.RHO_OPTIONS), key="rho_select", help="Ein ρ-Approximationsverfahren würde mit M = ρ · n + 1 den Hamiltonkreis entscheiden.")
    m = st.select_slider("Kosten M der Nichtkanten", options=list(C.M_OPTIONS), format_func=fmt_int, key="m_select", help="Kanten des Graphen kosten 1, alle anderen Paare M. Bei M = 2 gilt die Dreiecksungleichung noch.")
    p = st.select_slider("Köder-Kanten in Promille", options=list(C.P_OPTIONS), key="p_select", help="Zusätzliche Kanten neben dem eingepflanzten Hamiltonkreis, mit dieser Wahrscheinlichkeit je Paar. Ohne Köder ist die Instanz selbst ein Kreis und leicht.")

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "family_select": family, "method_select": method, "rho_select": int(rho), "m_select": int(m), "p_select": int(p)})

settings = Settings(n=int(n), seed=int(seed), family=family, method=method, rho=int(rho), m=int(m), p=int(p))
a = _analysis(settings)
for message in validation_errors(a):
    st.error(message)

# --- Eine Instanz ---------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Eine Instanz, drei Verfahren")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Optimum (Held–Karp)", fmt_num(a.opt.cost, 1), help="Kürzester Rundweg, exakt gerechnet.")
c2.metric("MST-Verdopplung", fmt_ratio(a.ratio("dt")), help="Kosten geteilt durch das Optimum. Garantie: höchstens 2.")
c3.metric("Christofides", fmt_ratio(a.ratio("chr")), help="Kosten geteilt durch das Optimum. Garantie: höchstens 1,5.")
c4.metric("Nächster Nachbar", fmt_ratio(a.ratio("nn")), help="Kosten geteilt durch das Optimum. Keine Garantie.")
c5, c6 = st.columns(2)
c5.metric("Zellen der Tabelle (Held–Karp)", fmt_int(a.opt.cells), help="(n − 1) · 2^(n − 1): die exakte Rechnung verdoppelt sich mit jedem Punkt.")
c6.metric("Zustände der Paarung", fmt_int(A.min_matching(a.dist, a.chr.odd).states), help=f"Bitmasken-DP über die {len(a.chr.odd)} Knoten mit ungeradem Grad im Gerüst.")
vkind, vtext = verdict_run(a)
getattr(st, vkind)(vtext)
g1, g2 = st.columns([3, 2])
with g1:
    st.plotly_chart(build_tour_map(a.points, a.tour(method), a.opt.tour, C.METHODS[method]), width="stretch", key="tour_map")
    st.caption(f"{C.METHODS[method]}: {_route(a.tour(method))}. Optimum (gestrichelt): {_route(a.opt.tour)}.")
with g2:
    st.plotly_chart(build_ratio_bars({k: a.ratio(k) for k in C.METHODS}), width="stretch", key="ratio_bars")
    st.caption("Die roten Striche sind die Garantien. Der nächste Nachbar hat keine.")

st.markdown("### Christofides Schritt für Schritt")
h1, h2 = st.columns([3, 2])
with h1:
    st.plotly_chart(build_christofides_map(a.points, a.chr), width="stretch", key="chr_map")
with h2:
    st.plotly_chart(build_proof_bars(a), width="stretch", key="proof_bars")
st.markdown(
    f"**Gerüst:** {', '.join(f'{x}–{y}' for x, y in a.chr.mst_edges)}.  **Ungerade Knoten:** {', '.join(str(v) for v in a.chr.odd) or 'keine'}.  "
    f"**Paarung:** {', '.join(f'{x}–{y}' for x, y in a.chr.matching) or 'keine'}.  **Eulerkreis:** {_route(a.chr.circuit[:-1])}.  **Abgekürzt:** {_route(a.chr.tour)}."
)
vkind, vtext = verdict_proof(a)
getattr(st, vkind)(vtext)
if st.button("📄 PDF erstellen"):
    st.session_state["pdf_for"] = settings
if st.session_state.get("pdf_for") == settings:
    st.download_button("⬇️ PDF herunterladen", data=_pdf(settings), file_name="approximation-und-ihre-grenze.pdf", mime="application/pdf")

st.markdown("## ❓ Kernfrage: Wie nah am Optimum, und wann ist keine Garantie zu haben?")
st.markdown(
    "Die Experimente trennen drei Dinge: wie weit die Verfahren mit **Garantie** in der Praxis vom Optimum entfernt sind (weit besser als die Garantie, aber nicht immer besser als einfache Heuristiken), "
    "wie nah eine **gesuchte** Instanz der Garantie kommt, und warum es ohne Dreiecksungleichung **gar keine** Garantie gibt."
)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie gut sind die garantierten Verfahren wirklich?")
st.caption(f"{len(C.SWEEP_SEEDS)} feste Instanzen je Größe (Verteilung: {C.FAMILIES[settings.family]}), Optimum durch Held–Karp; Median und Maximum des Verhältnisses „Kosten durch Optimum“. Rund 10 Sekunden.")
if st.button("▶️ Messreihe Güte rechnen"):
    st.session_state["quality_on"] = True
if st.session_state.get("quality_on"):
    with st.spinner(f"Rechne die Güte (Größen {C.SWEEP_SIZES[0]} bis {C.SWEEP_SIZES[-1]}, {len(C.SWEEP_SEEDS)} Instanzen, Optimum exakt) …"):
        quality = _quality(settings.family)
    st.plotly_chart(build_quality(quality), width="stretch", key="quality_chart")
    st.markdown(_md_table(
        ["n", "Verdopplung: Median / Maximum", "Christofides: Median / Maximum", "nächster Nachbar: Median / Maximum", "Gerüst / Optimum", "Paarung / Optimum", "ungerade Knoten (Median)"],
        [[r["n"]] + [f"{fmt_ratio(r['median'][k])} / {fmt_ratio(r['max'][k])}" for k in ("dt", "chr", "nn")] + [fmt_ratio(r["mst_over_opt"]), fmt_ratio(r["matching_over_opt"]), fmt_median(r["odd_median"])] for r in quality],
    ))
    vkind, vtext = verdict_quality(quality)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Wie nah kommt man der Garantie?")
st.caption(
    f"Hügelsteigen über die Lage von {C.SEARCH_N} Punkten: ein Punkt wird verschoben, behalten wird, was das Verhältnis zum Optimum vergrößert ({C.SEARCH_RESTARTS} Neustarts, {C.SEARCH_STEPS} Schritte je Verfahren). "
    "Gefunden wird eine **schlechte Instanz**, kein Beweis für die Schärfe der Schranke. Rund 5 Sekunden."
)
if st.button("▶️ Schlechte Instanz suchen"):
    st.session_state["search_on"] = True
if st.session_state.get("search_on"):
    with st.spinner("Suche schlechte Instanzen (zwei Verfahren) …"):
        found = _search()
    s1, s2 = st.columns(2)
    for col, res in zip((s1, s2), found):
        with col:
            dist = A.euclid_matrix(res.points)
            tour = A.double_tree_tour(dist).tour if res.method == "dt" else A.christofides_tour(dist).tour
            st.plotly_chart(build_tour_map(res.points, tour, A.held_karp(dist).tour, C.METHODS[res.method]), width="stretch", key=f"search_{res.method}")
            st.caption(f"{C.METHODS[res.method]}: schlechtestes gefundenes Verhältnis {fmt_ratio(res.best)}; je Neustart {', '.join(fmt_ratio(x) for x in res.restarts)}.")
    vkind, vtext = verdict_search(found)
    getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Warum der Hamiltonkreis die Grenze zeigt")
st.caption(
    "Aus einem Graphen G auf n Knoten wird eine Rundweg-Instanz: Kanten von G kosten 1, alle anderen Paare M = ρ · n + 1. Gibt es einen Hamiltonkreis, kostet der beste Rundweg n; gibt es keinen, mindestens n − 1 + M > ρ · n. "
    "Ein Verfahren mit Garantie ρ müsste also beide Fälle unterscheiden: es würde den Hamiltonkreis entscheiden. Unten der Graph der eingepflanzten Instanz (Zufalls-Seed, n, Köder und ρ aus den Reglern)."
)
st.plotly_chart(build_graph(a.settings.n, A.graph_edges(a.planted.dist), a.planted.cycle), width="stretch", key="graph_chart")
st.markdown(_md_table(
    ["Graph", "Kanten", "Hamiltonkreis (Brute Force)", "Optimum der Instanz (Held–Karp)", "Schwelle ρ · n", "Meldung eines ρ-Approximationsverfahrens"],
    [[r.label, r.edges, "ja" if r.has_cycle else "nein", fmt_num(r.opt, 1), fmt_int(int(r.threshold)), "Hamiltonkreis" if r.decided else "kein Hamiltonkreis"] for r in a.reduction],
))
vkind, vtext = verdict_reduction(a.reduction, settings.rho, settings.n)
getattr(st, vkind)(vtext)
red_all = _reduction_all()
vkind, vtext = verdict_reduction_all(red_all)
getattr(st, vkind)(vtext)

st.markdown("---")

st.subheader("🔬 Experiment: Wenn die Dreiecksungleichung fehlt")
st.caption(
    f"Eingepflanzte Instanzen ({C.M_SWEEP_N} Knoten, Köder {C.M_SWEEP_P / 10:g} %, {len(C.M_SWEEP_SEEDS)} feste Instanzen je M): das Optimum ist n. Vier Heuristiken ohne Garantie für diese Familie; "
    "dargestellt sind die Kosten geteilt durch n. Der exakte Löser bliebe bei 1, aber seine Tabelle verdoppelt sich mit jedem Knoten."
)
m_rows = _m_sweep()
st.plotly_chart(build_m(m_rows), width="stretch", key="m_chart")
st.markdown(_md_table(
    ["M", "Dreiecksungleichung verletzt", "nächster Nachbar", "Greedy-Kanten", "Verdopplung", "Christofides"],
    [[fmt_int(r["m"]), "nein" if r["violations"] == 0 else "ja"] + [f"{fmt_factor(r['median'][k])} ({r['found'][k]} von {r['count']} finden den Kreis)" for k in ALL_METHODS] for r in m_rows],
))
vkind, vtext = verdict_m(m_rows)
getattr(st, vkind)(vtext)
st.markdown(f"**Die Instanz aus den Reglern** (n = {settings.n}, M = {fmt_int(settings.m)}, Köder {settings.p / 10:g} %): Kosten durch n")
st.markdown(_md_table(
    [ALL_METHODS[k] for k in ALL_METHODS],
    [[f"{fmt_factor(a.planted_costs[k] / settings.n)}" + (" (Kreis gefunden)" if a.planted_costs[k] <= settings.n + C.TOLERANCE else "") for k in ALL_METHODS]],
))

st.markdown("---")

st.subheader("📚 Garantien im Portfolio")
st.markdown(
    """
| Verfahren | Garantie | Wo |
|---|---|---|
| Wert-Skalierung für den Rucksack | mindestens 1 − ε des Optimums (FPTAS) | Stück 5 der Reihe, `fptas-rucksack-demo` |
| MST-Verdopplung für den metrischen Rundweg | höchstens das 2-Fache | dieses Stück |
| Christofides für den metrischen Rundweg | höchstens das 3/2-Fache | dieses Stück |
| KMB und TM für den Steinerbaum | 2 (1 − 1/t) | `steiner-tree-demo` |
| Goemans–Williamson für den PCST | 2-Approximation | `pcst-demo` |
| Greedy für die Knotenüberdeckung | **keine** Garantie: auf der Greedy-Falle wächst der Faktor | `vertex-cover-demo` |
"""
)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Dreiecksungleichung gilt** | Die Garantien 2 und 3/2 gelten nur dort. Ohne sie (Experimente 3 und 4) gibt es unter P ≠ NP **kein** festes ρ; die Demo zeigt die Konstruktion, nicht den Beweis. | `weighted-blossom-demo` (die Paarung im Polynomialzeit-Verfahren) |
| **Die Garantie beschreibt typische Instanzen** | Sie ist eine Aussage über den schlimmsten Fall. Auf Zufallsinstanzen liegen beide Verfahren weit darunter, die Verdopplung ist oft nicht besser als der nächste Nachbar. | – |
| **Die gesuchte Instanz zeigt die Schärfe** | Das Hügelsteigen findet nur eine schlechte Instanz; enge Beispiele aus der Literatur (Verhältnis → 2 bzw. → 3/2 für wachsendes n) sind nicht nachgebaut. | – |
| **Das Optimum ist für große n verfügbar** | Held–Karp verdoppelt die Tabelle mit jedem Punkt; die App rechnet bis n = 14. Darüber gäbe es kein exaktes Verhältnis. | `zuordnung-vs-rundreise-demo` |
| **Die Paarung per Bitmasken-DP ist das Verfahren** | Sie ist exakt, aber exponentiell in der Zahl der ungeraden Knoten (bei n ≤ 14 höchstens 14); Christofides rechnet die Paarung polynomial (Blossom). | `weighted-blossom-demo` |
| **Heuristiken stehen für „jedes Verfahren“** | Die Messreihe über M zeigt vier Heuristiken. Dass **jedes** Verfahren scheitert, steht nur unter der Annahme P ≠ NP und folgt aus der Reduktion, nicht aus der Messung. | `reduktionskette-demo` |
| **Bester bekannter Faktor** | Für den metrischen Rundweg ist 3/2 seit 1976 der bekannte Faktor; Karlin, Klein und Oveis Gharan geben 3/2 − ε mit einem winzigen ε > 10^−36 an (Operations Research 2024). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(r"**Metrik.** Eine Entfernung $d$ ist metrisch, wenn $d(a, c) \le d(a, b) + d(b, c)$ für alle Punkte gilt. Dann ist jede Abkürzung höchstens so lang wie der Umweg.")
    st.markdown(r"**MST-Verdopplung.** Sei $T$ ein billigstes Gerüst. Jeder Rundweg ist ein Gerüst plus eine Kante, also $d(T) \le \mathrm{OPT}$. Der Eulerkreis des verdoppelten Gerüsts hat die Länge $2 \, d(T)$, die Abkürzung ist nicht länger:")
    st.latex(r"d(\text{Rundweg}) \;\le\; 2 \, d(T) \;\le\; 2 \cdot \mathrm{OPT}")
    st.markdown(r"**Christofides.** Sei $O$ die Menge der Knoten mit ungeradem Grad in $T$ (eine gerade Zahl), $M$ eine billigste perfekte Paarung auf $O$. Die Abkürzung des optimalen Rundwegs auf $O$ ist ein Kreis, dessen zwei abwechselnde Paarungen zusammen höchstens $\mathrm{OPT}$ kosten; die billigere hat höchstens das halbe:")
    st.latex(r"d(M) \le \tfrac{1}{2} \, \mathrm{OPT}, \qquad d(\text{Rundweg}) \le d(T) + d(M) \le \mathrm{OPT} + \tfrac{1}{2} \, \mathrm{OPT} = \tfrac{3}{2} \, \mathrm{OPT}")
    st.markdown(r"**Reduktion.** Zu einem Graphen $G$ auf $n$ Knoten und $\rho \ge 1$ setze $c(a, b) = 1$ für Kanten und $c(a, b) = M > \rho n$ sonst. Hat $G$ einen Hamiltonkreis, ist $\mathrm{OPT} = n$; sonst benutzt jeder Rundweg mindestens eine Nichtkante:")
    st.latex(r"\mathrm{OPT} \;\ge\; (n - 1) + M \;>\; \rho \, n")
    st.markdown(r"Ein Verfahren mit Faktor $\rho$ lieferte im ersten Fall höchstens $\rho n$, im zweiten mehr als $\rho n$: es entschiede den Hamiltonkreis (unter $\mathrm{P} \ne \mathrm{NP}$ gibt es ein solches Verfahren also nicht). Bei $M \le 2$ ist $c$ metrisch, und jeder Rundweg kostet höchstens $2n \le 2 \, \mathrm{OPT}$.")
    st.markdown(
        r"""
| Annahme | Bedeutung | Wer setzt an |
|---|---|---|
| Euklidische Entfernung | erfüllt die Dreiecksungleichung (Rechenfehler unter 10^−9) | – |
| Gleichstand im Gerüst | kleinster Index zuerst, Vorgänger nur bei echt kleinerem Schlüssel | – |
| Paarung exakt | Bitmasken-DP über die ungeraden Knoten, Gleichstand: zuerst gefundene | `weighted-blossom-demo` |
| Eulerkreis | Hierholzer ab Punkt 0, Kanten in Einfügereihenfolge | `euler-tour-demo` |
| Abkürzung | jeder Punkt beim ersten Besuch | – |

**Folgestücke.** Stück 7 der Reihe (parametrisierte Komplexität) fragt, ob ein kleiner Parameter hilft, Stück 8 (Zufall) zeigt Verfahren, die mit Wahrscheinlichkeit richtig sind.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
