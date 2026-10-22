"""Auswertung: Einzelanalyse, Prüfungen vor der Anzeige (jede Fehlermeldung hat einen Test, auch die Grenzen) und die Messreihen an kleinen Konfigurationen."""

from dataclasses import replace
from statistics import median

import pytest

import apx_algorithm as A
import apx_constants as C
import apx_evaluation as ev
from apx_scenario import make_points


def _base(n=6):
    return ev.analyse(ev.Settings(n=n, seed=3))


def test_default_analysis_is_consistent():
    a = ev.analyse(ev.Settings())
    assert ev.validation_errors(a) == []
    assert a.points == make_points(C.DEFAULT_N, C.DEFAULT_SEED, C.DEFAULT_FAMILY)
    assert a.opt == A.held_karp(a.dist) and a.dt == A.double_tree_tour(a.dist) and a.chr == A.christofides_tour(a.dist)
    assert a.nn[0] == A.nearest_neighbour(a.dist) and a.nn[1] == A.tour_cost(a.dist, a.nn[0])
    assert a.planted == A.planted_instance(C.DEFAULT_N, C.DEFAULT_P, C.DEFAULT_M, C.DEFAULT_SEED)
    assert a.planted_costs == ev.planted_costs(a.planted)
    assert a.reduction == ev.reduction_rows(C.DEFAULT_N, C.DEFAULT_P, C.DEFAULT_RHO, C.DEFAULT_SEED)


def test_analysis_accessors():
    a = _base()
    assert a.cost("dt") == a.dt.cost and a.cost("chr") == a.chr.cost and a.cost("nn") == a.nn[1]
    assert a.tour("dt") == a.dt.tour and a.tour("chr") == a.chr.tour and a.tour("nn") == a.nn[0]
    assert a.ratio("chr") == a.chr.cost / a.opt.cost
    zero = replace(a, opt=replace(a.opt, cost=0.0))
    assert zero.ratio("dt") == 1.0
    half = replace(a, opt=replace(a.opt, cost=0.5))                                              # Optimum zwischen 0 und 1: wird geteilt
    assert half.ratio("dt") == a.dt.cost / 0.5


def test_planted_costs_cover_four_methods():
    inst = A.planted_instance(8, 150, 10, 4)
    c = ev.planted_costs(inst)
    assert set(c) == {"nn", "greedy", "dt", "chr"} == set(ev.ALL_METHODS)
    d = inst.dist
    assert c["nn"] == A.tour_cost(d, A.nearest_neighbour(d)) and c["greedy"] == A.tour_cost(d, A.greedy_edge(d))
    assert c["dt"] == A.double_tree_tour(d).cost and c["chr"] == A.christofides_tour(d).cost


def test_reduction_rows_live():
    rows = ev.reduction_rows(8, 150, 2, 4)
    assert rows[0].has_cycle and rows[0].decided and rows[0].opt == 8 and rows[0].threshold == 16
    assert not rows[1].has_cycle and not rows[1].decided and rows[1].opt >= 7 + 17 and "nur mit einer Kante" in rows[1].label
    assert all(r.agrees for r in rows)
    inst = A.planted_instance(8, 150, 17, 4)
    v = inst.cycle[0]
    degree = sum(1 for e in A.graph_edges(inst.dist) if v in e)
    assert degree > 1 and rows[1].edges == rows[0].edges - (degree - 1)                          # genau eine Kante bleibt am Knoten v
    assert str(v) in rows[1].label
    pruned = [e for e in A.graph_edges(inst.dist) if v not in e or e == (min(inst.cycle[0], inst.cycle[1]), max(inst.cycle[0], inst.cycle[1]))]
    assert rows[1].opt == A.held_karp(A.graph_cost_matrix(8, pruned, 2 * 8 + 1)).cost        # M = ρ · n + 1 (unabhängig nachgerechnet)
    assert ev.reduction_rows(8, 150, 3, 4)[1].opt >= 7 + 25                                       # M = 3 · 8 + 1


def test_brute_force_optimum():
    assert ev.brute_force_optimum([[0.0]]) == 0.0
    assert ev.brute_force_optimum([[0, 5], [5, 0]]) == 10
    assert ev.brute_force_optimum([[0, 1, 4], [1, 0, 2], [4, 2, 0]]) == 7


# --- Prüfungen vor der Anzeige: jede Meldung wird ausgelöst ---------------------------------------------------------------------------------------


