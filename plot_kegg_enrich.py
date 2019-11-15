#!/usr/bin/env python
# coding=utf-8
import matplotlib.pyplot as plt
from itertools import islice
import math
import numpy as np
from matplotlib.font_manager import FontProperties




file = open("enrich_kegg.txt", "r")

name = list()
p_value = list()
for line in islice(file, 1, None):
    line = line.split("\t")
    name.append(line[1])
#            p_value.append(-math.log(float(line[6]), 10))
    p_value.append(-math.log(float(line[3]), 10))


name.reverse()
p_value.reverse()


p_max = max(p_value)

plt.rcdefaults()
customer_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf")

# (width, height)
len_max = max([len(term) for term in name])
# print(len_max)
width_user = round(len_max / 40 * 6.1 + 5)
height_user = 0.6 * len(p_value) + 2

# plt.rcParams['figure.autolayout'] = True
plt.rcParams['figure.figsize'] = (width_user, height_user)
fig = plt.figure()
ax = fig.add_axes([0.95 - 5 / width_user, 0.05, 5 / width_user, 0.95 - 1 / height_user])
# ax = fig.add_axes([0.1,0.1, 0.8, 0.8])
# ax = plt.axes()
ax.barh(np.arange(0, len(name)), p_value, height=0.6, color="#483D8B", linestyle="-", edgecolor="black",
        linewidth=2)

ax.spines['bottom'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')
ax.xaxis.set_ticks_position('top')
ax.spines['top'].set_position(('axes', 0.99))
ax.set_yticks(np.arange(len(p_value))) 
customer_font2 = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=16)
ax.set_yticklabels(name,fontProperties=customer_font2)

# ax.set_xticks(range(0, int(p_max + 1) + 1))
ax.set_xlim(0,int(p_max + 1)+1)
customer_font2 = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=22)
plt.xticks(fontProperties=customer_font2)
# plt.xticks(size=18,fontProperties=customer_font)
#  plt.xticks(fontdict={"fontsize":22},fontProperties=customer_font)
# ax.set_xticklabels(range(0, int(p_max + 1) + 1), fontdict={'fontsize': 22}, fontProperties=customer_font)
customer_font2 = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=22)
plt.title("-Log10(P_Value)\n", y=1.025, fontProperties=customer_font2,fontweight="bold")
# plt.xlim(0, round(p_max)+1) # change
plt.savefig("enrich_kegg.tiff",dpi=150)
plt.close()


