import os
import re
import time
from matplotlib.font_manager import FontProperties
import math
import pylab
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap
import sys
from itertools import  chain

def _enrich_go_plot(lengend_offset=None):
    title = ['GO-ID', 'Term', 'Category', 'FDR', 'P-Value', '#DIFF', '#REF', '%Diff', '%Ref', 'Over/Under', 'TestSeqs']
    enrich_go = open("enrich_go.txt", "w")
    enrich_go.write('\t'.join(title) + '\n')

    def get_term_and_percent(bp_mf_cc,enrich_go):
        term= list()
        percent= list()
        try:
            filtered = filter(lambda line: line.split("\t")[9] == "over" and line.split("\t")[2] == bp_mf_cc and float(
                line.split("\t")[4]) < 0.05, open("enrich.txt", "r"))
            sorted_temp = sorted(filtered, key=lambda s: float(s.split("\t")[4]))[:10]
            for line in list(sorted_temp):
                term.append(line.split('\t')[1])
                percent.append(-math.log(float(line.split('\t')[4]),10))
            enrich_go.write(''.join(sorted_temp))
            percent.reverse()
            term.reverse()
        except:
            term = None
            percent = None
        return term,percent



    term_bp,percent_bp = get_term_and_percent("P",enrich_go)
    term_mf,percent_mf = get_term_and_percent("F",enrich_go)
    term_cc,percent_cc = get_term_and_percent("C",enrich_go)
    Term =list(chain(term_bp,term_mf,term_cc))
    percent =list(chain(percent_bp,percent_mf,percent_cc))


    len_max = max([len(term) for term in Term])
    p_max = max(percent)
    width_user = round(len_max/88*11+11)
    height_user = round(len(Term)/30*12+3)
    plt.rcdefaults()
    # plt.rcParams['font.sans-serif'] = 'Helvetica'
    # plt.style.use('seaborn-ticks')
    customer_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=18)
    # plt.rcParams['figure.autolayout'] = True
    plt.rcParams['figure.figsize'] = (width_user, height_user)
    if height_user<6:
        height_user=6

    #todo bp,mf,cc为空的情况???
    fig = plt.figure()
    ax = fig.add_axes([0.88-8.5/width_user,0, 8.5/width_user, 0.98-1/height_user])
    #
    # ax = plt.axes()
    p1 = ax.barh(np.arange(0, len(term_bp)), percent_bp, color="#A52A2A", linestyle="-", edgecolor="black", linewidth=2)
    p2 = ax.barh(np.arange(len(term_bp),len(term_bp)+len(term_mf)), percent_mf, color="#7570B3", linestyle="-", edgecolor="black", linewidth=2)
    p3 = ax.barh(np.arange(len(term_bp)+len(term_mf), len(term_bp)+len(term_mf)+len(term_cc)), percent_cc, color="#D95F02", linestyle="-", edgecolor="black", linewidth=2)


    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.xaxis.set_ticks_position('top')
    ax.spines['top'].set_position(('axes', 0.97))
    ax.set_yticks(np.arange(len(percent)))
    ax.set_yticklabels(Term, fontProperties=customer_font)



    customer_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=24)
    # ax.set_xticks(range(0, int(p_max+1)+1))
    # ax.set_xticklabels(range(0, int(p_max+1)+1), fontProperties=customer_font)
    pylab.xticks(fontProperties=customer_font)

    if not int(p_max)>9:
        ax.set_xticks(range(0, int(p_max+1)+1))
    if not lengend_offset:
        lengend_offset  = (3-(int(p_max+1) - (max(percent_bp[:3])+1)*1.3)/int(p_max+1)*8.5)/8.4 +1

    print(lengend_offset)
    #以上公式  8.5 为条形所占区域为8.5 inch；3 为legends宽度为3 inch；1.2为适当扩大最后三个条形最长值
    customer_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=24) 
    plt.legend([p3, p2, p1], ['Cellular component','Molecular function', "Biological process"], loc='lower right',
               frameon=True, fontsize=18, bbox_to_anchor=(lengend_offset, 0.035), borderaxespad=0.5)
    plt.title("-Log10(P_value)\n", fontProperties=customer_font,fontweight = "bold")
    # plt.xlim(0, round(p_max)+1) # change

    plt.savefig("enrich_go.tif",dpi=150)
    plt.close()

if len(sys.argv)>1:
    a = float(sys.argv[1])
else:
    a = None
_enrich_go_plot(a)











