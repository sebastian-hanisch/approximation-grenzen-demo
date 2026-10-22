"""Konstanten: Regler-Grenzen, Rechengrenzen, Messreihen-Parameter, Farben und Presets.

Rechengrenze am Regler-Maximum (DEMO-PLAYBOOK §1c): n = 14 Punkte; Held–Karp als Maßstab braucht (n − 1) · 2^(n − 1) = 106.496 Zellen (rund 0,2 Sekunden); die Paarung hat höchstens n ungerade Knoten
(bei n = 14 im Median 7), die Bitmasken-DP bleibt klein."""

N_MIN, N_MAX, DEFAULT_N = 5, 14, 10
SEED_MAX, DEFAULT_SEED = 999999, 35
FAMILIES = {"uni": "gleichverteilt", "clu": "gehäuft (drei Gruppen)", "lin": "schmaler Streifen"}
DEFAULT_FAMILY = "uni"
METHODS = {"dt": "MST-Verdopplung", "chr": "Christofides", "nn": "nächster Nachbar"}      # Verfahren der metrischen Hälfte
DEFAULT_METHOD = "chr"
GUARANTEE = {"dt": 2.0, "chr": 1.5}                    # bewiesene Faktoren (nur für Punkte im metrischen Raum)
RHO_OPTIONS = (1, 2, 3)                                # angenommener Approximationsfaktor ρ der Reduktion
DEFAULT_RHO = 2
M_OPTIONS = (1, 2, 3, 5, 10, 20, 50, 100, 1000)        # Kosten der Nichtkanten
DEFAULT_M = 10
P_OPTIONS = (0, 50, 150, 300, 500)                     # Zusatzkanten (Köder) in Promille aller Paare
DEFAULT_P = 150
TOLERANCE = 1e-9                                       # relative Toleranz beim Vergleich mit den Garantien (Gleitkomma-Entfernungen)
COORD_MAX = 1000                                       # Koordinaten ganzzahlig in 0 bis 1000
STRIP_HEIGHT = 20                                      # Familie „schmaler Streifen“: y in 0 bis 20
CLUSTER_COUNT, CLUSTER_RADIUS = 3, 50

# Messreihen (alle Instanzen aus dem eigenen Generator: auf jeder Plattform dieselben)
SWEEP_SEEDS = tuple(range(100000, 100040))   # 40 feste Instanzen je Zelle: nie ein einzelner Seed als Befund
SWEEP_SIZES = (6, 8, 10, 12, 14)
SEARCH_N = 8                                 # Garantie-Suche: Punkte
SEARCH_RESTARTS = 4
SEARCH_STEPS = 700
SEARCH_SEED = 7000
M_SWEEP_N = 12                               # Faktor über M: Knoten der eingepflanzten Instanzen
M_SWEEP_P = 150
M_SWEEP_SEEDS = tuple(range(500, 540))
REDUCTION_SIZES = (4, 5)                     # alle Graphen mit so vielen Knoten werden geprüft
REDUCTION_RANDOM_N = 6                       # zusätzlich Zufallsgraphen
REDUCTION_RANDOM_COUNT = 300
REDUCTION_RANDOM_SEED = 5

COLOR_TOUR = "#2F6B65"
COLOR_OPT = "#C0392B"
COLOR_TREE = "#4c78a8"
COLOR_MATCH = "#B8860B"
COLOR_POINT = "#444444"
COLOR_GUARANTEE = "#C0392B"
COLOR_SERIES = ("#2F6B65", "#4c78a8", "#B8860B", "#C0392B")

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "family": "uni", "method": "chr", "rho": DEFAULT_RHO, "m": DEFAULT_M, "p": DEFAULT_P},
    "Lehrbeispiel (6 Punkte)": {"n": 6, "seed": 2, "family": "uni", "method": "chr", "rho": 2, "m": 10, "p": DEFAULT_P},
    "Gehäufte Punkte": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "family": "clu", "method": "chr", "rho": DEFAULT_RHO, "m": DEFAULT_M, "p": DEFAULT_P},
    "Schmaler Streifen": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "family": "lin", "method": "dt", "rho": DEFAULT_RHO, "m": DEFAULT_M, "p": DEFAULT_P},
    "Größte Instanz (14 Punkte)": {"n": N_MAX, "seed": DEFAULT_SEED, "family": "uni", "method": "dt", "rho": DEFAULT_RHO, "m": DEFAULT_M, "p": DEFAULT_P},
    "Nichtkanten sehr teuer (M = 100)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "family": "uni", "method": "nn", "rho": DEFAULT_RHO, "m": 100, "p": DEFAULT_P},
    "Gerade noch metrisch (M = 2)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "family": "uni", "method": "nn", "rho": DEFAULT_RHO, "m": 2, "p": DEFAULT_P},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "10 gleichverteilte Punkte: MST-Verdopplung, Christofides, nächster Nachbar und das Optimum nebeneinander.",
    "Lehrbeispiel (6 Punkte)": "Sechs Punkte: Gerüst, ungerade Knoten, Paarung und Abkürzung lassen sich Schritt für Schritt nachlesen.",
    "Gehäufte Punkte": "Drei Gruppen: Verfahren mit Garantie und einfache Heuristiken liegen eng beieinander.",
    "Schmaler Streifen": "Fast eine Gerade: das Gerüst ist ein Weg, die Verfahren sind (fast) optimal.",
    "Größte Instanz (14 Punkte)": "14 Punkte: das Optimum braucht 106.496 Tabellenzellen (n − 1 mal 2 hoch n − 1).",
    "Nichtkanten sehr teuer (M = 100)": "Eine Nichtkante kostet 100 statt 1: die Heuristiken liegen weit über dem Optimum n.",
    "Gerade noch metrisch (M = 2)": "Bei M = 2 gilt die Dreiecksungleichung, und jeder Rundweg ist höchstens doppelt so lang wie das Optimum.",
}