def _msgs(a):
    return " | ".join(ev.validation_errors(a))


def test_validation_is_clean_for_untouched_results():
    assert ev.validation_errors(_base()) == []


def test_validation_flags_a_tour_that_misses_a_point_for_each_method():
    a = _base()
    assert "MST-Verdopplung: der Rundweg besucht nicht jeden Punkt" in _msgs(replace(a, dt=replace(a.dt, tour=a.dt.tour[:-1])))
    assert "Christofides: der Rundweg besucht nicht jeden Punkt" in _msgs(replace(a, chr=replace(a.chr, tour=a.chr.tour[:-1])))
    assert "nächster Nachbar: der Rundweg besucht nicht jeden Punkt" in _msgs(replace(a, nn=(a.nn[0][:-1], a.nn[1])))
    assert "Held–Karp: der Rundweg besucht nicht jeden Punkt" in _msgs(replace(a, opt=replace(a.opt, tour=a.opt.tour[:-1])))


def test_validation_flags_costs_that_do_not_match_the_tour():
    a = _base()
    assert "Christofides: die gemeldeten Kosten passen nicht zum Rundweg" in _msgs(replace(a, chr=replace(a.chr, cost=a.chr.cost + 1.0)))
    assert "nächster Nachbar: die gemeldeten Kosten passen nicht zum Rundweg" in _msgs(replace(a, nn=(a.nn[0], a.nn[1] + 1.0)))
    tiny = replace(a, chr=replace(a.chr, cost=a.chr.cost + 0.5 * ev.TOL * max(1.0, a.chr.cost)))
    assert "gemeldeten Kosten" not in _msgs(tiny)                                                     # innerhalb der Toleranz
    assert "gemeldeten Kosten" in _msgs(replace(a, chr=replace(a.chr, cost=a.chr.cost + 2 * ev.TOL * max(1.0, a.chr.cost))))


def test_validation_flags_a_tour_cheaper_than_the_optimum():
    a = _base()
    cheaper = replace(a, opt=replace(a.opt, cost=2 * max(a.dt.cost, a.chr.cost, a.nn[1])))
    assert "Christofides: der Rundweg ist billiger als das Optimum" in _msgs(cheaper)
    barely = replace(a, chr=replace(a.chr, cost=a.opt.cost - 0.5 * ev.TOL * max(1.0, a.opt.cost)))
    assert "Christofides: der Rundweg ist billiger" not in _msgs(barely)           # innerhalb der Toleranz


def test_validation_guarantee_boundaries_are_inclusive():
    a = _base()
    opt = a.opt.cost
    at_two = replace(a, dt=replace(a.dt, cost=2 * opt))
    assert "Garantie 2 der MST-Verdopplung" not in _msgs(at_two)
    assert "Garantie 2 der MST-Verdopplung" in _msgs(replace(a, dt=replace(a.dt, cost=2 * opt + 1e-3)))
    at_one_half = replace(a, chr=replace(a.chr, cost=1.5 * opt))
    assert "Garantie 3/2" not in _msgs(at_one_half)
    assert "Garantie 3/2" in _msgs(replace(a, chr=replace(a.chr, cost=1.5 * opt + 1e-3)))


def test_validation_flags_each_proof_quantity():
    a = _base()
    opt = a.opt.cost
    assert "Beweisgröße" not in _msgs(replace(a, chr=replace(a.chr, mst_cost=opt, matching_cost=opt / 2)))
    assert "Beweisgröße" in _msgs(replace(a, chr=replace(a.chr, mst_cost=opt + 1e-3)))
    assert "Beweisgröße" in _msgs(replace(a, chr=replace(a.chr, matching_cost=opt / 2 + 1e-3)))
    assert "länger als Gerüst plus Paarung" in _msgs(replace(a, chr=replace(a.chr, cost=a.chr.mst_cost + a.chr.matching_cost + 1.0)))
    assert "länger als Gerüst plus Paarung" not in _msgs(a)


def test_brute_force_probe_runs_up_to_eight_points_and_not_beyond():
    for n, expected in ((8, True), (9, False)):
        a = _base(n)
        wrong = replace(a, opt=replace(a.opt, cost=a.opt.cost * 0.9))
        assert ("Brute-Force-Probe" in _msgs(wrong)) is expected, n


