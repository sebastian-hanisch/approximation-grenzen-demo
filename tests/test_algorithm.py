"""Einheiten des Kerns an Mini-Instanzen von Hand (DEMO-PLAYBOOK §1b): jede Einheit ist eine Funktion, jede hat einen Handwert."""

import math

import pytest

import apx_algorithm as A
from conftest import manhattan


# --- Entfernungen und Prüfer ---------------------------------------------------------------------------------------------------------------


def test_euclid_matrix_hand_values():
    d = A.euclid_matrix([(0, 0), (3, 4), (3, 0)])
    assert d[0][1] == d[1][0] == 5.0 and d[0][2] == 3.0 and d[1][2] == 4.0 and d[0][0] == 0.0


def test_tour_cost_and_is_tour(path4):
    assert A.tour_cost(path4, [0, 1, 2, 3]) == 16
    assert A.tour_cost(path4, [0, 1, 3, 2]) == 3 + 8 + 4 + 7              # Rückkante gehört dazu
    assert A.is_tour(4, [0, 2, 1, 3]) and A.is_tour(4, (3, 2, 1, 0))
    assert not A.is_tour(4, [0, 1, 2]) and not A.is_tour(4, [0, 1, 1, 2]) and not A.is_tour(4, [0, 1, 2, 4])


# --- Gerüst, ungerade Knoten ------------------------------------------------------------------------------------------------------------


def test_prim_hand_values(star, path4, line5):
    assert A.prim_mst(star) == [(0, 1), (0, 2), (0, 3)]
    assert A.prim_mst(path4) == [(0, 1), (1, 2), (2, 3)]
    assert A.prim_mst(line5) == [(0, 1), (1, 2), (2, 3), (3, 4)]


def test_prim_breaks_ties_by_smaller_index_and_keeps_the_first_parent():
    # alle Entfernungen gleich: Gerüst = Stern um 0 (Schlüssel gleich, kleinster Index zuerst, Vorgänger bleibt 0)
    d = [[0 if i == j else 1 for j in range(4)] for i in range(4)]
    assert A.prim_mst(d) == [(0, 1), (0, 2), (0, 3)]


def test_mst_weight(star):
    assert A.edges_cost(star, A.prim_mst(star)) == 13


def test_odd_nodes_hand_values(star, path4):
    assert A.odd_nodes(4, A.prim_mst(star)) == [0, 1, 2, 3]
    assert A.odd_nodes(4, A.prim_mst(path4)) == [0, 3]
    assert A.odd_nodes(3, [(0, 1), (0, 2)]) == [1, 2]


# --- Paarung -----------------------------------------------------------------------------------------------------------------------------


def test_min_matching_hand_values(star):
    r = A.min_matching(star, [0, 1, 2, 3])
    assert r.cost == 11 and r.pairs == ((0, 1), (2, 3))


def test_min_matching_states_by_hand():
    """Zustände der Bitmasken-DP (ohne die volle Maske): k = 0: 0; k = 2: 1; k = 4: 1 + 3 = 4; k = 6: 1 + 5 + 6 = 12 (die Abzählung steht im Kommentar zu `min_matching`)."""
    d = [[abs(i - j) for j in range(6)] for i in range(6)]
    assert A.min_matching(d, []).states == 0
    assert A.min_matching(d, [0, 1]).states == 1
    assert A.min_matching(d, [0, 1, 2, 3]).states == 4
    assert A.min_matching(d, [0, 1, 2, 3, 4, 5]).states == 12


def test_min_matching_on_a_line_pairs_neighbours():
    d = [[abs(i - j) for j in range(6)] for i in range(6)]
    r = A.min_matching(d, [0, 1, 2, 3, 4, 5])
    assert r.cost == 3 and r.pairs == ((0, 1), (2, 3), (4, 5))


def test_min_matching_rejects_an_odd_number_of_nodes(star):
    with pytest.raises(ValueError):
        A.min_matching(star, [0, 1, 2])


# --- Eulerkreis, Abkürzung -------------------------------------------------------------------------------------------------------------


def test_euler_circuit_hand_values():
    """Handrechnung (Hierholzer ab 0, erste unbenutzte Kante, Kantenliste (0,1), (0,2), (0,3), (0,1), (2,3)): Stapel 0, 1, 0, 2, 3, 0; dann nacheinander abgeben: 0, 3, 2, 0, 1, 0; umgedreht 0, 1, 0, 2, 3, 0."""
    assert A.euler_circuit(4, [(0, 1), (0, 2), (0, 3), (0, 1), (2, 3)]) == [0, 1, 0, 2, 3, 0]


