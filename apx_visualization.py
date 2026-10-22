"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import apx_constants as C
from apx_evaluation import ALL_METHODS


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _segments(points, order, closed=True):
    xs, ys = [], []
    count = len(order) if closed else len(order) - 1
    for i in range(count):
        a, b = points[order[i]], points[order[(i + 1) % len(order)]]
        xs += [a[0], b[0], None]
        ys += [a[1], b[1], None]
    return xs, ys


def _edge_segments(points, edges):
    xs, ys = [], []
    for a, b in edges:
        xs += [points[a][0], points[b][0], None]
        ys += [points[a][1], points[b][1], None]
    return xs, ys


def _point_trace(points, name="Punkte", color=C.COLOR_POINT):
    return go.Scatter(x=[p[0] for p in points], y=[p[1] for p in points], mode="markers+text", text=[str(i) for i in range(len(points))], textposition="top center",
                      marker=dict(color=color, size=9), name=name, hovertemplate="Punkt %{text}<br>x %{x}, y %{y}<extra></extra>")


def build_tour_map(points, tour, opt_tour, method_name):
    """Rundweg des Verfahrens (durchgezogen) und der optimale Rundweg (gestrichelt) über den Punkten."""
    fig = go.Figure()
    xs, ys = _segments(points, opt_tour)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_OPT, width=2, dash="dash"), name="Optimum", hoverinfo="skip"))
    xs, ys = _segments(points, tour)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_TOUR, width=3), name=method_name, hoverinfo="skip"))
    fig.add_trace(_point_trace(points))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return _base(fig, 380)


def build_christofides_map(points, result):
    """Bausteine von Christofides: Gerüst (blau), Paarung der ungeraden Knoten (gelb, gestrichelt), ungerade Knoten gelb markiert."""
    fig = go.Figure()
    xs, ys = _edge_segments(points, result.mst_edges)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_TREE, width=3), name="Gerüst", hoverinfo="skip"))
    if result.matching:
        xs, ys = _edge_segments(points, result.matching)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_MATCH, width=3, dash="dash"), name="Paarung", hoverinfo="skip"))
    even = [i for i in range(len(points)) if i not in result.odd]
    for name, idx, color in (("gerader Grad", even, C.COLOR_POINT), ("ungerader Grad", list(result.odd), C.COLOR_MATCH)):
        if idx:
            fig.add_trace(go.Scatter(x=[points[i][0] for i in idx], y=[points[i][1] for i in idx], mode="markers+text", text=[str(i) for i in idx], textposition="top center",
                                     marker=dict(color=color, size=10), name=name, hovertemplate="Punkt %{text}<extra></extra>"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return _base(fig, 380)


def build_ratio_bars(ratios):
    """Verhältnis zum Optimum je Verfahren; die Marken zeigen die Garantie (2 bzw. 3/2)."""
    names = [C.METHODS[k] for k in C.METHODS]
    fig = go.Figure(go.Bar(x=names, y=[ratios[k] for k in C.METHODS], marker_color=[C.COLOR_SERIES[i] for i in range(len(names))],
                           text=[f"{ratios[k]:.3f}".replace(".", ",") for k in C.METHODS], textposition="outside"))
    for i, k in enumerate(C.METHODS):
        if k in C.GUARANTEE:
            fig.add_shape(type="line", x0=i - 0.4, x1=i + 0.4, y0=C.GUARANTEE[k], y1=C.GUARANTEE[k], line=dict(color=C.COLOR_GUARANTEE, width=3, dash="dash"))
    fig.update_yaxes(title="Kosten / Optimum", range=[0.9, 2.15])
    return _base(fig, 320)


def build_proof_bars(a):
    """Die Größen des Beweises von Christofides an dieser Instanz."""
    c = a.chr
    labels = ["Gerüst", "Paarung", "halbes Optimum", "Optimum", "Gerüst + Paarung", "Rundweg Christofides"]
    values = [c.mst_cost, c.matching_cost, a.opt.cost / 2, a.opt.cost, c.mst_cost + c.matching_cost, c.cost]
    colors = [C.COLOR_TREE, C.COLOR_MATCH, C.COLOR_OPT, C.COLOR_OPT, C.COLOR_TREE, C.COLOR_TOUR]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:.1f}".replace(".", ",") for v in values], textposition="outside"))
    fig.update_yaxes(title="Länge")
    return _base(fig, 320)


def build_quality(rows):
    """Median (durchgezogen) und Maximum (gestrichelt) des Verhältnisses über n für drei Verfahren, dazu die Garantien."""
    fig = go.Figure()
    ns = [r["n"] for r in rows]
    for color, k in zip(C.COLOR_SERIES, C.METHODS):
        fig.add_trace(go.Scatter(x=ns, y=[r["median"][k] for r in rows], mode="lines+markers", name=f"{C.METHODS[k]}, Median", line=dict(color=color)))
        fig.add_trace(go.Scatter(x=ns, y=[r["max"][k] for r in rows], mode="lines+markers", name=f"{C.METHODS[k]}, Maximum", line=dict(color=color, dash="dash"), marker=dict(symbol="triangle-up")))
    for g, label in ((2.0, "Garantie 2"), (1.5, "Garantie 3/2")):
        fig.add_hline(y=g, line=dict(color=C.COLOR_GUARANTEE, dash="dot"), annotation_text=label, annotation_position="top left")
    fig.update_xaxes(title="Punkte n", dtick=2)
    fig.update_yaxes(title="Kosten / Optimum", range=[0.95, 2.1])
    return _base(fig, 400)


def build_m(rows):
    """Kosten / n über M (beide Achsen logarithmisch) für vier Verfahren auf der eingepflanzten Familie; das Optimum ist n."""
    fig = go.Figure()
    for color, k in zip(C.COLOR_SERIES, ALL_METHODS):
        fig.add_trace(go.Scatter(x=[r["m"] for r in rows], y=[r["median"][k] for r in rows], mode="lines+markers", name=ALL_METHODS[k], line=dict(color=color)))
    fig.add_hline(y=2, line=dict(color=C.COLOR_GUARANTEE, dash="dot"), annotation_text="Faktor 2", annotation_position="bottom right")
    fig.update_xaxes(type="log", title="Kosten M der Nichtkanten")
    fig.update_yaxes(type="log", title="Kosten / Optimum (Median)")
    return _base(fig, 380)


def build_graph(n, edges, cycle):
    """Der Graph auf einem Kreis angeordnet: die Kanten des eingepflanzten Hamiltonkreises grün, die Köder grau."""
    pos = [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]
    cycle_edges = {(min(cycle[i], cycle[(i + 1) % n]), max(cycle[i], cycle[(i + 1) % n])) for i in range(n)}
    fig = go.Figure()
    decoys = [e for e in edges if e not in cycle_edges]
    kept = [e for e in edges if e in cycle_edges]
    for name, es, color, width in (("Köder", decoys, "rgba(150,150,150,0.7)", 1.5), ("Kante des eingepflanzten Kreises", kept, C.COLOR_TOUR, 3)):
        if es:
            xs, ys = _edge_segments(pos, es)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width), name=name, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[p[0] for p in pos], y=[p[1] for p in pos], mode="markers+text", text=[str(i) for i in range(n)], textposition="top center",
                             marker=dict(color=C.COLOR_POINT, size=9), name="Knoten", hovertemplate="Knoten %{text}<extra></extra>"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return _base(fig, 340)
