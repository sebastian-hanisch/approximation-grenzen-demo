"""Orakel-Tests: andere Rechenwege als die der Demo (ORACLE-PLAYBOOK, DEMO-PLAYBOOK §12).

- Exakter Maßstab (Held–Karp): Brute Force über alle Rundwege (euklidisch und nicht metrisch) und CP-SAT (`ortools`, importorskip).
- Paarung: alle Paarungen aufgezählt (bis 8 Knoten) und `networkx.min_weight_matching` (importorskip); Gerüst: Gewicht gegen `networkx.minimum_spanning_tree`.
- Eulerkreis: unabhängiger Prüfer (jede Kante des Vielfachgraphen genau einmal, aufeinanderfolgende Punkte sind Nachbarn).
- Die Garantien als harte Prüfung auf Instanzen aller drei Familien, dazu die Beweisgrößen (Gerüst <= OPT, Paarung <= OPT / 2, Rundweg <= Gerüst + Paarung).
- Die Reduktion Hamiltonkreis <=> Optimum <= rho * n gegen Brute Force auf allen Graphen mit 4 Knoten; die eingepflanzte Familie hat das Optimum n."""

import itertools
from collections import Counter

import pytest

import apx_algorithm as A
import apx_constants as C
import apx_evaluation as ev
from apx_rng import SplitMix64
from apx_scenario import make_points

TOL = 1e-9


def brute_force_tour(dist):
    n = len(dist)
    if n == 1:
        return 0.0
    return min(A.tour_cost(dist, (0,) + perm) for perm in itertools.permutations(range(1, n)))


