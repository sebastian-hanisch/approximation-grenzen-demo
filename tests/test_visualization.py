"""Abbildungen: Reihen, Farben, gesperrte Achsen; der PDF-Bau mit Umlauten."""

import apx_algorithm as A
import apx_constants as C
import apx_evaluation as ev
import apx_visualization as V
from apx_pdf_export import build_pdf


def _locked(fig):
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_tour_map_draws_the_optimum_dashed_and_the_method_solid():
    a = ev.analyse(ev.Settings(n=7, seed=4))
    fig = V.build_tour_map(a.points, a.chr.tour, a.opt.tour, "Christofides")
    assert [t.name for t in fig.data] == ["Optimum", "Christofides", "Punkte"]
    assert fig.data[0].line.dash == "dash" and fig.data[0].line.color == C.COLOR_OPT and fig.data[1].line.color == C.COLOR_TOUR
    assert len(fig.data[2].x) == 7 and list(fig.data[2].text) == [str(i) for i in range(7)]
    assert sum(1 for v in fig.data[1].x if v is not None) == 2 * 7                       # eine Strecke je Kante des geschlossenen Rundwegs
    _locked(fig)


def test_christofides_map_marks_odd_nodes_tree_and_matching():
    a = ev.analyse(ev.Settings(n=8, seed=4))
    fig = V.build_christofides_map(a.points, a.chr)
    names = [t.name for t in fig.data]
    assert names[0] == "Gerüst" and "Paarung" in names and "ungerader Grad" in names
    odd = next(t for t in fig.data if t.name == "ungerader Grad")
    assert sorted(int(x) for x in odd.text) == sorted(a.chr.odd)
    tree = fig.data[0]
    assert sum(1 for v in tree.x if v is not None) == 2 * len(a.chr.mst_edges)
    _locked(fig)


def test_christofides_map_without_matching_or_odd_nodes():
    a = ev.analyse(ev.Settings(n=5, seed=1))
    fake = a.chr.__class__(a.chr.tour, a.chr.cost, a.chr.mst_edges, a.chr.mst_cost, [], (), 0.0, a.chr.circuit)
    names = [t.name for t in V.build_christofides_map(a.points, fake).data]
    assert "Paarung" not in names and "ungerader Grad" not in names and "gerader Grad" in names


def test_ratio_bars_mark_the_guarantees():
    fig = V.build_ratio_bars({"dt": 1.2, "chr": 1.05, "nn": 1.1})
    assert list(fig.data[0].y) == [1.2, 1.05, 1.1] and list(fig.data[0].x) == [C.METHODS[k] for k in C.METHODS]
    assert [s.y0 for s in fig.layout.shapes] == [2.0, 1.5]                                  # nur die zwei Verfahren mit Garantie
    _locked(fig)


def test_proof_bars_show_the_six_quantities():
    a = ev.analyse(ev.Settings(n=7, seed=4))
    fig = V.build_proof_bars(a)
    assert list(fig.data[0].x)[:2] == ["Gerüst", "Paarung"] and len(fig.data[0].y) == 6
    assert fig.data[0].y[3] == a.opt.cost and fig.data[0].y[2] == a.opt.cost / 2 and fig.data[0].y[5] == a.chr.cost
    _locked(fig)


def test_quality_chart_has_six_series_and_two_guarantee_lines():
    rows = ev.sweep_quality("uni", sizes=(6, 7), seeds=(1, 2, 3))
    fig = V.build_quality(rows)
    assert len(fig.data) == 6 and len(fig.layout.shapes) == 2
    assert [s.y0 for s in fig.layout.shapes] == [2.0, 1.5]
    assert list(fig.data[0].x) == [6, 7] and list(fig.data[0].y) == [rows[0]["median"]["dt"], rows[1]["median"]["dt"]]
    _locked(fig)


def test_m_chart_log_axes_and_four_series():
    rows = ev.sweep_m(n=7, p=150, ms=(1, 5, 100), seeds=(1, 2))
    fig = V.build_m(rows)
    assert [t.name for t in fig.data] == list(ev.ALL_METHODS.values()) and fig.layout.xaxis.type == "log" and fig.layout.yaxis.type == "log"
    _locked(fig)


def test_graph_chart_separates_cycle_edges_and_decoys():
    inst = A.planted_instance(7, 300, 10, 2)
    edges = A.graph_edges(inst.dist)
    fig = V.build_graph(7, edges, inst.cycle)
    names = [t.name for t in fig.data]
    assert names == ["Köder", "Kante des eingepflanzten Kreises", "Knoten"]
    assert sum(1 for v in fig.data[1].x if v is not None) == 2 * 7                          # alle sieben Kanten des Kreises
    assert sum(1 for v in fig.data[0].x if v is not None) == 2 * (len(edges) - 7)
    plain = V.build_graph(7, A.graph_edges(A.planted_instance(7, 0, 10, 2).dist), inst.cycle if False else A.planted_instance(7, 0, 10, 2).cycle)
    assert [t.name for t in plain.data] == ["Kante des eingepflanzten Kreises", "Knoten"]
    _locked(fig)


def test_pdf_builds_with_umlauts():
    for settings in (ev.Settings(), ev.Settings(n=C.N_MIN, family="lin"), ev.Settings(n=C.N_MAX, family="clu")):
        pdf = build_pdf(ev.analyse(settings))
        assert pdf.startswith(b"%PDF") and len(pdf) > 1000


def test_color_constants_are_distinct():
    assert len(set(C.COLOR_SERIES)) == len(C.COLOR_SERIES)
