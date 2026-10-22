"""Verdikte und Zahlenformate an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen und jede genannte Zahl direkt."""

import apx_algorithm as A
import apx_evaluation as ev


def _analysis(opt=100.0, dt=150.0, chr_=120.0, nn=160.0, mst=80.0, match=40.0):
    tour = [0, 1, 2, 3]
    planted = A.planted_instance(4, 0, 5, 1)
    td = A.TourResult(tour, dt, [], mst, [], (), 0.0, [])
    tc = A.TourResult(tour, chr_, [], mst, [0, 1], ((0, 1),), match, [])
    reduction = (ev.ReductionRow("G", 4, True, 4.0, 4.0, True),)
    return ev.Analysis(ev.Settings(), (), [], A.HkResult(opt, tour, 24), td, tc, (tour, nn), planted, {"nn": 4.0, "greedy": 4.0, "dt": 4.0, "chr": 4.0}, reduction)


# --- Formate ------------------------------------------------------------------------------------------------------------------------------


def test_number_formats():
    assert ev.fmt_int(106496) == "106.496" and ev.fmt_int(12) == "12"
    assert ev.fmt_num(22.7) == "22,7" and ev.fmt_num(3, 2) == "3,00"
    assert ev.fmt_median(1234) == "1.234" and ev.fmt_median(52.5) == "52,5"
    assert ev.fmt_ratio(1.04666) == "1,047" and ev.fmt_ratio(2) == "2,000"
    assert ev.fmt_percent(80.0) == "80" and ev.fmt_percent(17.5) == "17,5"
    assert ev.fmt_share(7, 40) == "17,5 %" and ev.fmt_share(40, 40) == "100 %"
    assert ev.fmt_factor(17.5) == "17,50" and ev.fmt_factor(99.99) == "99,99" and ev.fmt_factor(100) == "100" and ev.fmt_factor(292.38) == "292"


# --- Verdikte -----------------------------------------------------------------------------------------------------------------------------


def test_verdict_run_success_names_all_three_ratios_and_the_best_method():
    kind, text = ev.verdict_run(_analysis(dt=150.0, chr_=120.0, nn=160.0))
    assert kind == "success"
    assert "Optimum 100,0." in text and "MST-Verdopplung 1,500 (Garantie 2)" in text and "Christofides 1,200 (Garantie 1,5)" in text
    assert "nächster Nachbar 1,600 (keine Garantie)" in text and "am besten: Christofides." in text


def test_verdict_run_info_when_the_heuristic_without_guarantee_beats_the_doubling():
    kind, text = ev.verdict_run(_analysis(dt=150.0, chr_=120.0, nn=130.0))
    assert kind == "info" and "besser als die Verdopplung" in text
    assert ev.verdict_run(_analysis(dt=150.0, chr_=120.0, nn=150.0))[0] == "success"            # gleich gut: nicht „besser“


def test_verdict_run_best_method_ties_and_nearest_neighbour():
    assert "am besten: Christofides." in ev.verdict_run(_analysis(dt=120.0, chr_=120.0, nn=170.0))[1]       # Gleichstand: alphabetisch zuerst
    assert "am besten: MST-Verdopplung." in ev.verdict_run(_analysis(dt=110.0, chr_=120.0, nn=170.0))[1]
    assert "am besten: nächster Nachbar." in ev.verdict_run(_analysis(dt=150.0, chr_=120.0, nn=105.0))[1]


def test_verdict_run_guarantee_boundaries():
    assert ev.verdict_run(_analysis(dt=200.0, chr_=150.0, nn=300.0))[0] != "error"             # genau 2 und 1,5: erlaubt
    assert ev.verdict_run(_analysis(dt=200.1, chr_=120.0, nn=300.0))[0] == "error"
    kind, text = ev.verdict_run(_analysis(dt=150.0, chr_=150.1, nn=300.0))
    assert kind == "error" and "Eine Garantie ist verletzt" in text


def test_verdict_proof_names_the_three_inequalities():
    kind, text = ev.verdict_proof(_analysis(opt=100.0, chr_=120.0, mst=80.0, match=40.0))
    assert kind == "success"
    assert "Gerüst 80,0 ≤ Optimum 100,0" in text and "Paarung 40,0 ≤ halbes Optimum 50,0" in text and "Rundweg 120,0 ≤ Gerüst plus Paarung 120,0" in text and "Anderthalbfache" in text


def test_verdict_proof_boundaries():
    """Jede Bedingung allein: die anderen bleiben erfüllt (sonst fängt eine andere den Fehler)."""
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=150.0, mst=100.0, match=50.0))[0] == "success"          # alles genau an der Grenze
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=100.0, mst=100.1, match=10.0))[0] == "error"            # nur das Gerüst
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=100.0, mst=60.0, match=50.1))[0] == "error"             # nur die Paarung
    kind, text = ev.verdict_proof(_analysis(opt=100.0, chr_=130.1, mst=80.0, match=50.0))                      # nur der Rundweg
    assert kind == "error" and "Eine Ungleichung des Beweises ist verletzt" in text
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=130.0, mst=80.0, match=50.0))[0] == "success"


def test_verdict_proof_tolerances_are_relative_to_the_size():
    """Rundungsfehler der Größenordnung 1e-9 · Wert sind erlaubt, nicht darüber: bei Optimum 100 sind das 1e-7."""
    barely = 0.5e-9 * 100
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=100.0, mst=100.0 + barely, match=10.0))[0] == "success"
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=100.0, mst=60.0, match=50.0 + barely))[0] == "success"
    assert ev.verdict_proof(_analysis(opt=100.0, chr_=130.0 + barely, mst=80.0, match=50.0))[0] == "success"