def test_euler_circuit_of_a_triangle_and_rejects_non_eulerian_input():
    assert A.euler_circuit(3, [(0, 1), (1, 2), (0, 2)]) == [0, 1, 2, 0]
    with pytest.raises(ValueError):
        A.euler_circuit(3, [(0, 1), (1, 2)])                 # Grade ungerade
    with pytest.raises(ValueError):
        A.euler_circuit(4, [(0, 1), (0, 1), (2, 3), (2, 3)])  # nicht zusammenhängend


def test_shortcut_hand_values():
    assert A.shortcut([0, 1, 0, 2, 3, 0]) == [0, 1, 2, 3]
    assert A.shortcut([0, 1, 2, 0]) == [0, 1, 2]
    assert A.shortcut([0]) == [0]


# --- die beiden Verfahren ------------------------------------------------------------------------------------------------------------------


def test_christofides_hand_values(star):
    r = A.christofides_tour(star)
    assert r.tour == [0, 1, 2, 3] and r.cost == 24
    assert r.mst_edges == [(0, 1), (0, 2), (0, 3)] and r.mst_cost == 13
    assert r.odd == [0, 1, 2, 3] and r.matching == ((0, 1), (2, 3)) and r.matching_cost == 11
    assert r.circuit == [0, 1, 0, 2, 3, 0]


def test_double_tree_hand_values(star, path4):
    r = A.double_tree_tour(star)
    assert r.tour == [0, 1, 2, 3] and r.cost == 24 and r.mst_cost == 13 and r.matching == () and r.matching_cost == 0
    assert A.double_tree_tour(path4).tour == [0, 1, 2, 3]


def test_double_tree_circuit_is_the_doubled_tree_walk(star, path4):
    """Euler-Rundgang des verdoppelten Gerüsts: jede Gerüstkante zweimal, Länge 2 · (n − 1) + 1."""
    r = A.double_tree_tour(star)
    assert r.circuit == [0, 1, 0, 2, 0, 3, 0]                 # Handrechnung: Hierholzer auf (0,1), (0,2), (0,3) und noch einmal dieselben
    assert len(r.circuit) == 2 * 3 + 1 and r.circuit[0] == r.circuit[-1] == 0
    assert A.double_tree_tour(path4).circuit == [0, 1, 2, 3, 2, 1, 0]


def test_christofides_on_a_path_matches_the_two_ends(path4):
    r = A.christofides_tour(path4)
    assert r.odd == [0, 3] and r.matching == ((0, 3),) and r.matching_cost == 5 and r.cost == 16 == r.mst_cost + r.matching_cost


def test_line_instance_is_solved_optimally_by_both(line5):
    assert A.double_tree_tour(line5).cost == 20 and A.christofides_tour(line5).cost == 20


def test_tiny_instances():
    d3 = manhattan([(0, 0), (1, 0), (0, 1)])
    for f in (A.double_tree_tour, A.christofides_tour):
        r = f(d3)
        assert A.is_tour(3, r.tour) and r.cost == 4
    d1 = [[0.0]]
    assert A.double_tree_tour(d1).tour == [0] and A.christofides_tour(d1).tour == [0]


def test_identical_points_give_zero_cost():
    d = [[0.0] * 4 for _ in range(4)]
    for f in (A.double_tree_tour, A.christofides_tour):
        assert f(d).cost == 0 and A.is_tour(4, f(d).tour)


# --- Maßstab und einfache Heuristiken ------------------------------------------------------------------------------------------------------


def test_held_karp_hand_values(star, path4, line5):
    r = A.held_karp(star)
    assert r.cost == 24 and A.is_tour(4, r.tour) and A.tour_cost(star, r.tour) == 24 and r.cells == 3 * 2 ** 3
    assert A.held_karp(path4).cost == 16 and A.held_karp(line5).cost == 20 and A.held_karp(line5).cells == 4 * 2 ** 4


def test_held_karp_tiny():
    assert A.held_karp([[0.0]]).cost == 0 and A.held_karp([[0.0]]).tour == [0]
    d2 = [[0, 5], [5, 0]]
    assert A.held_karp(d2).cost == 10 and A.is_tour(2, A.held_karp(d2).tour)


def test_nearest_neighbour_hand_values(star, path4):
    assert A.nearest_neighbour(star) == [0, 1, 2, 3]          # von 0 aus: 1 (3), dann von 1: 2 (7), dann 3
    assert A.nearest_neighbour(path4) == [0, 1, 2, 3]
    assert A.nearest_neighbour(path4, start=3) == [3, 2, 1, 0]


