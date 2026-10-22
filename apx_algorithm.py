"""Kern: Gerüst, Paarung, Eulerkreis, Abkürzung, die zwei Verfahren mit Garantie (MST-Verdopplung, Christofides), nächster Nachbar, Greedy-Kanten, der exakte Maßstab (Held–Karp) und die Familie
ohne Dreiecksungleichung (Hamiltonkreis-Instanzen).

Jede Einheit ist eine Funktion (DEMO-PLAYBOOK §1b); `double_tree_tour` und `christofides_tour` setzen nur diese Bausteine zusammen. Eine Entfernungsmatrix ist eine Liste von Listen (symmetrisch, Diagonale 0);
metrisch ist sie nur, wenn die Dreiecksungleichung gilt (`triangle_violations`). Gezählt werden Zellen und Zustände, nie Sekunden.

Regeln für Gleichstände (festgelegt und getestet): Prim startet bei Punkt 0, wählt den Punkt mit kleinstem Schlüssel (bei Gleichstand den kleineren Index) und ersetzt den Vorgänger nur bei echt kleinerem
Schlüssel; die Paarung nimmt bei Gleichstand die zuerst gefundene (der kleinere Partner des kleinsten ungepaarten Knotens zuerst); der Eulerkreis nimmt die Kanten in Einfügereihenfolge (Gerüstkanten zuerst)."""

import math
from dataclasses import dataclass

from apx_rng import SplitMix64

_INF = float("inf")
_EPS = 1e-9


@dataclass(frozen=True)
class MatchResult:
    cost: float
    pairs: tuple                       # Paare (a, b) mit a < b, nach dem kleineren Knoten sortiert
    states: int                        # Zustände der Bitmasken-DP (ohne die volle Maske)


@dataclass(frozen=True)
class TourResult:
    tour: list                         # Rundweg (Reihenfolge der Punkte, Rückkante gehört dazu)
    cost: float
    mst_edges: list
    mst_cost: float
    odd: list                          # Knoten mit ungeradem Grad im Gerüst (leer bei der Verdopplung)
    matching: tuple                    # Paare der Paarung (leer bei der Verdopplung)
    matching_cost: float
    circuit: list                      # Eulerkreis des Vielfachgraphen (vor der Abkürzung)


@dataclass(frozen=True)
class HkResult:
    cost: float
    tour: list
    cells: int                         # Zellen der Tabelle (Teilmenge ohne Punkt 0, letzter Punkt): (n − 1) · 2^(n − 1)


@dataclass(frozen=True)
class PlantedInstance:
    dist: list
    cycle: list                        # der eingepflanzte Hamiltonkreis (Reihenfolge der Knoten)
    n: int
    p: int                             # Zusatzkanten in Promille
    m: int                             # Kosten der Nichtkanten


# --- Entfernungen und Prüfer ---------------------------------------------------------------------------------------------------------------


def euclid_matrix(points) -> list:
    n = len(points)
    return [[math.hypot(points[i][0] - points[j][0], points[i][1] - points[j][1]) for j in range(n)] for i in range(n)]


