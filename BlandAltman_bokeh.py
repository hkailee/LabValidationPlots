''' Present a scatter plot with linked histograms on both axes.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve selection_histogram.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/selection_histogram
in your browser.
'''

import numpy as np
from bokeh.layouts import row, column
from bokeh.models import BoxSelectTool, LassoSelectTool, Spacer
from bokeh.plotting import figure, curdoc
from bokeh.models import Span
import pandas as pd

# create three normal population samples with different parameters
df = pd.read_excel("HC_Jenny.xlsx")

# Filter out unwanted data rows
df = df[df.tm_IU > 15]
df = df[df.cb_IU > 15]

# Defining values for x- and y- axes, from the DataFrame
x = df['Meanof2measures']
y = df['Differencebetween2measuresinlog']

# Toolset to be included in the bokeh browser (Optional)
TOOLS="save"

# create the scatter plot
p = figure(tools=TOOLS, plot_width=600, plot_height=600, min_border=10, min_border_left=50,
           toolbar_location="above", x_axis_location='below', y_axis_location=None,
           title="Linked Histograms")
p.background_fill_color = "#fafafa"
p.select(BoxSelectTool).select_every_mousemove = False
p.select(LassoSelectTool).select_every_mousemove = False


mean_y = Span(location=df['Differencebetween2measuresinlog'].mean(),
              dimension='width', line_color='green',
              line_dash='dashed', line_width=3)

std_y_upper = Span(location=df['Differencebetween2measuresinlog'].mean() + df['Differencebetween2measuresinlog'].std() * 1.96,
                   dimension='width', line_color='red',
                   line_dash='dashed', line_width=3)

std_y_lower = Span(location=df['Differencebetween2measuresinlog'].mean() - df['Differencebetween2measuresinlog'].std() * 1.96,
                   dimension='width', line_color='red',
                   line_dash='dashed', line_width=3)

p.add_layout(mean_y)
p.add_layout(std_y_upper)
p.add_layout(std_y_lower)

print(mean_y)
print(std_y_upper)
print(std_y_lower)

r = p.scatter(x, y, size=3, color="#3A5785", alpha=0.6)

LINE_ARGS = dict(color="#3A5785", line_color=None)

# create the vertical histogram
vhist, vedges = np.histogram(y, bins=20)
vzeros = np.zeros(len(vedges)-1)
vmax = max(vhist)*1.1

pv = figure(toolbar_location=None, plot_width=200, plot_height=p.plot_height, x_range=(0, vmax),
            y_range=p.y_range, min_border=10, y_axis_location="right")
pv.ygrid.grid_line_color = None
pv.xaxis.major_label_orientation = np.pi/4
pv.background_fill_color = "#fafafa"

pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vhist, color="white", line_color="#3A5785")
vh1 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.5, **LINE_ARGS)
vh2 = pv.quad(left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros, alpha=0.1, **LINE_ARGS)

layout = column(row(p, pv))

curdoc().add_root(layout)
curdoc().title = "Selection Histogram"

def update(attr, old, new):
    inds = np.array(new['1d']['indices'])
    if len(inds) == 0 or len(inds) == len(x):
        # hhist1, hhist2 = hzeros, hzeros
        vhist1, vhist2 = vzeros, vzeros
    else:
        neg_inds = np.ones_like(x, dtype=np.bool)
        neg_inds[inds] = False
        # hhist1, _ = np.histogram(x[inds], bins=hedges)
        vhist1, _ = np.histogram(y[inds], bins=vedges)
        # hhist2, _ = np.histogram(x[neg_inds], bins=hedges)
        vhist2, _ = np.histogram(y[neg_inds], bins=vedges)

    # hh1.data_source.data["top"]   =  hhist1
    # hh2.data_source.data["top"]   = -hhist2
    vh1.data_source.data["right"] =  vhist1
    vh2.data_source.data["right"] = -vhist2

r.data_source.on_change('selected', update)