def test_validation_flags_a_broken_metric_and_the_planted_family():
    a = _base()
    broken = [row[:] for row in a.dist]
    broken[0][1] = broken[1][0] = 10 ** 6
    assert "Dreiecksungleichung" in _msgs(replace(a, dist=broken))
    other = A.planted_instance(a.settings.n, 150, 99, 1)
    assert "eingepflanzte Kreis kostet nicht n" in _msgs(replace(a, planted=replace(other, cycle=[0, 1, 2, 3, 4, 5][::-1] if False else other.cycle[::2] + other.cycle[1::2])))
    low = {k: a.settings.n - 1.0 for k in a.planted_costs}
    assert "auf der eingepflanzten Instanz billiger" in _msgs(replace(a, planted_costs=low))
    exact = {k: float(a.settings.n) for k in a.planted_costs}
    assert "auf der eingepflanzten Instanz billiger" not in _msgs(replace(a, planted_costs=exact))


def test_validation_flags_a_disagreeing_reduction():
    a = _base()
    bad = (replace(a.reduction[0], decided=False), a.reduction[1])
    assert "Die Reduktion widerspricht" in _msgs(replace(a, reduction=bad))


# --- Messreihen ---------------------------------------------------------------------------------------------------------------------------


def test_sweep_quality_matches_independent_computation_and_counts():
    seeds = (1, 2, 3, 4, 5)
    rows = ev.sweep_quality("clu", sizes=(6, 7), seeds=seeds)
    assert [r["n"] for r in rows] == [6, 7]
    for row in rows:
        data = {"dt": [], "chr": [], "nn": []}
        mst, match, odd, worse = [], [], [], 0
        for s in seeds:
            d = A.euclid_matrix(make_points(row["n"], s, "clu"))
            opt = A.held_karp(d).cost
            dt, ch, nn = A.double_tree_tour(d), A.christofides_tour(d), A.tour_cost(d, A.nearest_neighbour(d))
            data["dt"].append(dt.cost / opt)
            data["chr"].append(ch.cost / opt)
            data["nn"].append(nn / opt)
            mst.append(ch.mst_cost / opt)
            match.append(ch.matching_cost / opt)
            odd.append(len(ch.odd))
            worse += dt.cost > nn * (1 + ev.TOL)
        assert row["count"] == 5 and row["skipped"] == 0 and row["violations"] == 0 and row["dt_worse_than_nn"] == worse
        for k in data:
            assert row["median"][k] == pytest.approx(median(data[k])) and row["max"][k] == pytest.approx(max(data[k]))
        assert row["mst_over_opt"] == pytest.approx(median(mst)) and row["matching_over_opt"] == pytest.approx(median(match)) and row["odd_median"] == median(odd)


def test_sweep_quality_counts_violations_and_skips_degenerate_instances(monkeypatch):
    monkeypatch.setattr(ev, "make_points", lambda n, seed, family: tuple((5, 5) for _ in range(n)))
    rows = ev.sweep_quality("uni", sizes=(5,), seeds=(1, 2))
    assert rows[0]["count"] == 0 and rows[0]["skipped"] == 2 and rows[0]["median"]["dt"] == 1.0 and rows[0]["max"]["chr"] == 1.0
    monkeypatch.undo()
    monkeypatch.setattr(ev.A, "double_tree_tour", lambda dist: A.TourResult(list(range(len(dist))), 1e9, [], 1.0, [], (), 0.0, []))
    assert ev.sweep_quality("uni", sizes=(5,), seeds=(1, 2))[0]["violations"] == 2


def test_search_is_deterministic_and_checks_its_method():
    a = ev.search_worst_case("dt", n=5, seed=3, steps=20, restarts=2)
    assert a == ev.search_worst_case("dt", n=5, seed=3, steps=20, restarts=2)
    assert a.method == "dt" and a.n == 5 and len(a.points) == 5 and a.best == max(a.restarts) and a.best >= 1.0
    assert all(0 <= x <= C.COORD_MAX and 0 <= y <= C.COORD_MAX for x, y in a.points)
    assert ev.search_worst_case("chr", n=5, seed=3, steps=20, restarts=2) != a
    with pytest.raises(ValueError):
        ev.search_worst_case("nn")


def test_search_improves_on_its_starting_point_with_more_steps():
    short = ev.search_worst_case("dt", n=6, seed=5, steps=5, restarts=1)
    long = ev.search_worst_case("dt", n=6, seed=5, steps=120, restarts=1)
    assert long.best >= short.best


