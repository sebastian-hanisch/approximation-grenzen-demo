"""Kennzahlen, Messreihen und Verdikte (alle Verdikte sind reine Funktionen (Art, Text), DEMO-PLAYBOOK §12)."""

from dataclasses import dataclass
from statistics import median

import apx_algorithm as A
import apx_constants as C
from apx_rng import SplitMix64
from apx_scenario import make_points

TOL = C.TOLERANCE
EXTRA_METHODS = {"greedy": "Greedy-Kanten"}                                   # nur in der Familie ohne Dreiecksungleichung
ALL_METHODS = {"nn": "nächster Nachbar", "greedy": "Greedy-Kanten", "dt": "MST-Verdopplung", "chr": "Christofides"}


@dataclass(frozen=True, kw_only=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    family: str = C.DEFAULT_FAMILY
    method: str = C.DEFAULT_METHOD
    rho: int = C.DEFAULT_RHO
    m: int = C.DEFAULT_M
    p: int = C.DEFAULT_P


@dataclass(frozen=True)
class ReductionRow:
    label: str                       # „G“ oder „G ohne eine Kante des Kreises“
    edges: int
    has_cycle: bool                  # Brute Force
    opt: float                       # Optimum der Instanz (Held–Karp) mit M = ρ · n + 1
    threshold: float                 # ρ · n
    decided: bool                    # opt <= ρ · n: was ein ρ-Approximationsverfahren melden würde

    @property
    def agrees(self) -> bool:
        return self.has_cycle == self.decided


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    points: tuple
    dist: list
    opt: A.HkResult
    dt: A.TourResult
    chr: A.TourResult
    nn: tuple                        # (Rundweg, Kosten)
    planted: A.PlantedInstance
    planted_costs: dict              # Verfahren -> Kosten auf der eingepflanzten Instanz
    reduction: tuple                 # (ReductionRow, ReductionRow)

    def cost(self, method: str) -> float:
        return {"dt": self.dt.cost, "chr": self.chr.cost, "nn": self.nn[1]}[method]

    def tour(self, method: str) -> list:
        return {"dt": self.dt.tour, "chr": self.chr.tour, "nn": self.nn[0]}[method]

    def ratio(self, method: str) -> float:
        return self.cost(method) / self.opt.cost if self.opt.cost > 0 else 1.0


# --- Zahlen im deutschen Format ------------------------------------------------------------------------------------------------------------


def fmt_int(n: int) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner (106.496)."""
    return f"{n:,}".replace(",", ".")


def fmt_num(x: float, digits: int = 1) -> str:
    """Dezimalzahl mit Komma (22,7)."""
    return f"{x:.{digits}f}".replace(".", ",")


def fmt_median(x) -> str:
    """Median als ganze Zahl, wenn er eine ist, sonst mit einer Nachkommastelle und Komma (nie stillschweigend gerundet)."""
    return fmt_int(int(x)) if x == int(x) else fmt_num(float(x), 1)


def fmt_ratio(x: float) -> str:
    """Verhältnis zum Optimum mit drei Nachkommastellen und Komma (1,047)."""
    return fmt_num(x, 3)


def fmt_percent(x: float) -> str:
    return fmt_int(int(x)) if x == int(x) else fmt_num(x, 1)


def fmt_share(count: int, total: int) -> str:
    """Anteil als Prozentzahl (7 von 40 = 17,5 %)."""
    return f"{fmt_percent(100 * count / total)} %"


def fmt_factor(x: float) -> str:
    """Faktor mit Komma, auf zwei Nachkommastellen, ab 100 ganzzahlig (17,50; 292)."""
    return fmt_int(round(x)) if x >= 100 else fmt_num(x, 2)


# --- Einzelanalyse -------------------------------------------------------------------------------------------------------------------------


def reduction_rows(n: int, p: int, rho: int, seed: int) -> tuple:
    """Reduktion live: der Graph der eingepflanzten Instanz (hat einen Hamiltonkreis) und derselbe, in dem ein Knoten nur noch eine Kante behält (hat sicher keinen: dieser Knoten hat Grad 1); M = ρ · n + 1."""
    m = rho * n + 1
    inst = A.planted_instance(n, p, m, seed)
    edges = A.graph_edges(inst.dist)
    v, keep = inst.cycle[0], (min(inst.cycle[0], inst.cycle[1]), max(inst.cycle[0], inst.cycle[1]))
    pruned = [e for e in edges if v not in e or e == keep]
    rows = []
    for label, es in (("G (mit eingepflanztem Kreis)", edges), (f"G, Knoten {v} nur mit einer Kante", pruned)):
        opt = A.held_karp(A.graph_cost_matrix(n, es, m)).cost
        rows.append(ReductionRow(label, len(es), A.has_hamiltonian_cycle(n, es), opt, float(rho * n), opt <= rho * n + TOL))
    return tuple(rows)


def planted_costs(inst: A.PlantedInstance) -> dict:
    d = inst.dist
    return {"nn": A.tour_cost(d, A.nearest_neighbour(d)), "greedy": A.tour_cost(d, A.greedy_edge(d)),
            "dt": A.double_tree_tour(d).cost, "chr": A.christofides_tour(d).cost}


def analyse(settings: Settings) -> Analysis:
    points = make_points(settings.n, settings.seed, settings.family)
    dist = A.euclid_matrix(points)
    nn = A.nearest_neighbour(dist)
    planted = A.planted_instance(settings.n, settings.p, settings.m, settings.seed)
    return Analysis(settings, points, dist, A.held_karp(dist), A.double_tree_tour(dist), A.christofides_tour(dist), (nn, A.tour_cost(dist, nn)),
                    planted, planted_costs(planted), reduction_rows(settings.n, settings.p, settings.rho, settings.seed))


def brute_force_optimum(dist) -> float:
    """Alle Rundwege mit festem Startpunkt aufzählen (für n <= 8)."""
    import itertools
    n = len(dist)
    if n == 1:
        return 0.0
    return min(A.tour_cost(dist, (0,) + perm) for perm in itertools.permutations(range(1, n)))


def validation_errors(a: Analysis) -> list:
    """Ergebnis vor der Anzeige prüfen (DEMO-PLAYBOOK §1d): Rundwege vollständig, Kosten stimmig, Garantien, Beweisgrößen, bei n <= 8 Brute Force, Reduktion, eingepflanzter Kreis."""
    errors = []
    n, opt = a.settings.n, a.opt.cost
    for name, tour, cost in (("MST-Verdopplung", a.dt.tour, a.dt.cost), ("Christofides", a.chr.tour, a.chr.cost), ("nächster Nachbar", a.nn[0], a.nn[1]), ("Held–Karp", a.opt.tour, opt)):
        if not A.is_tour(n, tour):
            errors.append(f"{name}: der Rundweg besucht nicht jeden Punkt genau einmal.")
        elif abs(A.tour_cost(a.dist, tour) - cost) > TOL * max(1.0, cost):
            errors.append(f"{name}: die gemeldeten Kosten passen nicht zum Rundweg.")
        if cost < opt - TOL * max(1.0, opt):
            errors.append(f"{name}: der Rundweg ist billiger als das Optimum.")
    if a.dt.cost > 2 * opt + TOL * max(1.0, opt):
        errors.append("Die Garantie 2 der MST-Verdopplung ist verletzt.")
    if a.chr.cost > 1.5 * opt + TOL * max(1.0, opt):
        errors.append("Die Garantie 3/2 von Christofides ist verletzt.")
    if a.chr.mst_cost > opt + TOL * max(1.0, opt) or a.chr.matching_cost > opt / 2 + TOL * max(1.0, opt):
        errors.append("Eine Beweisgröße ist verletzt: das Gerüst muss höchstens das Optimum und die Paarung höchstens das halbe Optimum kosten.")
    if a.chr.cost > a.chr.mst_cost + a.chr.matching_cost + TOL * max(1.0, a.chr.cost):
        errors.append("Der Rundweg von Christofides ist länger als Gerüst plus Paarung.")
    if n <= 8 and abs(brute_force_optimum(a.dist) - opt) > TOL * max(1.0, opt):
        errors.append("Das Optimum widerspricht der Brute-Force-Probe.")
    if A.triangle_violations(a.dist):
        errors.append("Die Entfernungen verletzen die Dreiecksungleichung.")
    if abs(A.tour_cost(a.planted.dist, a.planted.cycle) - n) > TOL:
        errors.append("Der eingepflanzte Kreis kostet nicht n.")
    if any(c < n - TOL for c in a.planted_costs.values()):
        errors.append("Ein Verfahren ist auf der eingepflanzten Instanz billiger als das Optimum n.")
    for r in a.reduction:
        if not r.agrees:
            errors.append(f"Die Reduktion widerspricht dem Brute-Force-Hamiltonkreis ({r.label}).")
    return errors


# --- Messreihen ----------------------------------------------------------------------------------------------------------------------------


def sweep_quality(family: str, sizes=C.SWEEP_SIZES, seeds=C.SWEEP_SEEDS) -> list:
    """Verhältnis zum Optimum über n (feste Instanzen, euklidisch): Median und Maximum je Verfahren, Verletzungen der Garantien, Beweisgrößen (Gerüst / Optimum, Paarung / Optimum), ungerade Knoten."""
    rows = []
    for n in sizes:
        ratios = {"dt": [], "chr": [], "nn": []}
        mst, match, odd = [], [], []
        violations = dt_worse = skipped = 0
        for seed in seeds:
            dist = A.euclid_matrix(make_points(n, seed, family))
            opt = A.held_karp(dist).cost
            if opt <= 0:
                skipped += 1
                continue
            dt, ch = A.double_tree_tour(dist), A.christofides_tour(dist)
            nn_cost = A.tour_cost(dist, A.nearest_neighbour(dist))
            ratios["dt"].append(dt.cost / opt)
            ratios["chr"].append(ch.cost / opt)
            ratios["nn"].append(nn_cost / opt)
            mst.append(ch.mst_cost / opt)
            match.append(ch.matching_cost / opt)
            odd.append(len(ch.odd))
            violations += dt.cost > 2 * opt * (1 + TOL) or ch.cost > 1.5 * opt * (1 + TOL)
            dt_worse += dt.cost > nn_cost + TOL * nn_cost
        med = lambda v: median(v) if v else 1.0           # nur wenn alle Instanzen entartet waren (alle Punkte gleich): neutrale Werte
        rows.append({"n": n, "count": len(ratios["dt"]), "skipped": skipped, "violations": violations, "dt_worse_than_nn": dt_worse,
                     "median": {k: med(v) for k, v in ratios.items()}, "max": {k: max(v) if v else 1.0 for k, v in ratios.items()},
                     "mst_over_opt": med(mst), "matching_over_opt": med(match), "odd_median": med(odd)})
    return rows


@dataclass(frozen=True)
class SearchResult:
    method: str
    n: int
    best: float                      # größtes gefundenes Verhältnis zum Optimum
    points: tuple                    # die Punkte dieser Instanz
    restarts: tuple                  # bestes Verhältnis je Neustart


def _search_ratio(points, method: str) -> float:
    dist = A.euclid_matrix(points)
    opt = A.held_karp(dist).cost
    if opt <= 0:
        return 0.0
    cost = A.double_tree_tour(dist).cost if method == "dt" else A.christofides_tour(dist).cost
    return cost / opt


def search_worst_case(method: str, n: int = C.SEARCH_N, seed: int = C.SEARCH_SEED, steps: int = C.SEARCH_STEPS, restarts: int = C.SEARCH_RESTARTS) -> SearchResult:
    """Hügelsteigen über die Lage der Punkte: ein Punkt wird verschoben (erst grob ±200, dann fein ±40), behalten wird nur eine Verschlechterung für das Verfahren, also ein größeres Verhältnis zum Optimum."""
    if method not in ("dt", "chr"):
        raise ValueError("nur MST-Verdopplung und Christofides haben eine Garantie")
    top = C.COORD_MAX
    best_overall, best_points, per_restart = 0.0, (), []
    for restart in range(restarts):
        rng = SplitMix64(seed + restart + 10 * n)
        points = [(rng.below(top + 1), rng.below(top + 1)) for _ in range(n)]
        current = _search_ratio(points, method)
        for step in range(steps):
            i = rng.below(n)
            scale = 200 if step < steps * 2 // 5 else 40
            candidate = list(points)
            candidate[i] = (min(top, max(0, points[i][0] + rng.below(2 * scale + 1) - scale)), min(top, max(0, points[i][1] + rng.below(2 * scale + 1) - scale)))
            ratio = _search_ratio(candidate, method)
            if ratio > current:
                points, current = candidate, ratio
        per_restart.append(current)
        if current > best_overall:
            best_overall, best_points = current, tuple(points)
    return SearchResult(method, n, best_overall, best_points, tuple(per_restart))


def sweep_m(n: int = C.M_SWEEP_N, p: int = C.M_SWEEP_P, ms=C.M_OPTIONS, seeds=C.M_SWEEP_SEEDS) -> list:
    """Kosten / n (das Optimum der eingepflanzten Instanz ist n) über M für vier Verfahren: Median und Anteil der Läufe, die den Kreis finden (Kosten n); Verletzungen der Dreiecksungleichung und größter Rundweg."""
    rows = []
    for m in ms:
        costs = {k: [] for k in ALL_METHODS}
        violations = 0
        worst_tour = 0.0
        for seed in seeds:
            inst = A.planted_instance(n, p, m, seed)
            c = planted_costs(inst)
            for k in costs:
                costs[k].append(c[k] / n)
            violations += A.triangle_violations(inst.dist)
            worst_tour = max(worst_tour, max(c.values()) / n)
        rows.append({"m": m, "count": len(seeds), "violations": violations, "worst": worst_tour,
                     "median": {k: median(v) for k, v in costs.items()}, "found": {k: sum(x <= 1 + TOL for x in v) for k, v in costs.items()}})
    return rows


def reduction_all(sizes=C.REDUCTION_SIZES, random_n: int = C.REDUCTION_RANDOM_N, random_count: int = C.REDUCTION_RANDOM_COUNT, seed: int = C.REDUCTION_RANDOM_SEED) -> dict:
    """Hamiltonkreis ⇔ Optimum <= ρ · n (M = ρ · n + 1) auf ALLEN Graphen mit n in `sizes` und auf Zufallsgraphen mit `random_n` Knoten, für ρ = 1, 2, 3 (Brute Force gegen Held–Karp)."""
    checks = mismatches = with_cycle = graphs = 0

    def check(n, edges):
        nonlocal checks, mismatches
        has = A.has_hamiltonian_cycle(n, edges)
        for rho in C.RHO_OPTIONS:
            opt = A.held_karp(A.graph_cost_matrix(n, edges, rho * n + 1)).cost
            checks += 1
            mismatches += (opt <= rho * n + TOL) != has
        return has

    for n in sizes:
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
        for mask in range(1 << len(pairs)):
            graphs += 1
            with_cycle += check(n, [pr for i, pr in enumerate(pairs) if mask >> i & 1])
    rng = SplitMix64(seed)
    pairs = [(a, b) for a in range(random_n) for b in range(a + 1, random_n)]
    rand_cycle = 0
    for _ in range(random_count):
        rand_cycle += check(random_n, [pr for pr in pairs if rng.below(100) < 45])
    return {"sizes": tuple(sizes), "graphs": graphs, "with_cycle": with_cycle, "random_n": random_n, "random_count": random_count, "random_with_cycle": rand_cycle,
            "checks": checks, "mismatches": mismatches}


# --- Verdikte (reine Funktionen: (Art, Text)) ------------------------------------------------------------------------------------------------------


def verdict_run(a: Analysis) -> tuple:
    r = {k: a.ratio(k) for k in C.METHODS}
    best = min(r, key=lambda k: (r[k], k))
    head = (f"Optimum {fmt_num(a.opt.cost, 1)}. MST-Verdopplung {fmt_ratio(r['dt'])} (Garantie 2), Christofides {fmt_ratio(r['chr'])} (Garantie 1,5), "
            f"nächster Nachbar {fmt_ratio(r['nn'])} (keine Garantie) mal das Optimum; am besten: {C.METHODS[best]}.")
    if r["dt"] > 2 + TOL or r["chr"] > 1.5 + TOL:
        return "error", head + " Eine Garantie ist verletzt."
    if r["nn"] < r["dt"] - TOL:
        return "info", head + " Das Verfahren ohne Garantie ist hier besser als die Verdopplung mit Garantie."
    return "success", head


def verdict_proof(a: Analysis) -> tuple:
    c, opt = a.chr, a.opt.cost
    head = (f"Gerüst {fmt_num(c.mst_cost, 1)} ≤ Optimum {fmt_num(opt, 1)}; Paarung {fmt_num(c.matching_cost, 1)} ≤ halbes Optimum {fmt_num(opt / 2, 1)}; "
            f"Rundweg {fmt_num(c.cost, 1)} ≤ Gerüst plus Paarung {fmt_num(c.mst_cost + c.matching_cost, 1)}.")
    ok = c.mst_cost <= opt + TOL * max(1.0, opt) and c.matching_cost <= opt / 2 + TOL * max(1.0, opt) and c.cost <= c.mst_cost + c.matching_cost + TOL * max(1.0, c.cost)
    return ("success", head + " Zusammen: höchstens das Anderthalbfache des Optimums.") if ok else ("error", head + " Eine Ungleichung des Beweises ist verletzt.")


def verdict_quality(rows: list) -> tuple:
    total = sum(r["count"] for r in rows)
    bad = sum(r["violations"] for r in rows)
    if bad:
        return "error", f"Die Garantie wurde in {bad} von {total} Läufen verletzt: das darf nicht sein."
    worst = {k: max(r["max"][k] for r in rows) for k in ("dt", "chr", "nn")}
    last = rows[-1]
    worse = sum(r["dt_worse_than_nn"] for r in rows)
    return "info", (
        f"In allen {total} Läufen hielten die Garantien. Das größte gemessene Verhältnis war {fmt_ratio(worst['dt'])} bei der Verdopplung (Garantie 2) und {fmt_ratio(worst['chr'])} bei Christofides (Garantie 1,5); "
        f"beim nächsten Nachbarn ohne Garantie {fmt_ratio(worst['nn'])}. Bei n = {last['n']} lag der Median bei {fmt_ratio(last['median']['dt'])} (Verdopplung), {fmt_ratio(last['median']['chr'])} (Christofides) "
        f"und {fmt_ratio(last['median']['nn'])} (nächster Nachbar); die Verdopplung war in {worse} von {total} Läufen länger als der nächste Nachbar."
    )


def verdict_search(results: list) -> tuple:
    by = {r.method: r for r in results}
    return "warning", (
        f"Gesuchte schlechte Instanzen ({by['dt'].n} Punkte): MST-Verdopplung {fmt_ratio(by['dt'].best)} (Garantie 2), Christofides {fmt_ratio(by['chr'].best)} (Garantie 1,5). "
        "Das sind Funde einer Suche, nicht die Schärfe der Schranke: beide bleiben unter der Garantie."
    )


def verdict_reduction(rows: tuple, rho: int, n: int) -> tuple:
    if not all(r.agrees for r in rows):
        return "error", "Die Reduktion widerspricht dem Brute-Force-Hamiltonkreis: das darf nicht sein."
    parts = []
    for r in rows:
        meldung = "Hamiltonkreis" if r.decided else "kein Hamiltonkreis"
        parts.append(f"{r.label}: Optimum {fmt_num(r.opt, 1)}, Schwelle ρ · n = {fmt_int(int(r.threshold))}: ein {rho}-Approximationsverfahren würde „{meldung}“ melden (Brute Force: {'ja' if r.has_cycle else 'nein'})")
    return "info", f"Mit M = ρ · n + 1 = {rho * n + 1}: " + "; ".join(parts) + "."


def verdict_reduction_all(res: dict) -> tuple:
    sizes = " und ".join(str(s) for s in res["sizes"])
    if res["mismatches"]:
        return "error", f"Die Reduktion stimmte in {res['mismatches']} von {fmt_int(res['checks'])} Prüfungen nicht: das darf nicht sein."
    return "success", (
        f"Hamiltonkreis ⇔ Optimum ≤ ρ · n gilt auf allen {fmt_int(res['graphs'])} Graphen mit n = {sizes} ({fmt_int(res['with_cycle'])} mit Hamiltonkreis) und auf {res['random_count']} Zufallsgraphen mit n = {res['random_n']} "
        f"({res['random_with_cycle']} mit Hamiltonkreis), für ρ = 1, 2, 3: {fmt_int(res['checks'])} Prüfungen, 0 Abweichungen."
    )


def verdict_m(rows: list) -> tuple:
    at2 = next((r for r in rows if r["m"] == 2), None)
    big = rows[-1]
    parts = []
    if at2 is not None:
        parts.append(f"Bei M = 2 gilt die Dreiecksungleichung ({at2['violations']} Verletzungen), jeder Rundweg kostet höchstens 2 · n: das größte gemessene Verhältnis war {fmt_ratio(at2['worst'])}, die Güte 2 ist dort trivial.")
    parts.append(
        f"Bei M = {fmt_int(big['m'])} liegen die Kosten im Median beim {fmt_factor(big['median']['nn'])}-Fachen (nächster Nachbar), {fmt_factor(big['median']['greedy'])}-Fachen (Greedy-Kanten), "
        f"{fmt_factor(big['median']['dt'])}-Fachen (Verdopplung) und {fmt_factor(big['median']['chr'])}-Fachen (Christofides) des Optimums n; den Kreis fanden {big['found']['nn']}, {big['found']['greedy']}, "
        f"{big['found']['dt']} und {big['found']['chr']} von {big['count']} Läufen. Der Faktor wächst mit M: jeder falsche Schritt kostet M statt 1."
    )
    return "info", " ".join(parts)