def random_matrix(n, seed, high=20):
    """Zufällige symmetrische Matrix ohne Dreiecksungleichung."""
    rng = SplitMix64(seed)
    d = [[0] * n for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            d[a][b] = d[b][a] = 1 + rng.below(high)
    return d


def all_perfect_matchings(nodes):
    if not nodes:
        yield ()
        return
    first, rest = nodes[0], nodes[1:]
    for i, partner in enumerate(rest):
        for tail in all_perfect_matchings(rest[:i] + rest[i + 1:]):
            yield ((first, partner),) + tail


# --- Held–Karp ---------------------------------------------------------------------------------------------------------------------------


def test_held_karp_matches_brute_force_on_euclidean_and_non_metric_instances():
    count = 0
    for family in C.FAMILIES:
        for n in (1, 2, 3, 5, 7, 8):
            for seed in range(6):
                dist = A.euclid_matrix(make_points(n, 100 + seed, family))
                r = A.held_karp(dist)
                assert r.cost == pytest.approx(brute_force_tour(dist), abs=1e-6), (family, n, seed)
                assert A.is_tour(n, r.tour) and A.tour_cost(dist, r.tour) == pytest.approx(r.cost, abs=1e-6)
                count += 1
    for n in (3, 4, 6, 8):
        for seed in range(30):
            dist = random_matrix(n, 500 + seed)
            r = A.held_karp(dist)
            assert r.cost == brute_force_tour(dist) and A.tour_cost(dist, r.tour) == r.cost
            count += 1
    assert count >= 200


def test_held_karp_matches_cp_sat():
    cp = pytest.importorskip("ortools.sat.python.cp_model")
    for seed in range(12):
        n = 6 + seed % 5
        dist = random_matrix(n, 900 + seed, high=50)
        model = cp.CpModel()
        arcs, lit = [], {}
        for a in range(n):
            for b in range(n):
                if a != b:
                    lit[a, b] = model.NewBoolVar(f"x{a}_{b}")
                    arcs.append((a, b, lit[a, b]))
        model.AddCircuit(arcs)
        model.Minimize(sum(dist[a][b] * v for (a, b), v in lit.items()))
        solver = cp.CpSolver()
        assert solver.Solve(model) == cp.OPTIMAL
        assert A.held_karp(dist).cost == round(solver.ObjectiveValue()), seed


# --- Gerüst, Paarung, Eulerkreis ---------------------------------------------------------------------------------------------------------------


def test_prim_weight_matches_networkx():
    nx = pytest.importorskip("networkx")
    for family in C.FAMILIES:
        for seed in range(10):
            dist = A.euclid_matrix(make_points(9, 300 + seed, family))
            g = nx.Graph()
            g.add_weighted_edges_from((a, b, dist[a][b]) for a in range(9) for b in range(a + 1, 9))
            expected = sum(d["weight"] for _, _, d in nx.minimum_spanning_edges(g, data=True))
            edges = A.prim_mst(dist)
            assert len(edges) == 8 and A.edges_cost(dist, edges) == pytest.approx(expected, abs=1e-6)


def test_min_matching_matches_enumeration_and_networkx():
    count = 0
    for seed in range(60):
        rng = SplitMix64(1000 + seed)
        k = 2 * (1 + rng.below(4))
        dist = random_matrix(k, 2000 + seed)
        nodes = list(range(k))
        best = min(sum(dist[a][b] for a, b in m) for m in all_perfect_matchings(nodes))
        r = A.min_matching(dist, nodes)
        assert r.cost == best and sum(dist[a][b] for a, b in r.pairs) == r.cost
        assert sorted(v for pair in r.pairs for v in pair) == nodes
        count += 1
    assert count == 60
    nx = pytest.importorskip("networkx")
    for seed in range(15):
        dist = random_matrix(8, 3000 + seed)
        g = nx.Graph()
        g.add_weighted_edges_from((a, b, dist[a][b]) for a in range(8) for b in range(a + 1, 8))
        expected = sum(dist[a][b] for a, b in nx.min_weight_matching(g))
        assert A.min_matching(dist, list(range(8))).cost == expected


def test_min_matching_on_a_subset_of_nodes():
    dist = random_matrix(9, 77)
    nodes = [1, 3, 4, 8]
    best = min(sum(dist[a][b] for a, b in m) for m in all_perfect_matchings(nodes))
    assert A.min_matching(dist, nodes).cost == best


def test_euler_circuit_uses_every_edge_exactly_once():
    for family in C.FAMILIES:
        for seed in range(15):
            n = 7
            dist = A.euclid_matrix(make_points(n, 400 + seed, family))
            edges = A.prim_mst(dist)
            match = A.min_matching(dist, A.odd_nodes(n, edges)).pairs
            for multigraph in (edges + edges, edges + list(match)):
                circuit = A.euler_circuit(n, multigraph)
                steps = Counter(frozenset((circuit[i], circuit[i + 1])) if circuit[i] != circuit[i + 1] else frozenset((circuit[i],)) for i in range(len(circuit) - 1))
                wanted = Counter(frozenset((a, b)) for a, b in multigraph)
                assert steps == wanted and circuit[0] == circuit[-1] == 0, (family, seed)


# --- die Garantien als harte Prüfung -----------------------------------------------------------------------------------------------------------


def test_guarantees_and_proof_quantities_on_euclidean_instances():
    count = 0
    for family in C.FAMILIES:
        for n in (5, 6, 7, 8, 9, 10):
            for seed in range(20):
                dist = A.euclid_matrix(make_points(n, 7000 + 31 * n + seed, family))
                opt = A.held_karp(dist).cost
                dt, ch = A.double_tree_tour(dist), A.christofides_tour(dist)
                nn = A.tour_cost(dist, A.nearest_neighbour(dist))
                assert A.is_tour(n, dt.tour) and A.is_tour(n, ch.tour)
                assert opt - 1e-6 <= dt.cost <= 2 * opt + 1e-6, ("2", family, n, seed)
                assert opt - 1e-6 <= ch.cost <= 1.5 * opt + 1e-6, ("1.5", family, n, seed)
                assert dt.cost <= 2 * dt.mst_cost + 1e-6 and ch.cost <= ch.mst_cost + ch.matching_cost + 1e-6
                assert ch.mst_cost <= opt + 1e-6 and ch.matching_cost <= opt / 2 + 1e-6, ("Beweis", family, n, seed)
                assert nn >= opt - 1e-6
                assert A.is_tour(n, A.greedy_edge(dist))
                count += 1
    assert count == 360


def test_analysis_matches_brute_force_and_the_guarantees():
    for family in C.FAMILIES:
        for seed in range(8):
            a = ev.analyse(ev.Settings(n=7, seed=seed, family=family))
            assert a.opt.cost == pytest.approx(brute_force_tour(a.dist), abs=1e-6) and ev.validation_errors(a) == []
            assert a.ratio("dt") <= 2 + TOL and a.ratio("chr") <= 1.5 + TOL and a.ratio("nn") >= 1 - TOL


def test_sweep_quality_matches_independent_recomputation():
    rows = ev.sweep_quality("uni", sizes=(6, 7), seeds=(1, 2, 3, 4))
    for row in rows:
        ratios = []
        for seed in (1, 2, 3, 4):
            dist = A.euclid_matrix(make_points(row["n"], seed, "uni"))
            ratios.append(A.christofides_tour(dist).cost / brute_force_tour(dist))
        assert row["max"]["chr"] == pytest.approx(max(ratios)) and row["median"]["chr"] == pytest.approx(sorted(ratios)[1] / 2 + sorted(ratios)[2] / 2)
        assert row["violations"] == 0 and row["count"] == 4


def test_search_finds_valid_instances_within_the_guarantee():
    for method, bound in (("dt", 2.0), ("chr", 1.5)):
        res = ev.search_worst_case(method, n=6, seed=11, steps=60, restarts=2)
        assert 1.0 <= res.best <= bound + TOL and len(res.points) == 6 and len(res.restarts) == 2
        dist = A.euclid_matrix(res.points)
        tour = (A.double_tree_tour if method == "dt" else A.christofides_tour)(dist).tour
        assert A.tour_cost(dist, tour) / brute_force_tour(dist) == pytest.approx(res.best)


# --- Reduktion und eingepflanzte Familie -------------------------------------------------------------------------------------------------------


def brute_force_hamiltonian(n, edges):
    es = {frozenset(e) for e in edges}
    return any(all(frozenset((t[i], t[(i + 1) % n])) in es for i in range(n)) for t in ((0,) + p for p in itertools.permutations(range(1, n))))


def test_reduction_agrees_with_brute_force_on_all_graphs_with_four_nodes():
    n = 4
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [pr for i, pr in enumerate(pairs) if mask >> i & 1]
        has = brute_force_hamiltonian(n, edges)
        for rho in (1, 2, 3):
            opt = brute_force_tour(A.graph_cost_matrix(n, edges, rho * n + 1))
            assert (opt <= rho * n) == has == A.has_hamiltonian_cycle(n, edges), (mask, rho)


def test_reduction_summary_counts():
    res = ev.reduction_all(sizes=(4,), random_n=5, random_count=40, seed=3)
    assert res["graphs"] == 64 and res["with_cycle"] == 10 and res["mismatches"] == 0 and res["checks"] == (64 + 40) * 3


def test_planted_family_has_optimum_n_and_the_heuristics_never_beat_it():
    for seed in range(15):
        inst = A.planted_instance(9, 150, 10, seed)
        assert A.held_karp(inst.dist).cost == 9
        costs = ev.planted_costs(inst)
        assert all(c >= 9 - TOL for c in costs.values())
    rows = ev.sweep_m(n=8, p=150, ms=(1, 2, 10), seeds=(1, 2, 3, 4))
    assert rows[0]["median"] == {k: 1.0 for k in ev.ALL_METHODS} and rows[1]["violations"] == 0 and rows[2]["violations"] > 0
    assert rows[1]["worst"] <= 2 + TOL                                                  # M = 2: jeder Rundweg höchstens 2 · n
