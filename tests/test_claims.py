"""Jede Zahl der README steht hier und wird über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Alle Instanzen kommen aus dem eigenen SplitMix64-Generator (plattform- und versionsunabhängig); Zähler sind exakt, Verhältnisse stehen als auf drei Stellen gerundete Dezimalzahlen (`fmt_ratio`)."""

import pytest

import apx_algorithm as A
import apx_constants as C
import apx_evaluation as ev

R = ev.fmt_ratio

# --- Befund 1: Güte der garantierten Verfahren ----------------------------------------------------------------------------------------------------

# n: (Median dt, chr, nn), (Maximum dt, chr, nn), dt länger als nn, Gerüst / OPT, Paarung / OPT, ungerade Knoten (Median)
QUALITY = {
    "uni": {
        6: (("1,082", "1,012", "1,072"), ("1,209", "1,139", "1,357"), 8, "0,663", "0,409", 4.0),
        8: (("1,118", "1,033", "1,087"), ("1,375", "1,132", "1,383"), 13, "0,689", "0,377", 4.0),
        10: (("1,172", "1,034", "1,115"), ("1,331", "1,138", "1,315"), 23, "0,727", "0,358", 4.0),
        12: (("1,202", "1,070", "1,133"), ("1,362", "1,162", "1,415"), 18, "0,751", "0,378", 6.0),
        14: (("1,222", "1,075", "1,124"), ("1,452", "1,182", "1,417"), 25, "0,764", "0,377", 6.0),
    },
    "clu": {
        6: (("1,012", "1,005", "1,013"), ("1,147", "1,056", "1,119"), 2, "0,550", "0,470", 2.0),
        8: (("1,022", "1,012", "1,029"), ("1,163", "1,065", "1,128"), 7, "0,562", "0,459", 4.0),
        10: (("1,032", "1,017", "1,041"), ("1,177", "1,082", "1,193"), 8, "0,577", "0,459", 4.0),
        12: (("1,039", "1,021", "1,052"), ("1,297", "1,106", "1,177"), 10, "0,589", "0,454", 6.0),
        14: (("1,049", "1,026", "1,061"), ("1,307", "1,112", "1,172"), 10, "0,594", "0,450", 6.0),
    },
    "lin": {
        6: (("1,001", "1,001", "1,002"), ("1,012", "1,012", "1,237"), 0, "0,502", "0,500", 2.0),
        8: (("1,002", "1,002", "1,003"), ("1,012", "1,012", "1,098"), 0, "0,504", "0,499", 2.0),
        10: (("1,005", "1,005", "1,005"), ("1,016", "1,016", "1,074"), 0, "0,506", "0,499", 2.0),
        12: (("1,006", "1,006", "1,007"), ("1,017", "1,017", "1,176"), 0, "0,508", "0,499", 2.0),
        14: (("1,007", "1,006", "1,008"), ("1,016", "1,016", "1,089"), 0, "0,508", "0,499", 2.0),
    },
}


@pytest.fixture(scope="module", params=list(QUALITY))
def quality(request):
    return request.param, ev.sweep_quality(request.param)


def test_claim_quality_tables(quality):
    """README: Median und Maximum des Verhältnisses zum Optimum, Gerüst / OPT, Paarung / OPT und ungerade Knoten je Verteilung und Größe (40 feste Instanzen je Zelle, Optimum durch Held–Karp)."""
    family, rows = quality
    assert [r["n"] for r in rows] == list(C.SWEEP_SIZES) and all(r["count"] == 40 and r["skipped"] == 0 and r["violations"] == 0 for r in rows)
    for r in rows:
        med, mx, worse, mst, match, odd = QUALITY[family][r["n"]]
        assert tuple(R(r["median"][k]) for k in ("dt", "chr", "nn")) == med, (family, r["n"])
        assert tuple(R(r["max"][k]) for k in ("dt", "chr", "nn")) == mx, (family, r["n"])
        assert r["dt_worse_than_nn"] == worse and R(r["mst_over_opt"]) == mst and R(r["matching_over_opt"]) == match and r["odd_median"] == odd


def test_claim_the_guarantees_hold_in_all_600_runs_and_are_far_from_reached():
    """README: in allen 600 Läufen (3 Verteilungen, 5 Größen, 40 Instanzen) hielten beide Garantien; größtes Verhältnis 1,452 (Verdopplung, gleichverteilt, n = 14) und 1,182 (Christofides, gleichverteilt, n = 14)."""
    big = {"dt": 0.0, "chr": 0.0}
    total = 0
    for family in QUALITY:
        for n, (_, mx, *_rest) in QUALITY[family].items():
            total += 40
            big["dt"], big["chr"] = max(big["dt"], float(mx[0].replace(",", "."))), max(big["chr"], float(mx[1].replace(",", ".")))
    assert total == 600 and (big["dt"], big["chr"]) == (1.452, 1.182)


