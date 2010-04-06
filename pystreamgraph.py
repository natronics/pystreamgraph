# pystreamgraph.py copyright (C) 2010 Nathan Bergey <nathan.bergey@gmail.com>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# 
# Full licence is in the file COPYING and at http://www.gnu.org/copyleft/gpl.html

import svgfig 

class StreamGraph:
  """A class to generate a kind of data vizulazation called 'stream graphs'
  Based on the paper "Stacked Graphs - Geometry & Aesthetics" by Lee Byron & 
  Martin Wattenberg

  In general there are two things to consider:
    1.) The shape of the begginig layer, or g_0
    2.) The order you draw the layers.
  These two things will determine the shape and look of the graph.
  """

  # Data and meta-data. These should all be the same length!
  data = []             # The Data
  colors = []           # A list of colors for the layers
  labels = []           # A list of labels for the layers

  # Usefull things
  n_layers = 0          # Layers
  n_points = 0          # Points in a layer
  y_extent = []         # A list of maximum (stacked) y values for each x
  y_max = 0             # The maximun (stacked) y value for the whole dataset
  x_min = 0             # The smallest x vaule in the dataset 
  x_max = 0             # The largets x vaule in the dataset

  def __init__(self, data, colors = None, labels = None):
    self.data = data
    self.colors = colors
    self.labels = labels
    self.preprocess()


  def draw(self, filename, graphshape = None, width = 1280, height = 720, show_labels = False):
    """This does the drawing. It starts by getting a function for the bottom
    most layer. As descrbed in Byron & Wattenberg this will control the overall
    shape of the graph. It then it prints a stacked graph on top of that bottom 
    line, whatever shape it is.  
    """
    
    # Preprocess some stuff
    aspect_ratio = float(width) / float(height)
    x_offset = int( -((100 * aspect_ratio) - 100) / 2.0 )

    # Get a g_0 depending in desired shape
    g_0 = self.themeRiver() # Default (fallbacks)
    y_offset = 0
    if str(graphshape) == "Stacked_Graph" : 
      g_0 = self.stackedGraph()
      y_offset = 0
    if str(graphshape) == "Theme_River" : 
      g_0 = self.themeRiver()
      y_offset = -50
    if str(graphshape) == "Wiggle" : 
      g_0 = self.wiggle()
      y_offset = -50
    if str(graphshape) == "Weighted_Wiggle" : 
      g_0 = self.weighted_wiggle()
      y_offset = -50

    # Initilize a streamgraph groups in SVG.
    graph = svgfig.SVG("g", id="StreamGraph")
    labels = svgfig.SVG("g", id="Labels")

    # Initilize a SVG Window object to do the transormations on each object
    window = svgfig.window(self.x_min, self.x_max, 0, self.y_max * 1.3, x_offset, y_offset, int(100 * aspect_ratio), 100)

    # Loop through each layer
    for layer in range(0, self.n_layers):
      points = []
      point_range = range(0, self.n_points)
      # Forwards; draw top of the shape
      for i in point_range:
        x = self.data[layer][i][0]
        y = self.data[layer][i][1]
        # Start with g_0 and stack
        y_stacked = g_0[i] + y
        # Stack!
        for l in range(0, layer):
          y_stacked += self.data[l][i][1]
        # Add the points to the shape
        points.append((x, y_stacked))
      # Backwards; draw bottom of the shape
      point_range.reverse()
      for i in point_range:
        x = self.data[layer][i][0]
        # This time we don't include this layer
        y_stacked = g_0[i]
        # Stack!
        for l in range(0, layer):
          y_stacked += self.data[l][i][1]
        points.append((x,y_stacked))
      # Shapes  
      poly = svgfig.Poly(points, "smooth", stroke="#eeeeee", fill=self.rgb2hex(self.colors[layer]), stroke_width="0.05")
      graph.append(poly.SVG(window))
      if show_labels:
        label = self.placeLabel(points, layer)
        #labels.append(label.SVG(window))
    # End Loop

    # Add objects to the canvas and save it
    w = str(int(width)) + "px"
    h = str(int(height)) + "px"
    canv = svgfig.canvas(graph, labels, width=w, height=h)
    canv.save(filename)

  def placeLabel(self, points, layer):
    """Brute Force method to calculate a position for the labels. No other way 
    to do it except by hand.
    Starts by modeling the label as a rectangle, then tries to fit the rectangle
    in the current stream by making the box bigger and bigger
    """
    def interp(a,b,val):
      slope = float(b[1] - a[1]) / float(b[0] - a[0])
      inter = a[1] - slope * a[0]
      return (val * slope) + inter

    # Get the label
    label = self.labels[layer]
    print label

    # Take a guess at the aspect ratio of the word
    aspect_ratio = 0
    aspect_ratio = len(label) * 0.7  #magic
    iterations = 20

    # Try and fit a rectangle in the shape
    """
        x1,y2a               x2,y2b
        +-------------------+
        |                   |
        |                   |
        |                   |
        +-------------------+
        x1,y1a               x2,y1b
    """
    for p in range(len(points)/2 - 1):
      x1 = points[p][0]         # Bottom Point
      y1a = points[-(p+1)][1]    # Bottom Point
      y2a = points[p][1]         # Top Point
      y1b = points[-(p+2)][1]
      y2b = points[p + 1][1] 
      x2 = points[p + 1][0]
      x_iter = float(x2 - x1) / float(iterations)
      previous_height = y2a - y1a
      for i in range(iterations):
        x1p = x1 + x_iter*i
        y1p = interp((x1,y1a), (x2,y1b), x1p)
        y2p = interp((x1,y2a), (x2,y2b), x1p)
        height = y2p - y1p
        height_prime = height - previous_height
        print str(x1p) + "," + str(height) + "," + str(height_prime)
        previous_height = height
        
    

    return svgfig.Rect(0,5,0,2, fill="#cccccc", fill_opacity="50%") 

  ## Begin Graph types 

  def stackedGraph(self):
    """Returns a g_0 of exactly 0 (x-axis) for a traditional stacked graph 
    look
    """
    g_0 = []
    for i in range(0, self.n_points): g_0.append(0)
    return g_0

  def themeRiver(self):
    """The "Theme River" style is a basic stream graph and is symmetric around
    the x-axis
    """
    g_0 = []
    for i in range(self.n_points): 
      g_0.append(- self.y_extent[i] / 2.0)
    return g_0

  def wiggle(self):
    """Seeks to minimize wiggle by taking the slope of the lines into account as 
    well as the overall sillouet.
    """
    g_0 = []
    n = self.n_layers
    for i in range(self.n_points):
      wiggle = 0
      for layer in range(1, n):
          wiggle += (n - layer + 1) * self.data[layer][i][1]
      g_0.append(- (1 / float(n + 1) *  wiggle) )
    return g_0

  def weighted_wiggle(self):
    """Similar to the wiggle method, but this seeks to minimize the wiggle on a
    weighted scale of stream thicknes (i.e., visual importance)
    """
    g_0 = []
    g_prime_0 = []
    n = self.n_layers
    for y in range(self.n_points):
      wiggle = 0
      last_f = self.data[0][y][1]
      last_x = self.data[0][y][0]
      for i in range(n):
        f = self.data[i][y][1]
        x = self.data[i][y][0]
        if (x - last_x) != 0:
          f_prime = (f - last_x) / (x - last_x)
        else:
          f_prime = 0
        sumf_prime = 0
        sublast_f = self.data[1][y][1]
        sublast_x = self.data[1][y][0]
        for j in range(1, i - 1):
          subf = self.data[j][y][1]
          subx = self.data[j][y][0]
          if (subx - sublast_x) != 0:
            sumf_prime += (subf - sublast_f) / (subx - sublast_x)
          else:
            sumf_prime += 0
          sublast_f = subf
          sublast_x = subx
        wiggle += (0.5 * f_prime + sumf_prime) * f
        last_f = f
        last_x = x
      g_prime_0.append( - (1 / self.y_extent[y]) * wiggle )

    g = 0
    last_x = self.data[0][y][0]
    for i in range(self.n_points):
      x = self.data[0][i][0]
      step = x - last_x
      g += g_prime_0[i] * step
      g_0.append(g)
      last_x = x

    return g_0

  ## End Graph Types

  ## Begin Utilities 

  def preprocess(self):
    """Goes through the dataset at the beginning and figures out things so we
    don't have to calcualte them again later.
    """
    # Lengths for ranges
    self.n_layers = len(self.data)
    self.n_points = len(self.data[0])

    # Calculate the sum of the y values for each point
    for i in range(0, self.n_points):
      y_sum = 0
      for layer in range(0, self.n_layers):
        y_sum += self.data[layer][i][1]
      self.y_extent.append(y_sum)
      if self.y_max < y_sum : self.y_max = y_sum
    
    # Range of x vaules, assuming in order.
    self.x_min = self.data[0][0][0]
    self.x_max = self.data[0][-1][0]

  def rgb2hex(self, rgb):
    rgb = rgb[0]*255, rgb[1]*255, rgb[2]*255
    hexcolor = '#%02x%02x%02x' % rgb
    return hexcolor

  ## End Utilities 

## End StreamGraph