def tour_cost(dist, tour) -> float:
    return sum(dist[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def edges_cost(dist, edges) -> float:
    return sum(dist[a][b] for a, b in edges)


def is_tour(n: int, tour) -> bool:
    """Jeder Punkt genau einmal (unabhängiger Prüfer, nicht Teil der Verfahren)."""
    tour = list(tour)
    return len(tour) == n and sorted(tour) == list(range(n))


def triangle_violations(dist) -> int:
    """Zahl der geordneten Tripel (a, b, c) mit d(a, c) > d(a, b) + d(b, c): 0 heißt metrisch."""
    n = len(dist)
    return sum(1 for a in range(n) for b in range(n) for c in range(n)
               if len({a, b, c}) == 3 and dist[a][c] > dist[a][b] + dist[b][c] + _EPS)


# --- Gerüst, ungerade Knoten, Paarung ------------------------------------------------------------------------------------------------------


def prim_mst(dist) -> list:
    """Kanten (Vorgänger, Punkt) eines billigsten Gerüsts nach Prim ab Punkt 0, in der Reihenfolge, in der die Punkte aufgenommen werden."""
    n = len(dist)
    done = [False] * n
    key = [_INF] * n
    parent = [-1] * n
    key[0] = 0
    edges = []
    for _ in range(n):
        u = min((v for v in range(n) if not done[v]), key=lambda v: (key[v], v))
        done[u] = True
        if parent[u] >= 0:
            edges.append((parent[u], u))
        for v in range(n):
            if not done[v] and dist[u][v] < key[v]:
                key[v] = dist[u][v]
                parent[v] = u
    return edges


def odd_nodes(n: int, edges) -> list:
    degree = [0] * n
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
    return [v for v in range(n) if degree[v] % 2]


def min_matching(dist, nodes) -> MatchResult:
    """Billigste perfekte Paarung der Knoten `nodes` per Bitmasken-DP: der kleinste ungepaarte Knoten wird mit jedem anderen ungepaarten gepaart.

    Zustände (Teilmengen, die auftreten, ohne die volle): k = 0: 0, k = 2: 1, k = 4: 1 + 3 = 4, k = 6: 1 + 5 + 6 = 12 (Maske der Stufe 4: {0, a, b, c}, 6 verschiedene)."""
    nodes = list(nodes)
    k = len(nodes)
    if k % 2:
        raise ValueError("Eine perfekte Paarung braucht eine gerade Zahl von Knoten")
    full = (1 << k) - 1
    memo: dict = {}

    def rec(mask):
        if mask == full:
            return 0.0, ()
        if mask in memo:
            return memo[mask]
        i = 0
        while mask >> i & 1:
            i += 1
        best = (_INF, ())
        for j in range(i + 1, k):
            if not mask >> j & 1:
                rest_cost, rest = rec(mask | 1 << i | 1 << j)
                cost = rest_cost + dist[nodes[i]][nodes[j]]
                if cost < best[0]:
                    pair = (min(nodes[i], nodes[j]), max(nodes[i], nodes[j]))
                    best = (cost, (pair,) + rest)
        memo[mask] = best
        return best

    cost, pairs = rec(0)
    return MatchResult(cost if k else 0.0, pairs, len(memo))


# --- Eulerkreis, Abkürzung, die beiden Verfahren -----------------------------------------------------------------------------------------


def euler_circuit(n: int, edges) -> list:
    """Hierholzer ab Knoten 0 auf dem Vielfachgraphen `edges` (Kanten in Einfügereihenfolge, erste unbenutzte zuerst); jede Kante genau einmal.

    Handrechnung für (0,1), (0,2), (0,3), (0,1), (2,3): Stapel 0, 1, 0, 2, 3, 0, dann abgeben 0, 3, 2, 0, 1, 0, umgedreht 0, 1, 0, 2, 3, 0."""
    edges = list(edges)
    if any(d % 2 for d in _degrees(n, edges)):
        raise ValueError("Ein Eulerkreis braucht lauter gerade Grade")
    adj = [[] for _ in range(n)]
    for idx, (a, b) in enumerate(edges):
        adj[a].append((b, idx))
        adj[b].append((a, idx))
    used = [False] * len(edges)
    ptr = [0] * n
    stack, circuit = [0], []
    while stack:
        u = stack[-1]
        while ptr[u] < len(adj[u]) and used[adj[u][ptr[u]][1]]:
            ptr[u] += 1
        if ptr[u] == len(adj[u]):
            circuit.append(stack.pop())
        else:
            v, idx = adj[u][ptr[u]]
            used[idx] = True
            stack.append(v)
    if not all(used):
        raise ValueError("Der Graph ist nicht zusammenhängend: kein Eulerkreis")
    return circuit[::-1]


def _degrees(n, edges):
    degree = [0] * n
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
    return degree


def shortcut(circuit) -> list:
    """Abkürzung: jeder Punkt nur beim ersten Besuch; der Rundweg kehrt von allein zum Start zurück."""
    seen, tour = set(), []
    for v in circuit:
        if v not in seen:
            seen.add(v)
            tour.append(v)
    return tour


def double_tree_tour(dist) -> TourResult:
    """MST-Verdopplung: Gerüst, jede Kante doppelt, Eulerkreis, Abkürzung. Höchstens das Doppelte des Optimums (metrisch)."""
    n = len(dist)
    edges = prim_mst(dist)
    circuit = euler_circuit(n, edges + edges) if n > 1 else [0]
    tour = shortcut(circuit)
    return TourResult(tour, tour_cost(dist, tour), edges, edges_cost(dist, edges), [], (), 0.0, circuit)


def christofides_tour(dist) -> TourResult:
    """Christofides: Gerüst, billigste Paarung der Knoten mit ungeradem Grad, Eulerkreis des Vielfachgraphen, Abkürzung. Höchstens das Anderthalbfache des Optimums (metrisch)."""
    n = len(dist)
    edges = prim_mst(dist)
    odd = odd_nodes(n, edges)
    match = min_matching(dist, odd)
    circuit = euler_circuit(n, edges + list(match.pairs)) if n > 1 else [0]
    tour = shortcut(circuit)
    return TourResult(tour, tour_cost(dist, tour), edges, edges_cost(dist, edges), odd, match.pairs, match.cost, circuit)


# --- Maßstab und einfache Heuristiken --------------------------------------------------------------------------------------------------------


def held_karp(dist) -> HkResult:
    """Exaktes Optimum per Tabelle über (Teilmenge der Punkte 1 bis n − 1, letzter Punkt); Zellen (n − 1) · 2^(n − 1)."""
    n = len(dist)
    if n == 1:
        return HkResult(0.0, [0], 0)
    m = n - 1
    size = 1 << m
    dp = [[_INF] * m for _ in range(size)]
    parent = [[-1] * m for _ in range(size)]
    for j in range(m):
        dp[1 << j][j] = dist[0][j + 1]
    for mask in range(1, size):
        row = dp[mask]
        for j in range(m):
            cur = row[j]
            if cur == _INF:
                continue
            dj = dist[j + 1]
            for k in range(m):
                if mask >> k & 1:
                    continue
                nxt = dp[mask | 1 << k]
                cost = cur + dj[k + 1]
                if cost < nxt[k]:
                    nxt[k] = cost
                    parent[mask | 1 << k][k] = j
    full = size - 1
    last = min(range(m), key=lambda j: (dp[full][j] + dist[j + 1][0], j))
    best = dp[full][last] + dist[last + 1][0]
    order, mask, j = [], full, last
    while j >= 0:
        order.append(j + 1)
        prev = parent[mask][j]
        mask ^= 1 << j
        j = prev
    return HkResult(best, [0] + order[::-1], m * size)


def nearest_neighbour(dist, start: int = 0) -> list:
    n = len(dist)
    seen = [False] * n
    tour = [start]
    seen[start] = True
    for _ in range(n - 1):
        u = tour[-1]
        v = min((w for w in range(n) if not seen[w]), key=lambda w: (dist[u][w], w))
        seen[v] = True
        tour.append(v)
    return tour


def greedy_edge(dist) -> list:
    """Greedy-Kanten: die billigsten Kanten zuerst (Gleichstand: kleinere Kante), solange kein Punkt Grad 3 bekommt und sich kein vorzeitiger Kreis schließt; die Rückkante schließt den Weg."""
    n = len(dist)
    if n < 3:
        return list(range(n))
    degree = [0] * n
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    adj = [[] for _ in range(n)]
    for _, a, b in sorted((dist[a][b], a, b) for a in range(n) for b in range(a + 1, n)):
        if degree[a] < 2 and degree[b] < 2 and find(a) != find(b):
            adj[a].append(b)
            adj[b].append(a)
            degree[a] += 1
            degree[b] += 1
            parent[find(a)] = find(b)
    start = min(v for v in range(n) if degree[v] < 2)
    tour, prev, cur = [start], -1, start
    while len(tour) < n:
        nxt = next(w for w in adj[cur] if w != prev)
        tour.append(nxt)
        prev, cur = cur, nxt
    return tour


# --- Familie ohne Dreiecksungleichung ----------------------------------------------------------------------------------------------------------


def graph_cost_matrix(n: int, edges, m: int) -> list:
    """Kosten 1 auf den Kanten des Graphen, m auf allen anderen Paaren (Reduktion Hamiltonkreis → Handlungsreisender)."""
    es = {(min(a, b), max(a, b)) for a, b in edges}
    return [[0.0 if a == b else (1.0 if (min(a, b), max(a, b)) in es else float(m)) for b in range(n)] for a in range(n)]


def graph_edges(dist) -> list:
    """Kanten (a < b) einer Kostenmatrix aus `graph_cost_matrix`: alle Paare mit Kosten 1."""
    n = len(dist)
    return [(a, b) for a in range(n) for b in range(a + 1, n) if dist[a][b] == 1.0]


def has_hamiltonian_cycle(n: int, edges) -> bool:
    """Brute Force mit Rücksprung (für kleine n): gibt es einen Rundweg, der jeden Knoten genau einmal besucht und nur Kanten benutzt? Ein Kreis braucht mindestens drei Knoten."""
    if n < 3:
        return False
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    visited = [False] * n
    visited[0] = True

    def extend(u, count):
        if count == n:
            return 0 in adj[u]
        for v in sorted(adj[u]):
            if not visited[v]:
                visited[v] = True
                if extend(v, count + 1):
                    return True
                visited[v] = False
        return False

    return extend(0, 1)


def planted_instance(n: int, p: int, m: int, seed: int) -> PlantedInstance:
    """Graph mit eingepflanztem Hamiltonkreis (verdeckte Reihenfolge), dazu jedes weitere Paar mit Wahrscheinlichkeit p / 1000 als Kante (Köder); Kosten 1 auf Kanten, m sonst: das Optimum ist n."""
    rng = SplitMix64(seed)
    order = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.below(i + 1)
        order[i], order[j] = order[j], order[i]
    edges = {(min(order[i], order[(i + 1) % n]), max(order[i], order[(i + 1) % n])) for i in range(n)}
    for a in range(n):
        for b in range(a + 1, n):
            if (a, b) not in edges and rng.below(1000) < p:
                edges.add((a, b))
    return PlantedInstance(graph_cost_matrix(n, edges, m), order, n, p, m)