def test_claim_doubling_is_longer_than_nearest_neighbour_in_87_of_200_uniform_runs():
    """README: bei gleichverteilten Punkten war die Verdopplung in 87 von 200 Läufen länger als der nächste Nachbar (8 + 13 + 23 + 18 + 25), bei gehäuften in 37 von 200, auf dem Streifen in 0."""
    assert [sum(v[2] for v in QUALITY[f].values()) for f in ("uni", "clu", "lin")] == [87, 37, 0]


# --- Befund 2: gesuchte schlechte Instanz ---------------------------------------------------------------------------------------------------


def test_claim_the_search_stays_below_the_guarantees():
    """README (n = 8, 4 Neustarts, 700 Schritte): schlechteste gefundene Verhältnisse 1,572 (Verdopplung; je Neustart 1,572, 1,524, 1,504, 1,556) und 1,315 (Christofides; 1,315, 1,310, 1,293, 1,296)."""
    dt, ch = ev.search_worst_case("dt"), ev.search_worst_case("chr")
    assert (R(dt.best), [R(x) for x in dt.restarts]) == ("1,572", ["1,572", "1,524", "1,504", "1,556"])
    assert (R(ch.best), [R(x) for x in ch.restarts]) == ("1,315", ["1,315", "1,310", "1,293", "1,296"])
    assert dt.best < 2 and ch.best < 1.5 and dt.n == ch.n == 8
    dist = A.euclid_matrix(dt.points)
    assert A.double_tree_tour(dist).cost / A.held_karp(dist).cost == pytest.approx(dt.best)


# --- Befund 3: Reduktion ----------------------------------------------------------------------------------------------------------------------


def test_claim_reduction_on_all_small_graphs():
    """README: Hamiltonkreis ⇔ Optimum ≤ ρ · n (M = ρ · n + 1) auf allen 64 Graphen mit n = 4 (10 mit Hamiltonkreis) und allen 1.024 mit n = 5 (218), dazu 300 Zufallsgraphen mit n = 6 (53 mit Hamiltonkreis), ρ = 1, 2, 3: 4.164 Prüfungen, 0 Abweichungen."""
    res = ev.reduction_all()
    assert res == {"sizes": (4, 5), "graphs": 1088, "with_cycle": 228, "random_n": 6, "random_count": 300, "random_with_cycle": 53, "checks": 4164, "mismatches": 0}


# --- Befund 4: Faktor über M ------------------------------------------------------------------------------------------------------------------

M_TABLE = {   # M: (Verletzungen der Dreiecksungleichung, größtes Verhältnis, Median nn, greedy, dt, chr, gefunden nn, greedy, dt, chr)
    1: (0, "1,000", 1.0, 1.0, 1.0, 1.0, (40, 40, 40, 40)),
    2: (0, "1,500", 1.17, 1.17, 1.29, 1.17, (3, 3, 0, 1)),
    3: (3218, "2,000", 1.33, 1.33, 1.58, 1.33, (3, 3, 0, 1)),
    5: (3218, "3,000", 1.67, 1.67, 2.17, 1.67, (3, 3, 0, 1)),
    10: (3218, "5,500", 2.5, 2.5, 3.62, 2.5, (3, 3, 0, 1)),
    20: (3218, "10,500", 4.17, 4.17, 6.54, 4.17, (3, 3, 0, 1)),
    50: (3218, "25,500", 9.17, 9.17, 15.29, 9.17, (3, 3, 0, 1)),
    100: (3218, "50,500", 17.5, 17.5, 29.88, 17.5, (3, 3, 0, 1)),
    1000: (3218, "500,500", 167.5, 167.5, 292.38, 167.5, (3, 3, 0, 1)),
}


def test_claim_factor_grows_with_m():
    """README (12 Knoten, Köder 15 %, 40 feste Instanzen je M, Optimum n): Median der Kosten durch n für vier Heuristiken, Anteil der Läufe, die den Kreis finden, Verletzungen der Dreiecksungleichung."""
    rows = ev.sweep_m()
    assert [r["m"] for r in rows] == list(M_TABLE) and all(r["count"] == 40 for r in rows)
    for r in rows:
        viol, worst, nn, gr, dt, ch, found = M_TABLE[r["m"]]
        assert r["violations"] == viol and R(r["worst"]) == worst, r["m"]
        assert tuple(round(r["median"][k], 2) for k in ("nn", "greedy", "dt", "chr")) == (nn, gr, dt, ch), r["m"]
        assert tuple(r["found"][k] for k in ("nn", "greedy", "dt", "chr")) == found, r["m"]
    assert max(r["worst"] for r in rows if r["m"] == 2) <= 2.0                           # M = 2: jeder Rundweg höchstens 2 · n
    assert rows[-1]["median"]["dt"] / rows[0]["median"]["dt"] == pytest.approx(292.38, abs=0.01)