def test_greedy_edge_hand_values(path4):
    """Kanten aufsteigend: (0,1) 3, (1,2) 4, (2,3) 4 [Gleichstand: kleinere Kante zuerst]: alle drei passen, Weg 0-1-2-3; Rückkante (3,0)."""
    t = A.greedy_edge(path4)
    assert t == [0, 1, 2, 3] and A.tour_cost(path4, t) == 16            # der Weg beginnt am kleineren Ende


def test_greedy_edge_skips_edges_that_close_a_cycle_early():
    d = manhattan([(0, 0), (1, 0), (2, 0), (0, 1)])
    t = A.greedy_edge(d)
    assert A.is_tour(4, t)


# --- Familie ohne Dreiecksungleichung --------------------------------------------------------------------------------------------------------


def test_hamiltonian_matrix_hand_values(four_cycle_graph, path_graph):
    n, edges = four_cycle_graph
    d = A.graph_cost_matrix(n, edges, 5)
    assert d[0][1] == 1 and d[0][3] == 1 and d[0][2] == 5 and d[1][3] == 5 and d[0][0] == 0
    assert A.held_karp(d).cost == 4
    n, edges = path_graph
    assert A.held_karp(A.graph_cost_matrix(n, edges, 5)).cost == 8
    assert A.held_karp(A.graph_cost_matrix(n, edges, 9)).cost == 12


def test_has_hamiltonian_cycle_hand_values(four_cycle_graph, path_graph):
    assert A.has_hamiltonian_cycle(*four_cycle_graph) and not A.has_hamiltonian_cycle(*path_graph)
    assert A.has_hamiltonian_cycle(3, [(0, 1), (1, 2), (0, 2)])                   # Dreieck
    assert not A.has_hamiltonian_cycle(4, [(0, 1), (1, 2), (2, 0), (0, 3)])         # Dreieck mit Anhängsel
    assert not A.has_hamiltonian_cycle(4, [])


def test_planted_instance_has_the_hidden_cycle_and_optimum_n():
    inst = A.planted_instance(8, 150, 10, 3)
    assert sorted(inst.cycle) == list(range(8)) and A.is_tour(8, inst.cycle)
    assert A.tour_cost(inst.dist, inst.cycle) == 8                                  # der eingepflanzte Kreis kostet n
    assert all(inst.dist[a][b] in (1.0, 10.0) for a in range(8) for b in range(8) if a != b)
    assert A.planted_instance(8, 150, 10, 3).dist == inst.dist != A.planted_instance(8, 150, 10, 4).dist


def test_planted_instance_without_decoys_is_a_plain_cycle():
    inst = A.planted_instance(6, 0, 7, 1)
    assert sum(1 for a in range(6) for b in range(a + 1, 6) if inst.dist[a][b] == 1.0) == 6
    full = A.planted_instance(6, 1000, 7, 1)
    assert all(full.dist[a][b] == 1.0 for a in range(6) for b in range(6) if a != b)


def test_triangle_violations_counts_ordered_triples():
    metric = manhattan([(0, 0), (1, 0), (2, 0)])
    assert A.triangle_violations(metric) == 0
    bad = [[0, 1, 5], [1, 0, 1], [5, 1, 0]]               # 0-2 = 5 > 0-1 + 1-2 = 2
    assert A.triangle_violations(bad) == 2                    # (0, 1, 2) und (2, 1, 0)


def test_graph_edges_and_a_path_has_no_hamiltonian_cycle():
    inst = A.planted_instance(6, 0, 7, 2)
    es = A.graph_edges(inst.dist)
    assert len(es) == 6 and all(a < b for a, b in es)
    assert A.has_hamiltonian_cycle(6, es) and not A.has_hamiltonian_cycle(6, es[1:])


# --- Lücken aus der Mutationsprüfung ------------------------------------------------------------------------------------------------------


def test_two_points_make_a_tour_for_both_methods():
    d2 = [[0, 5], [5, 0]]
    for f in (A.double_tree_tour, A.christofides_tour):
        r = f(d2)
        assert A.is_tour(2, r.tour) and r.cost == 10


def test_a_cycle_needs_three_nodes():
    assert not A.has_hamiltonian_cycle(2, [(0, 1)]) and not A.has_hamiltonian_cycle(1, []) and not A.has_hamiltonian_cycle(0, [])


def test_greedy_edge_with_fewer_than_three_points():
    assert A.greedy_edge([[0.0]]) == [0] and A.greedy_edge([[0, 5], [5, 0]]) == [0, 1] and A.greedy_edge([]) == []
