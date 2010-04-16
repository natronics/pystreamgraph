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

import random
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
  canvas_aspect = 0     # Aspect Ratio of the canvas (image)
  current_label = svgfig.Text(0,0," ")

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
    self.canvas_aspect = aspect_ratio
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
    for layer in range(self.n_layers):
      points = []
      point_range = range(self.n_points)
      # Forwards; draw top of the shape
      for i in point_range:
        x = self.data[layer][i][0]
        y = self.data[layer][i][1]
        # Start with g_0 and stack
        y_stacked = g_0[i] + y
        # Stack!
        for l in range(layer):
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
        for l in range(layer):
          y_stacked += self.data[l][i][1]
        points.append((x,y_stacked))
      # Shapes  
      poly = svgfig.Poly(points, "smooth", stroke="#eeeeee", fill=self.rgb2hex(self.colors[layer]), stroke_width="0.05")
      graph.append(poly.SVG(window))
      if show_labels:
        #label = self.placeLabel(points, layer)
        #label = self.test_placeLabel(points, layer)
        #label = self.test2_placeLabel(points, layer, window)
        label = self.placeLabel2(points, layer)
        #for l in label:
        #  labels.append(l)
        labels.append(label.SVG(window))
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

    # Take a guess at the aspect ratio of the word
    aspect_ratio = 0
    aspect_ratio = len(label) * 0.7  #magic
   
    max_area = 0
    max_area_x = 0
    max_area_y = 0

    end_of_line = (len(points) / 2)
    point_range = range(len(points))
    point_range.reverse()
    for i in range(1, end_of_line - 1):
      bottom_point = point_range[i]
      x = points[i][0]
      y = points[i][1]
      y_0 = points[bottom_point][1]
      xm1 = points[i - 1][0]
      ym1 = points[i - 1][1]
      ym1_0 = points[bottom_point + 1][1]
      xp1 = points[i + 1][0]
      yp1 = points[i + 1][1]
      yp1_0 = points[bottom_point - 1][1]
      height = y - y_0
      heightm1 = ym1 - ym1_0
      width = xp1 - x
      widthm1 = x - xm1
      area = (widthm1 * heightm1) + (height * height)
      if max_area < area: 
        max_area = area
        max_area_index = i
        max_area_index_0 = bottom_point


    placement_x1 = points[max_area_index - 1][0]
    placement_x2 = points[max_area_index + 1][0]
    width = placement_x2 - placement_x1
    placement_x = points[max_area_index][0]
    placement_y1 = points[max_area_index_0][1]
    placement_y2 = points[max_area_index][1]
    height = placement_y2 - placement_y1
    placement_y = placement_y1 + (height * 0.3)

    scale_height = (self.y_max / 40.0)
    return svgfig.Text(placement_x, placement_y, label, fill="#cccccc", font_size=str(height / scale_height), font_family="Droid Sans")
    #return svgfig.Rect(placement_x1, placement_y1, placement_x2, placement_y2, fill="#cccccc", fill_opacity="50%", stroke_width="0") 

  def test_placeLabel(self, points, layer):
    """Use this for testing different packing algorthims.
    """
    
    # Get the label
    label = self.labels[layer]

    # Take a guess at the aspect ratio of the word
    label_aspect = len(label) * 0.7  #magic

    window_aspect = (self.x_max - self.x_min) / float(self.y_max * 1.3)

    iterations = 20
    end_of_line = (len(points) / 2)
    point_range = range(len(points))
    point_range.reverse()
    for i in range(0, end_of_line - 1):
      bottom_point = point_range[i]
      x = points[i][0]
      y = points[i][1]
      y_0 = points[bottom_point][1]
      height_init = y_0 - y
      for i in range(iterations):
        height = height_init - (i * (height_init / iterations))
        width = height / (label_aspect / window_aspect)
     
    yint = 6
    x = points[yint][0]
    y = points[yint][1]
    y_0 = points[point_range[yint]][1]
    height = y - y_0
    width = height / (label_aspect / window_aspect / self.canvas_aspect)
    
    x1 = x
    y1 = y_0
    x2 = x1 + width
    y2 = y

    return svgfig.Rect(x1, y1, x2, y2, fill="#cccccc", fill_opacity="50%", stroke_width="0") 

  def test2_placeLabel(self, points, layer, window):

    def interp(a,b,val):
      slope = float(b[1] - a[1]) / float(b[0] - a[0])
      inter = a[1] - slope * a[0]
      return (val * slope) + inter

    def f_bl(x):
      point_range = range(len(points))
      point_range.reverse()
      last_x = 0
      for i in range(len(points) / 2):
        point = points[point_range[i]]
        #print str(point[0]) + "  " +str(x) + "  " + str(last_x)
        if x <= point[0] and x > last_x:
          #print "Bang!"
          return interp(point, points[point_range[i - 1]], x)
        last_x = point[0]
      return 0

    def f_tl(x):
      last_x = 0
      for i in range(len(points) / 2):
        point = points[i]
        if x <= point[0] and x > last_x:
          return interp(point, points[i - 1], x)
        last_x = point[0]
      return 0

    def is_box_in_shape(x1, y1, x2, y2):
      width = x2 - x1
      for j in range(resolution):
        x = x1 + ((width / float(resolution)) * j)
        y_lo = f_bl(x)
        y_hi = f_tl(x)
        if y1 < y_lo or y2 > y_hi:
          return False
      return True
    # Get the label
    label = self.labels[layer]
    # Take a guess at the aspect ratio of the word
    label_aspect = len(label) * 0.7  #magic
    window_aspect = (self.x_max - self.x_min) / float(self.y_max * 1.3)

    num_guesses = 400
    resolution = 10
   
    total_aspect = (((1 / label_aspect) / window_aspect) * self.canvas_aspect)

    
    height_max = 0
    boxes = svgfig.SVG("g", id="boxes")
    x1_l = 0
    x2_l = 0
    y1_l = 0
    y2_l = 0
    for i in range(num_guesses):
      x1 = random.uniform(self.x_min,self.x_max)
      y_lo = f_bl(x1)
      y_hi = f_tl(x1)
      h = y_hi - y_lo
      y1 = random.uniform(y_lo, y_hi - (h/8.0))
      y2 = random.uniform(y1,y_hi)
      height = y2 - y1
      x2 = x1 +  height / float(total_aspect)
      if is_box_in_shape(x1, y1, x2, y2):
        if height_max < height:
          height_max = height
          x1_l = x1
          y1_l = y1
          x2_l = x2
          y2_l = y2
        boxes.append(svgfig.Rect(x1,y1,x2,y2,fill="#eeeeee", fill_opacity="10%", stroke_width="0").SVG(window))

    boxes.append(svgfig.Rect(x1_l,y1_l,x2_l,y2_l,fill="#eeeeee", fill_opacity="23%", stroke_width="0").SVG(window))

    label_x = x1_l + ((x2_l - x1_l) / 2.0)
    label_y = y1_l + ((y2_l - y1_l) / 6.0)
    #print (y2_l - y1_l)
    font = ((y2_l - y1_l) / 2.5) #magic
    self.current_label = svgfig.Text(label_x, label_y, label, font_family="Droid Sans", font_size=str(font))
    
    return boxes
    
  def placeLabel2(self, points, layer):

    def interp(a,b,val):
      slope = float(b[1] - a[1]) / float(b[0] - a[0])
      inter = a[1] - slope * a[0]
      return (val * slope) + inter

    def f_bl(x):
      point_range = range(len(points))
      point_range.reverse()
      last_x = 0
      for i in range(len(points) / 2):
        point = points[point_range[i]]
        #print str(point[0]) + "  " +str(x) + "  " + str(last_x)
        if x <= point[0] and x > last_x:
          #print "Bang!"
          return interp(point, points[point_range[i - 1]], x)
        last_x = point[0]
      return 0

    def f_tl(x):
      last_x = 0
      for i in range(len(points) / 2):
        point = points[i]
        if x <= point[0] and x > last_x:
          return interp(point, points[i - 1], x)
        last_x = point[0]
      return 0

    def is_box_in_shape(x1, y1, x2, y2):
      width = x2 - x1
      for j in range(resolution):
        x = x1 + ((width / float(resolution)) * j)
        y_lo = f_bl(x)
        y_hi = f_tl(x)
        if y1 < y_lo or y2 > y_hi:
          return False
      return True
      
    # Get the label
    label = self.labels[layer]
    # Take a guess at the aspect ratio of the word
    label_aspect = len(label) * 0.7  #magic
    window_aspect = (self.x_max - self.x_min) / float(self.y_max * 1.3)
    total_aspect = (((1 / label_aspect) / window_aspect) * self.canvas_aspect)
    
    # How slow vs. how good
    num_guesses = 500
    resolution = 15
   
    height_max = 0
    boxes = svgfig.SVG("g", id="boxes")
    x1_l = 0
    x2_l = 0
    y1_l = 0
    y2_l = 0
    for i in range(num_guesses):
      x1 = random.uniform(self.x_min,self.x_max)
      y_lo = f_bl(x1)
      y_hi = f_tl(x1)
      h = y_hi - y_lo
      y1 = random.uniform(y_lo, y_hi - (h/8.0))
      y2 = random.uniform(y1,y_hi)
      height = y2 - y1
      x2 = x1 +  height / float(total_aspect)
      if is_box_in_shape(x1, y1, x2, y2):
        if height_max < height:
          height_max = height
          x1_l = x1
          y1_l = y1
          x2_l = x2
          y2_l = y2
          
    label_x = x1_l + ((x2_l - x1_l) / 2.0)
    label_y = y1_l + ((y2_l - y1_l) / 6.5)
    font_scale = self.y_max / 100.0
    font = ((y2_l - y1_l) / font_scale) * 0.9 #magic
    label = svgfig.Text(label_x, label_y, label, font_family="Droid Sans", font_size=str(font), fill="#e7e7e7")
    
    return label

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
