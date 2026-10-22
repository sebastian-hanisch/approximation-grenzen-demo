"""Szenario: Punkte in der Ebene für den Rundweg (Auslieferstellen), mit eigenem Zufallsgenerator (SplitMix64, wörtliche Kopie in apx_rng.py), damit alle Instanzen auf jeder Plattform gleich sind.

Drei Familien: „gleichverteilt“ (x und y in 0 bis 1000), „gehäuft“ (drei Gruppen, Streuung ±50 um den Mittelpunkt; einzelne Punkte können knapp außerhalb von 0 bis 1000 liegen) und „schmaler Streifen“
(x in 0 bis 1000, y in 0 bis 20: fast eine Gerade). Entfernung ist die euklidische."""

import apx_constants as C
from apx_rng import SplitMix64


def make_points(n: int, seed: int, family: str) -> tuple:
    """Deterministisch aus (n, Zufalls-Seed, Familie): gleiche Eingabe, gleiche Punkte."""
    if family not in C.FAMILIES:
        raise ValueError(f"unbekannte Familie: {family}")
    rng = SplitMix64(seed)
    top = C.COORD_MAX + 1
    if family == "uni":
        return tuple((rng.below(top), rng.below(top)) for _ in range(n))
    if family == "lin":
        return tuple((rng.below(top), rng.below(C.STRIP_HEIGHT + 1)) for _ in range(n))
    centers = [(rng.below(top), rng.below(top)) for _ in range(C.CLUSTER_COUNT)]
    points = []
    for _ in range(n):
        cx, cy = centers[rng.below(C.CLUSTER_COUNT)]
        points.append((cx + rng.below(2 * C.CLUSTER_RADIUS + 1) - C.CLUSTER_RADIUS, cy + rng.below(2 * C.CLUSTER_RADIUS + 1) - C.CLUSTER_RADIUS))
    return tuple(points)