def test_sweep_m_rows():
    rows = ev.sweep_m(n=8, p=150, ms=(1, 2, 20), seeds=(1, 2, 3, 4, 5))
    assert [r["m"] for r in rows] == [1, 2, 20] and all(r["count"] == 5 for r in rows)
    assert rows[0]["found"] == {k: 5 for k in ev.ALL_METHODS}                                  # M = 1: jeder Rundweg kostet n
    assert rows[1]["violations"] == 0 and rows[2]["violations"] > 0
    inst = A.planted_instance(8, 150, 20, 3)
    direct = ev.planted_costs(inst)
    assert rows[2]["worst"] >= max(direct.values()) / 8 - 1e-9
    assert all(rows[2]["median"][k] >= 1.0 for k in ev.ALL_METHODS)


def test_reduction_all_default_sizes_and_labels():
    res = ev.reduction_all()
    assert res["sizes"] == (4, 5) and res["graphs"] == 64 + 1024 and res["with_cycle"] == 10 + 218 and res["mismatches"] == 0
    assert res["random_n"] == 6 and res["random_count"] == 300 and res["random_with_cycle"] == 53 and res["checks"] == (1088 + 300) * 3


def test_search_ratio_of_degenerate_points_is_zero():
    assert ev._search_ratio([(5, 5)] * 4, "dt") == 0.0 and ev._search_ratio([(5, 5)] * 4, "chr") == 0.0
    assert ev._search_ratio([(0, 0), (1, 0), (0, 1), (1, 1)], "chr") >= 1.0


def test_guarantee_tolerances_in_the_validation_scale_with_the_cost():
    a = _base()
    opt = a.opt.cost
    assert opt > 100                                                                           # die Toleranz ist relativ: TOL · opt
    barely = 0.5 * ev.TOL * opt
    assert "Garantie 2" not in _msgs(replace(a, dt=replace(a.dt, cost=2 * opt + barely)))
    assert "Beweisgröße" not in _msgs(replace(a, chr=replace(a.chr, mst_cost=opt + barely, matching_cost=opt / 2 + barely)))
    assert "Beweisgröße" not in _msgs(replace(a, chr=replace(a.chr, mst_cost=opt, matching_cost=opt / 2 + barely)))


def test_sweep_quality_violation_thresholds(monkeypatch):
    real_dt, real_chr = A.double_tree_tour, A.christofides_tour

    def scaled(factor, which):
        def patched(dist):
            opt = A.held_karp(dist).cost
            base = real_dt(dist) if which == "dt" else real_chr(dist)
            return A.TourResult(base.tour, factor * opt, base.mst_edges, base.mst_cost, base.odd, base.matching, base.matching_cost, base.circuit)
        return patched
    seeds = (1, 2, 3)
    for which, bound in (("dt", 2.0), ("chr", 1.5)):
        name = "double_tree_tour" if which == "dt" else "christofides_tour"
        monkeypatch.setattr(ev.A, name, scaled(bound, which))
        assert ev.sweep_quality("uni", sizes=(5,), seeds=seeds)[0]["violations"] == 0                   # genau an der Garantie: erlaubt
        monkeypatch.setattr(ev.A, name, scaled(bound * (1 + 1e-6), which))
        assert ev.sweep_quality("uni", sizes=(5,), seeds=seeds)[0]["violations"] == 3                   # knapp darüber: gezählt
        monkeypatch.undo()


def test_remaining_validation_tolerances_scale_with_the_cost():
    a = _base()
    opt = a.opt.cost
    barely = 0.5 * ev.TOL * opt
    assert "Garantie 3/2" not in _msgs(replace(a, chr=replace(a.chr, cost=1.5 * opt + barely)))
    big = replace(a, chr=replace(a.chr, cost=a.chr.mst_cost + a.chr.matching_cost + 0.5 * ev.TOL * a.chr.cost))
    assert "länger als Gerüst plus Paarung" not in _msgs(big)
    off = replace(a, opt=replace(a.opt, cost=opt + barely), dist=a.dist)
    assert "Brute-Force-Probe" not in _msgs(off)
    assert "Brute-Force-Probe" in _msgs(replace(a, opt=replace(a.opt, cost=opt + 2 * ev.TOL * opt + 1e-3)))