def test_claim_decoy_density_matters():
    """README (12 Knoten, M = 1.000, 40 feste Instanzen): Läufe, die den Kreis finden (nächster Nachbar, Greedy-Kanten, Verdopplung, Christofides), bei Köder 0 / 5 / 15 / 30 / 50 %: 40 / 40 / 12 / 40, 15 / 15 / 3 / 11, 3 / 3 / 0 / 1, 5 / 3 / 0 / 1, 9 / 9 / 0 / 4."""
    expected = {0: (40, 40, 12, 40), 50: (15, 15, 3, 11), 150: (3, 3, 0, 1), 300: (5, 3, 0, 1), 500: (9, 9, 0, 4)}
    for p, found in expected.items():
        row = ev.sweep_m(n=12, p=p, ms=(1000,))[0]
        assert tuple(row["found"][k] for k in ("nn", "greedy", "dt", "chr")) == found, p
    assert ev.sweep_m(n=12, p=0, ms=(1000,))[0]["median"]["nn"] == 1.0


# --- Presets (Einzelinstanzen) --------------------------------------------------------------------------------------------------------------

PRESET_TABLE = {   # Optimum, Verhältnisse dt / chr / nn, Zellen, Zustände der Paarung, ungerade Knoten, Kosten / n der eingepflanzten Instanz (nn, greedy, dt, chr), Hamiltonkreis der zwei Graphen
    "Standardfall (Voreinstellung)": ("3017,5", "1,136", "1,080", "1,232", 4608, 12, 6, (3.7, 1.9, 3.7, 1.9), (True, False)),
    "Lehrbeispiel (6 Punkte)": ("2069,5", "1,045", "1,022", "1,045", 160, 4, 4, (1.0, 1.0, 1.0, 1.0), (True, False)),
    "Gehäufte Punkte": ("1294,6", "1,074", "1,038", "1,066", 4608, 4, 4, (3.7, 1.9, 3.7, 1.9), (True, False)),
    "Schmaler Streifen": ("1831,8", "1,001", "1,001", "1,001", 4608, 1, 2, (3.7, 1.9, 3.7, 1.9), (True, False)),
    "Größte Instanz (14 Punkte)": ("3670,8", "1,203", "1,100", "1,117", 106496, 33, 8, (2.29, 2.29, 4.86, 2.29), (True, False)),
    "Nichtkanten sehr teuer (M = 100)": ("3017,5", "1,136", "1,080", "1,232", 4608, 12, 6, (30.7, 10.9, 30.7, 10.9), (True, False)),
    "Gerade noch metrisch (M = 2)": ("3017,5", "1,136", "1,080", "1,232", 4608, 12, 6, (1.3, 1.1, 1.3, 1.1), (True, False)),
}


def test_claim_presets_are_single_instances_with_these_values():
    """README, Preset-Tabelle."""
    got = {}
    for name, s in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**s))
        got[name] = (ev.fmt_num(a.opt.cost, 1), R(a.ratio("dt")), R(a.ratio("chr")), R(a.ratio("nn")), a.opt.cells, A.min_matching(a.dist, a.chr.odd).states, len(a.chr.odd),
                     tuple(round(a.planted_costs[k] / s["n"], 2) for k in ("nn", "greedy", "dt", "chr")), tuple(r.has_cycle for r in a.reduction))
    assert got == PRESET_TABLE


def test_claim_table_sizes_follow_the_formula():
    """README: die Tabelle von Held–Karp hat (n − 1) · 2^(n − 1) Zellen: 160 (n = 6), 4.608 (n = 10), 106.496 (n = 14)."""
    assert [A.held_karp(A.euclid_matrix(ev.make_points(n, 1, "uni"))).cells for n in (6, 10, 14)] == [160, 4608, 106496]
    assert [(n - 1) * 2 ** (n - 1) for n in (6, 10, 14)] == [160, 4608, 106496]


def test_claim_unit_is_cells_and_states_never_seconds():
    """README: Aufwand in Tabellenzellen und Zuständen, nie in Sekunden."""
    a = ev.analyse(ev.Settings())
    for text in (ev.verdict_run(a)[1], ev.verdict_proof(a)[1], ev.verdict_reduction(a.reduction, 2, 10)[1]):
        assert "Sekunden" not in text
