#!/usr/bin/env python
import pystreamgraph
import random
import colorsys

# Gen. some bogus data
data = []
colors = []
labels = ["one", "two", "three", "four", "five"]
for layer in range(0,5):
  x = []
  y = []
  for i in range(0,20):
    x.append(i)
    y.append(random.uniform(500,10000))
  data.append(zip(x,y))
  colors.append(colorsys.hsv_to_rgb(0.588, 0.2, random.uniform(0.4,0.7)))

sg = pystreamgraph.StreamGraph(data, colors=colors, labels=labels)
#sg.draw("Stacked_Graph.test.svg", "Stacked_Graph", width=512, height=512)
sg.draw("Theme_River.test.svg", "Theme_River", show_labels=True, width=1600, height=600)
#sg.draw("Wiggle.test.svg", "Wiggle")
#sg.draw("Weighted_Wiggle.test.svg", "Weighted_Wiggle")

