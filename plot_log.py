#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plotfile = sys.argv[1]
modelname = sys.argv[2]

ytsvfile =  sys.argv[3] # "iteration.tsv"
ctsvfile =  sys.argv[4] # "checkpoint.tsv"
etsvfile =  sys.argv[5] # "eval.tsv"
stsvfile =  sys.argv[6] # "sub.tsv"

maxticks=4

ydf = pd.read_csv(ytsvfile,sep='\t', encoding='utf-8')
cdf = pd.read_csv(ctsvfile,sep='\t', encoding='utf-8')
edf = pd.read_csv(etsvfile,sep='\t', encoding='utf-8')
sdf = pd.read_csv(stsvfile,sep='\t', encoding='utf-8')

ydf = ydf.sort_values('LearningIteration')
cdf = cdf.sort_values('LearningIteration')
edf = edf.sort_values('LearningIteration')
sdf = sdf.sort_values('LearningIteration')

y = ydf['IterationCER']
x = ydf['LearningIteration']
t = ydf['TrainingIteration']

c = cdf['CheckpointCER']
cx = cdf['LearningIteration']
ct = cdf['TrainingIteration']

e = edf['EvalCER']
ex = edf['LearningIteration']
et = edf['TrainingIteration'] # Not available in training log file

s = sdf['SubtrainerCER']
sx = sdf['LearningIteration']
st = sdf['TrainingIteration']

def annot_min(boxcolor, xpos, ypos, x, y, z):
    if z.isnull().values.any():
          xmin = x.iloc[np.argmin(y)]
          ymin = y.min()
          boxtext= " {:.3f}% at {:,} learning iterations " .format(ymin,xmin)
    else:
          tmin = z.iloc[np.argmin(y)]
          xmin = x.iloc[np.argmin(y)]
          ymin = y.min()
          boxtext= " {:.3f}% at {:,} / {:,} " .format(ymin,xmin,tmin)
    ax1.annotate(boxtext, xy=(xmin, ymin), xytext=(xpos,ypos), textcoords='offset points', color='black', fontsize=9,
        arrowprops=dict(shrinkA=1, shrinkB=1, fc=boxcolor,alpha=0.7, ec='white', connectionstyle="arc3"),
        bbox=dict(boxstyle='round,pad=0.2', fc=boxcolor, alpha=0.3))

PlotTitle="Tesseract LSTM Training : " + modelname
fig = plt.figure(figsize=(11,8.5)) #size is in inches
ax1 = fig.add_subplot()

ax1.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax1.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.1f"))
ax1.set_ylabel('Error Rate %')

ax1.set_xlabel('Learning Iterations')
ax1.set_xticks(x)
ax1.tick_params(axis='x', labelsize='small')
ax1.locator_params(axis='x', nbins=maxticks)  # limit ticks on x-axis
ax1.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax1.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))

ax1.scatter(x, y, c='teal', alpha=0.7, s=0.5, label='BCER at #iterations/100 - lstmtraining - list.train')
ax1.plot(x, y, 'teal', alpha=0.3, linewidth=0.5, label='Training BCER')
ax1.grid(True)

if not c.dropna().empty: # not NaN or empty
    ax1.scatter(cx, c, c='teal', marker='x', s=35,
       label='BCER at checkpoints - lstmtraining - list.train', alpha=0.5)
    annot_min('teal',-50,-50,cx,c,ct)

if not e.dropna().empty: # not NaN or empty
    ax1.plot(ex, e, 'magenta', linewidth=1.0, label='Validation BCER')
    ax1.scatter(ex, e, c='magenta', s=30,
       label='BCER at checkpoints - lstmtraining - list.eval', alpha=0.5)
    annot_min('magenta',-50,50,ex,e,et)

if not s.dropna().empty: # not NaN or empty
    ax1.plot(sx, s, 'orange', linewidth=0.5, label='SubTrainer BCER')
    ax1.scatter(sx, s, c='orange', s=0.5,
       label='BCER for UpdateSubtrainer every 100 iterations', alpha=0.5)
    annot_min('orange',-100,-100,sx,s,st)

plt.title('character error rate over learning iterations - from lstmtraining',fontsize=10)
plt.suptitle(PlotTitle, y=0.95, fontsize = 14, fontweight = 'bold')
plt.legend(loc='upper right')

ax1.set_ylim([-0.5,100])

# Secondary x axis on top to display Training Iterations
ax2 = ax1.twiny() # ax1 and ax2 share y-axis
ax2.set_xlabel("Training Iterations")
ax2.set_xlim(ax1.get_xlim()) # ensure the independent x-axes now span the same range
ax2.set_xticks(x) # copy over the locations of the x-ticks from Learning Iterations
ax2.tick_params(axis='x', labelsize='small')
ax2.set_xticklabels(matplotlib.ticker.StrMethodFormatter('{x:,.0f}').format_ticks(t)) # But give value of Training Iterations
ax2.locator_params(axis='x', nbins=maxticks)  # limit ticks to same as x-axis
ax2.xaxis.set_ticks_position('bottom') # set the position of ticks of the second x-axis to bottom
ax2.xaxis.set_label_position('bottom') # set the position of labels of the second x-axis to bottom
ax2.spines['bottom'].set_position(('outward', 36)) # positions the second x-axis below the first x-axis

plt.savefig(plotfile)
