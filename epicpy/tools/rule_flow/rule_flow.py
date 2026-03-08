"""
This file is part of the EPICpy source code. EPICpy is a tool for simulating
human performance tasks using the EPIC computational cognitive architecture
(David Kieras and David Meyer 1997a) using the Python programming language.
Copyright (C) 2022-2026 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import shutil
import timeit
from collections.abc import Iterable
from textwrap import dedent
from typing import Set

import networkx as nx
from epiclibcpp.epiclib.output_tee_globals import Exception_out
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from qtpy.QtCore import QByteArray
from qtpy.QtGui import QColor, QGuiApplication, QPen
from qtpy.QtSvgWidgets import QSvgWidget
from qtpy.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from epicpy.widgets.mem_large_text_view import MemLargeTextView

# Global flag: is Graphviz available?
HAVE_GRAPHVIZ = False

import importlib.util

if importlib.util.find_spec("graphviz") is not None:
    from graphviz import Digraph

    # Also check if the 'dot' executable is on PATH
    if shutil.which("dot"):
        HAVE_GRAPHVIZ = True
else:
    Digraph = None
    HAVE_GRAPHVIZ = False

WHICH_NETWORKX = 0  # in (0=directed_one_level, 1=directed_multi_level)

"""
Create an EPIC rule graph based on the trace output.
NOTE: for now, I think we're using the content of the Normal Output Window, not the Trace Output Window.
"""

import re
from typing import Dict, Tuple


# ~.08 sec
class RegexScheduler(object):
    FIRE_PATTERN = re.compile(r"^\*\*\* Fire: (.+)$")

    def __init__(self):
        self.nodes: Dict[str, int] = {}
        self.edges: Set[Tuple[str, str]] = set()
        self.last_rule: str = ""
        self.redraw: bool = False

    @staticmethod
    def _normalize_rule(rule: str) -> str:
        rule = rule.replace("_", "\n")
        return rule.replace("visualresponse", "visual\nresponse")

    def process_lines(self, lines: Iterable[str]):
        """
        Find all rule firings by scanning lines, then build nodes/edges.
        Works directly with an iterable (e.g., deque) to avoid copying.
        """
        for line in lines:
            match = self.FIRE_PATTERN.match(line)
            if not match:
                continue

            rule = self._normalize_rule(match.group(1))

            if not self.nodes:
                # First rule starts subset 1
                self.nodes[rule] = 1
                self.last_rule = rule
                continue

            if rule not in self.nodes:
                self.nodes[rule] = self.nodes[self.last_rule] + 1

            # Always add edge from last_rule → rule
            self.edges.add((self.last_rule, rule))
            self.last_rule = rule

        self.redraw = True

    def display(self):
        print(self.__str__())


# ~.11 sec
class OrigScheduler(object):
    def __init__(self):
        self.nodes: dict = {}  # dict where they keys are the str labels and the values are the subset ints
        self.edges: Set[tuple] = set()
        self.last_rule: str = ""
        self.redraw: bool = False

    def process_lines(self, lines: Iterable[str]):
        """
        looking for rule firings, e.g.:
        *** Fire: Identify_steeringwheel
        Creates a unique list of rules
        Creates a unique list of edges by combining rules with their predecessor
        """
        start = timeit.default_timer()
        for line in lines:
            line = line.strip()
            if line.startswith("*** Fire: "):
                rule = line.split(": ")[-1]
                rule = rule.replace("_", "\n")
                rule = rule.replace("visualresponse", "visual\nresponse")

                if len(self.nodes) < 1:
                    # Adds first subset to the first rule
                    self.nodes[rule] = 1
                else:
                    # if the current rule was not already added
                    # it is part of the subset below the current node
                    if rule not in self.nodes.keys():
                        self.nodes[rule] = self.nodes[self.last_rule] + 1

                if len(self.nodes) < 2:
                    # This must be the first rule, set last rule and move on
                    self.last_rule = rule
                else:
                    # make pairs like normal (previous last-rule plus this rule)
                    edge = (self.last_rule, rule)
                    self.edges.add(edge)
                    self.last_rule = rule
        print(f"Finished text process in {timeit.default_timer() - start:0.5f} sec.")
        self.redraw = True

    def display(self):
        print(self.__str__())


class RuleFlowWindow(QMainWindow):
    def __init__(self, trace_widget: MemLargeTextView):
        super(RuleFlowWindow, self).__init__()

        self.trace_widget: MemLargeTextView = trace_widget

        """ Setup GUI """

        # self.font = QFont()
        # self.font.setPointSize(16)
        self.pen = QPen(QColor("black"))
        self.scheduler = RegexScheduler()

        self.setWindowTitle("EPICViewRuleFlow")
        self.setGeometry(100, 100, 1024, 768)

        self.figure = plt.figure(dpi=125)
        self.canvas = FigureCanvas(self.figure)

        my_graph_widget = QWidget()
        layout = QVBoxLayout(my_graph_widget)
        layout.addWidget(self.canvas)
        self.setCentralWidget(my_graph_widget)

        self.center_me()

    def update_graph_edges(self):
        self.scheduler = RegexScheduler()
        self.scheduler.process_lines(self.trace_widget.lines)

    def center_me(self):
        center_point = QGuiApplication.screens()[0].geometry().center()
        self.move(center_point - self.frameGeometry().center())

    def create_directed_graph_off(self, *args, **kwargs):
        self.figure.clear()
        G = nx.gnp_random_graph(10, 0.5)
        nx.draw(G, with_labels=True, ax=self.figure.add_subplot(111))
        self.canvas.draw()

    def create_directed_graph(self, node_dict: dict, edge_set: set):
        # min_width_inch, min_height_inch = 10, 8

        def pixels_to_inches(width_px, height_px, dpi=100):
            width_in = width_px / dpi
            height_in = height_px / dpi
            return width_in, height_in

        try:
            self.figure.clear()

            # Create a NextworkX directed graph
            graph = nx.DiGraph()

            for key, value in node_dict.items():
                graph.add_node(key, subset=value)

            edges = list(edge_set)
            graph.add_edges_from(edges)

            # Draw the graph

            pos = nx.multipartite_layout(graph, align="vertical")

            # Check if there is a loop in the digraph with nx.recursive_simple_cycles
            # if there is the lines are curved else they are straight
            if len(nx.recursive_simple_cycles(graph)) > 0:
                arc_rad = 0.5
            else:
                arc_rad = 0

            # Draw the graph
            nx.draw(
                graph,
                pos,
                with_labels=True,
                node_color=[[1, 1, 1, 0]],  # transparent for testing use: 'red'
                node_size=1800,
                node_shape="s",
                edge_color="black",
                linewidths=1,
                arrowsize=9,
                font_family="DejaVu Sans Mono",
                font_size=8,
                ax=self.figure.add_subplot(111),
                connectionstyle=f"arc3,rad={arc_rad}",
                # Making a bounding box that has color
                # https://stackoverflow.com/questions/30344592/networkx-how-to-change-the-shape-of-the-node
                bbox=dict(
                    facecolor="goldenrod",
                    edgecolor="black",
                    boxstyle="round,pad=0.2",
                    alpha=1.0,
                ),
            )

            # plt.text(0, 0, self.get_info())
            self.setWindowTitle(self.get_info())

            self.canvas.draw()

        except Exception as e:
            Exception_out(f"Problem drawing graph: {e}")

    def create_directed_graph_separated(self, node_dict: dict, edge_set: set):
        min_width_inch, min_height_inch = 10, 8

        def pixels_to_inches(width_px, height_px, dpi=100):
            return width_px / dpi, height_px / dpi

        try:
            # ----- build graph -----
            graph = nx.DiGraph()
            for key, value in node_dict.items():
                graph.add_node(key, subset=value)
            graph.add_edges_from(list(edge_set))

            # ----- figure sizing on the *existing* self.figure -----
            screen = QGuiApplication.primaryScreen()
            logical_dpi = screen.logicalDotsPerInch()

            f_width, f_height = pixels_to_inches(self.width(), self.height(), int(logical_dpi))
            f_width = min(max(f_width, min_width_inch), 10)
            f_height = min(max(f_height, min_height_inch), 8)

            # Clear and (re)size the existing figure used by the canvas
            self.figure.clear()
            self.figure.set_dpi(logical_dpi)
            self.figure.set_size_inches(f_width, f_height, forward=True)

            ax = self.figure.add_subplot(111)

            # layout
            pos = nx.multipartite_layout(graph, align="vertical")

            # curved edges only if cycles exist
            arc_rad = 0.3 if len(nx.recursive_simple_cycles(graph)) > 0 else 0.0

            # ----- three-pass draw -----

            # 1) Nodes as solid golden boxes (no label bbox later, so no double-box)
            nx.draw_networkx_nodes(
                graph,
                pos,
                ax=ax,
                node_shape="s",
                node_size=1800,
                node_color="goldenrod",
                edgecolors="black",
                linewidths=1.0,
                alpha=1.0,
            )

            # 2) Edges after nodes, with margins so arrowheads meet the box edge
            nx.draw_networkx_edges(
                graph,
                pos,
                ax=ax,
                arrows=True,
                arrowstyle="-|>",
                arrowsize=9,
                edge_color="black",
                width=1.0,
                connectionstyle=f"arc3,rad={arc_rad}",
                min_source_margin=20,  # a bit larger since boxes are solid now
                min_target_margin=20,
            )

            # 3) Labels on top, *without* bbox so they don’t cover arrows
            nx.draw_networkx_labels(
                graph,
                pos,
                ax=ax,
                font_family="DejaVu Sans Mono",
                font_size=8,
            )

            ax.set_axis_off()
            self.setWindowTitle(self.get_info())
            self.canvas.draw_idle()

        except Exception as e:
            print(f"Problem drawing graph: {e}")

    def create_directed_graph_graphviz(self, node_dict: dict, edge_set: set):
        """
        Render the same graph with Graphviz DOT → SVG, then show it in a QSvgWidget.
        """
        dot = Digraph(engine="dot")  # layered layout
        # Global graph / node / edge styles
        dot.attr(rankdir="LR", splines="spline", overlap="false", concentrate="true")
        dot.attr(
            "node",
            shape="box",
            style="rounded,filled",
            color="black",
            fillcolor="goldenrod",
            fontname="DejaVu Sans Mono",
            fontsize="12",
            penwidth="1.2",
        )
        dot.attr("edge", arrowsize="0.9", color="black", penwidth="1.2")

        # Group nodes into columns using rank=same (one subgraph per subset)
        # node_dict: {label: subset_int}
        by_subset = {}
        for label, subset in node_dict.items():
            by_subset.setdefault(subset, []).append(label)

        # Create subgraphs to force column alignment
        for subset, labels in sorted(by_subset.items()):
            with dot.subgraph(name=f"cluster_subset_{subset}") as sg:
                sg.attr(rank="same")  # put these on the same rank (column)
                sg.attr(color="transparent")  # no visible box around the group
                for label in labels:
                    sg.node(label)

        # Add edges
        for u, v in edge_set:
            dot.edge(u, v)

        # Produce SVG bytes in-memory
        svg_bytes = dot.pipe(format="svg")

        # Display in Qt
        # Replace the central widget’s content with an SVG viewer once, then just load data
        if not hasattr(self, "_svg_widget"):
            self._svg_widget = QSvgWidget()
            self._svg_widget.setMinimumSize(1024, 768)
            self.setCentralWidget(self._svg_widget)

        self._svg_widget.load(QByteArray(svg_bytes))
        self._svg_widget.repaint()

        # Optional: window title / status
        self.setWindowTitle(self.get_info())

    def get_info(self) -> str:
        # extra_space = "\n" * 25
        try:
            info = (
                f"Rule Nodes: {len(self.scheduler.nodes)} | "
                f"Rule Edges: {len(self.scheduler.edges)}) | "
                f"{'Using GraphVis' if HAVE_GRAPHVIZ else 'Using NetworkX'}"
            )
        except Exception as e:
            info = f"Unknown! ({e})"
        return dedent(info)

    def update_graph(self):
        # reset background image
        if HAVE_GRAPHVIZ:
            self.create_directed_graph_graphviz(self.scheduler.nodes, self.scheduler.edges)
        else:
            if WHICH_NETWORKX == 0:
                self.create_directed_graph(self.scheduler.nodes, self.scheduler.edges)
            elif WHICH_NETWORKX == 1:
                self.create_directed_graph_separated(self.scheduler.nodes, self.scheduler.edges)
            else:
                raise ValueError(f"{WHICH_NETWORKX=} is not a valid NETWORKX method reference")

    def showEvent(self, event):
        super().showEvent(event)
        self.center_me()
        self.activateWindow()
        self.raise_()
