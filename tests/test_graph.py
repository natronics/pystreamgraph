#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_graph
----------------------------------

Tests for `graph` module.
"""

from __future__ import print_function
import unittest
import colorsys
import random
import pystreamgraph
from pystreamgraph import graph


class TestGraph(unittest.TestCase):

    def setUp(self):
        # Gen. some bogus data
        self.data = []
        self.colors = []
        self.labels = ["one", "two", "three", "four", "five"]
        for layer in range(5):
            x = [i for i in range(20)]
            y = [random.uniform(500, 10000) for i in range(20)]
            self.data.append(zip(x, y))
            self.colors.append(colorsys.hsv_to_rgb(0.588, 0.2, random.uniform(0.4, 0.7)))

    def test_river(self):
        sg = graph.Stream(self.data, colors=self.colors, labels=self.labels)
        sg.draw("Theme_River.test.svg", pystreamgraph.THEME_RIVER, show_labels=True, width=1600, height=600)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