QUALITY_ROWS = [
    {"n": 6, "count": 40, "skipped": 0, "violations": 0, "dt_worse_than_nn": 8, "median": {"dt": 1.08, "chr": 1.01, "nn": 1.07}, "max": {"dt": 1.2, "chr": 1.14, "nn": 1.36},
     "mst_over_opt": 0.66, "matching_over_opt": 0.41, "odd_median": 4.0},
    {"n": 14, "count": 40, "skipped": 0, "violations": 0, "dt_worse_than_nn": 25, "median": {"dt": 1.222, "chr": 1.075, "nn": 1.124}, "max": {"dt": 1.452, "chr": 1.182, "nn": 1.417},
     "mst_over_opt": 0.76, "matching_over_opt": 0.38, "odd_median": 6.0},
]


def test_verdict_quality_names_worst_cases_and_medians_at_the_largest_size():
    kind, text = ev.verdict_quality(QUALITY_ROWS)
    assert kind == "info"
    assert "In allen 80 Läufen hielten die Garantien" in text
    assert "1,452 bei der Verdopplung (Garantie 2) und 1,182 bei Christofides (Garantie 1,5)" in text and "nächsten Nachbarn ohne Garantie 1,417" in text
    assert "Bei n = 14 lag der Median bei 1,222 (Verdopplung), 1,075 (Christofides) und 1,124 (nächster Nachbar)" in text
    assert "die Verdopplung war in 33 von 80 Läufen länger als der nächste Nachbar" in text


def test_verdict_quality_reports_violations_as_error():
    rows = [dict(QUALITY_ROWS[0], violations=2), dict(QUALITY_ROWS[1], violations=1)]
    kind, text = ev.verdict_quality(rows)
    assert kind == "error" and "3 von 80" in text


def test_verdict_search_names_both_findings_and_that_they_are_not_tight():
    found = [ev.SearchResult("dt", 8, 1.614, (), ()), ev.SearchResult("chr", 8, 1.325, (), ())]
    kind, text = ev.verdict_search(found)
    assert kind == "warning"
    assert "(8 Punkte)" in text and "MST-Verdopplung 1,614 (Garantie 2)" in text and "Christofides 1,325 (Garantie 1,5)" in text and "nicht die Schärfe der Schranke" in text


def test_verdict_reduction_names_threshold_and_message():
    rows = (ev.ReductionRow("G", 12, True, 10.0, 20.0, True), ev.ReductionRow("G, Knoten 8 nur mit einer Kante", 9, False, 30.0, 20.0, False))
    kind, text = ev.verdict_reduction(rows, 2, 10)
    assert kind == "info"
    assert "Mit M = ρ · n + 1 = 21" in text and "G: Optimum 10,0, Schwelle ρ · n = 20: ein 2-Approximationsverfahren würde „Hamiltonkreis“ melden (Brute Force: ja)" in text
    assert "Knoten 8 nur mit einer Kante: Optimum 30,0" in text and "würde „kein Hamiltonkreis“ melden (Brute Force: nein)" in text
    bad = (ev.ReductionRow("G", 12, True, 30.0, 20.0, False),)
    assert ev.verdict_reduction(bad, 2, 10)[0] == "error"


def test_reduction_row_agreement():
    assert ev.ReductionRow("G", 1, True, 4.0, 4.0, True).agrees and ev.ReductionRow("G", 1, False, 8.0, 4.0, False).agrees
    assert not ev.ReductionRow("G", 1, True, 8.0, 4.0, False).agrees and not ev.ReductionRow("G", 1, False, 4.0, 4.0, True).agrees


def test_verdict_reduction_all():
    res = {"sizes": (4, 5), "graphs": 1088, "with_cycle": 228, "random_n": 6, "random_count": 300, "random_with_cycle": 53, "checks": 4164, "mismatches": 0}
    kind, text = ev.verdict_reduction_all(res)
    assert kind == "success"
    assert "auf allen 1.088 Graphen mit n = 4 und 5 (228 mit Hamiltonkreis)" in text and "300 Zufallsgraphen mit n = 6 (53 mit Hamiltonkreis)" in text and "4.164 Prüfungen, 0 Abweichungen" in text
    kind, text = ev.verdict_reduction_all(dict(res, mismatches=2))
    assert kind == "error" and "2 von 4.164" in text


M_ROWS = [
    {"m": 2, "count": 40, "violations": 0, "worst": 1.5, "median": {"nn": 1.17, "greedy": 1.17, "dt": 1.29, "chr": 1.17}, "found": {"nn": 3, "greedy": 3, "dt": 0, "chr": 1}},
    {"m": 1000, "count": 40, "violations": 5000, "worst": 292.4, "median": {"nn": 167.5, "greedy": 167.5, "dt": 292.38, "chr": 167.5}, "found": {"nn": 3, "greedy": 3, "dt": 0, "chr": 1}},
]


def test_verdict_m_names_the_trivial_bound_and_the_growth():
    kind, text = ev.verdict_m(M_ROWS)
    assert kind == "info"
    assert "Bei M = 2 gilt die Dreiecksungleichung (0 Verletzungen)" in text and "höchstens 2 · n" in text and "das größte gemessene Verhältnis war 1,500" in text
    assert "Bei M = 1.000 liegen die Kosten im Median beim 168-Fachen (nächster Nachbar), 168-Fachen (Greedy-Kanten), 292-Fachen (Verdopplung) und 168-Fachen (Christofides) des Optimums n" in text
    assert "den Kreis fanden 3, 3, 0 und 1 von 40 Läufen" in text and "Der Faktor wächst mit M" in text


def test_verdict_m_without_the_row_for_m_equal_to_two():
    text = ev.verdict_m(M_ROWS[1:])[1]
    assert "Bei M = 2" not in text and "Bei M = 1.000" in text
