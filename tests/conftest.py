"""Gemeinsame Fixtures: Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Die Handrechnungen verwenden die Manhattan-Entfernung (ganzzahlig, erfüllt die Dreiecksungleichung): die Algorithmen nehmen jede Entfernungsmatrix.
Regeln für Gleichstände (im Kern und hier gleich): Prim startet bei Punkt 0 und wählt den Punkt mit kleinstem Schlüssel, bei Gleichstand den kleineren Index, und ersetzt den Vorgänger nur bei echt kleinerem Schlüssel;
Tiefensuche und Eulerkreis nehmen die Nachbarn in Einfügereihenfolge (Gerüstkanten zuerst, dann die Paarung)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def manhattan(points):
    return [[abs(a[0] - b[0]) + abs(a[1] - b[1]) for b in points] for a in points]


@pytest.fixture
def star():
    """Punkte c(0,0), a(3,0), b(0,4), d(-5,1) mit den Nummern 0, 1, 2, 3 (Manhattan).

    Entfernungen: 0-1 = 3, 0-2 = 4, 0-3 = 6, 1-2 = 7, 1-3 = 9, 2-3 = 8.
    Gerüst (Prim ab 0): Schlüssel 1: 3, 2: 4, 3: 6; nacheinander Kanten (0,1), (0,2), (0,3), Gewicht 13. Grade: Punkt 0 hat 3, die anderen 1: alle vier ungerade.
    Paarungen: (0,1)+(2,3) = 3 + 8 = 11, (0,2)+(1,3) = 4 + 9 = 13, (0,3)+(1,2) = 6 + 7 = 13: die billigste ist (0,1), (2,3) mit 11.
    Vielfachgraph (Gerüst, dann Paarung): (0,1), (0,2), (0,3), (0,1), (2,3); alle Grade gerade (Punkt 0: 4, die anderen 2).
    Eulerkreis (Hierholzer ab 0, erste unbenutzte Kante): 0, 1, 0, 2, 3, 0 (Handrechnung im Test `test_euler_circuit_hand_values`). Abkürzung (erste Besuche): 0, 1, 2, 3.
    Christofides: Gerüst 13 + Paarung 11 = 24; Rundweg 0, 1, 2, 3 mit 3 + 7 + 8 + 6 = 24.
    Verdopplung: Tiefensuche ab 0, Kinder aufsteigend: 0, 1, 2, 3, Kosten 24. Optimum: 0, 1, 2, 3 (24) und 0, 1, 3, 2 (3 + 9 + 8 + 4 = 24), 0, 2, 1, 3 hat 4 + 7 + 9 + 6 = 26: Optimum 24."""
    return manhattan([(0, 0), (3, 0), (0, 4), (-5, 1)])


@pytest.fixture
def path4():
    """Punkte (0,0), (3,0), (3,4), (0,5) (Manhattan): Entfernungen 0-1 = 3, 1-2 = 4, 2-3 = 4, 0-3 = 5, 0-2 = 7, 1-3 = 8.

    Gerüst (Prim ab 0): Schlüssel 1: 3, 2: 7, 3: 5; Punkt 1 (3), dann 2 über 1 (4, ersetzt 7) und 3 über 2 (4, ersetzt 5): Kanten (0,1), (1,2), (2,3), Gewicht 11. Ungerade Knoten 0 und 3, Paarung (0,3) = 5.
    Rundweg 0, 1, 2, 3 mit 3 + 4 + 4 + 5 = 16; die anderen beiden Rundwege kosten 22 und 24: Optimum 16."""
    return manhattan([(0, 0), (3, 0), (3, 4), (0, 5)])


@pytest.fixture
def line5():
    """Fünf Punkte auf einer Geraden bei x = 0, 1, 3, 6, 10 (Manhattan): Gerüst = Weg (1 + 2 + 3 + 4 = 10), ungerade Knoten die beiden Enden (Paarung 10), Rundweg 20 = 2 mal die Spannweite = Optimum."""
    return manhattan([(0, 0), (1, 0), (3, 0), (6, 0), (10, 0)])


@pytest.fixture
def four_cycle_graph():
    """Graph auf 4 Knoten mit den Kanten des Vierecks (0,1), (1,2), (2,3), (0,3): hat einen Hamiltonkreis. Mit M = 5 (> 1 · 4) kosten die Kanten 1, die Diagonalen 5: Optimum 4."""
    return 4, [(0, 1), (1, 2), (2, 3), (0, 3)]


@pytest.fixture
def path_graph():
    """Weg 0-1-2-3 auf 4 Knoten: kein Hamiltonkreis. Mit M = 5 ist das Optimum 3 + 5 = 8 (der Weg und eine Nichtkante), mit M = 9: 3 + 9 = 12."""
    return 4, [(0, 1), (1, 2), (2, 3)]
