#!/usr/bin/env python
# coding=utf-8
from itertools import islice
from scipy import stats
from statsmodels.stats import multitest
from itertools import chain
import os
import re
from selenium import webdriver
import requests
import time
from matplotlib.font_manager import FontProperties
import math
import pylab
import scipy.cluster.hierarchy as sch
import seaborn as sns
import pandas as pd
from seaborn import matrix
import matplotlib.pyplot as plt
import shutil
import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap


def hcluster2():
    def get_new_colormap():

        # coolwarm111 = cm.get_cmap('coolwarm', 256)
        # bwr111 = cm.get_cmap('bwr', 256)
        # coolwarm111 = coolwarm111(np.linspace(0, 1, 256))
        # bwr111 = bwr111(np.linspace(0, 1, 256))
        # pink = bwr111[114:143, :]
        # coolwarm111[114:143, :] = bwr111[114:143, :]
        # newcmp = ListedColormap(coolwarm111)

        # ss = cm.get_cmap('coolwarm', 100)
        # 41, 117, 232
        # 26, 107, 230
        # 24, 100, 215
        N = 256
        vals = np.ones((N, 4))
        vals[:, 0] = np.linspace(24/255, 1, N)
        vals[:, 1] = np.linspace(100/255, 1, N)
        vals[:, 2] = np.linspace(215/255, 1, N)
        newcmp1 = ListedColormap(vals)

        # ss = cm.get_cmap('coolwarm', 100)
        # 244, 126, 96
        # 206, 53, 15

        N = 256
        vals = np.ones((N, 4))
        vals[:, 0] = np.linspace(206/255, 1, N)
        vals[:, 1] = np.linspace(53/255, 1, N)
        vals[:, 2] = np.linspace(15/255, 1, N)
        newcmp2 = ListedColormap(vals)
        top = cm.get_cmap(newcmp2,100)
        bottom = cm.get_cmap(newcmp1.reversed(), 100)

        newcolors = np.vstack((top(np.linspace(0, 1, 50))[:48,:],
                               bottom(np.linspace(0, 1, 50))[2:,:]))
        newcmp = ListedColormap(newcolors, name='OrangeBlue').reversed()
        return newcmp
        # newcmp = "seismic"

    def plot_cluster_heatmap_detail(file):

        df = pd.read_table(file, header=0, index_col=0)
        df = matrix.ClusterGrid(df).format_data(df, None, z_score=0)
        df.to_csv("cluster_data.txt",sep="\t")
        col_name_length_max = max([len(name) for name in df.columns])
        row_name_length_max = max([len(name) for name in df.index])+2
        rows,cols = df.shape
        # fig = plt.figure(figsize=[6,2.5])   10
        # fig = plt.figure(figsize=[13,25])   100
        pic_width = 11+row_name_length_max*20/150
        pic_height = 4+0.2*rows
        # x_start = 2.5/pic_width
        # plot_width = 8.5/pic_width
        fig = plt.figure(figsize=[pic_width, pic_height])

        # Compute and plot col dendrogram.
        ax1 = fig.add_axes([2.5/pic_width, 1-2.5/pic_height, 8.5/pic_width, 2.5/pic_height])
        col_link = sch.linkage(df.T, method='average')
        z1 = sch.dendrogram(col_link, orientation='top', color_threshold=0, above_threshold_color="black",ax=ax1)
        col_name = df.columns[z1["leaves"]]
        ax1.set_axis_off()

        # Compute and plot row dendrogram.
        ax2 = fig.add_axes([0.0, 1.5/pic_height, 2.5/pic_width, 0.2*rows/pic_height])
        row_link = sch.linkage(df, method='average')
        z2 = sch.dendrogram(row_link,orientation='left',color_threshold=0,above_threshold_color="black",ax=ax2)
        row_name = df.index[z2["leaves"]]
        ax2.set_axis_off()
        cluster_data_list = open("cluster_data_list.txt","w")
        for i in list(row_name):
            cluster_data_list.write("{0}\n".format(i))
        cluster_data_list.close()

        # Compute and plot heatmap.
        heatmap_data = df.values[z2["leaves"], :][:, z1["leaves"]]
        ax3 = fig.add_axes([2.5/pic_width, 1.5/pic_height, 8.5/pic_width, 0.2*rows/pic_height])
        mesh = ax3.pcolormesh(heatmap_data, cmap=newcmp,vmin=-2, vmax=2)
        sns.heatmap(heatmap_data,ax=ax3,cbar=None, linewidths=0.01, cmap=newcmp,yticklabels=False,xticklabels=False)
        # set yaxis
        ax3.set_yticks(np.arange(len(row_name))+0.5)
        ax3.set_yticklabels(row_name, minor=False)
        ax3.yaxis.set_label_position('right')
        ax3.yaxis.tick_right()
        pylab.yticks( fontsize=12)
        # set_yaxis
        ax3.set_xticks(np.arange(len(col_name))+0.5)
        ax3.set_xticklabels(col_name, minor=False, rotation=90)
        ax3.xaxis.set_label_position('bottom')
        ax3.xaxis.tick_bottom()
        pylab.xticks(fontsize=16)

        # plot colorbar
        ax4 = fig.add_axes([2.5/pic_width/4, 1-2.5/pic_height,2.5/pic_width/4, 2.4/pic_height])
        cb = fig.colorbar(mesh,ax=ax3,cax=ax4, orientation="vertical")
        # ax4 = fig.add_axes([0.01, 1-1/pic_height,0.25, 0.05])
        # cb = fig.colorbar(mesh,ax=ax3,cax=ax4, orientation="horizontal")
        cb.outline.set_linewidth(0)

        fig.savefig("cluster_heatmap.png",dpi=150)

    def plot_cluster_heatmap_small(file):
        df = pd.read_table(file, header=0, index_col=0)
        df = matrix.ClusterGrid(df).format_data(df, None, z_score=0)
        rows, cols = df.shape
        pic_width = 4
        if rows>=50:
            pic_height = 4
        elif rows<=15:
            pic_height = 2
        else:
            pic_height = 3

        fig = plt.figure(figsize=[pic_width, pic_height])


        ax1 = fig.add_axes([0.02, 0.9, 0.8, 0.1])
        col_link = sch.linkage(df.T, method='average')
        z1 = sch.dendrogram(col_link, orientation='top', color_threshold=0, above_threshold_color="black", ax=ax1)
        col_name = df.columns[z1["leaves"]]
        ax1.set_axis_off()

        #
        ax2 = fig.add_axes([0.5, 0.5, 0.0001, 0.0001])
        row_link = sch.linkage(df, method='average')
        z2 = sch.dendrogram(row_link, orientation='left', color_threshold=0, above_threshold_color="black", ax=ax2)
        ax2.set_axis_off()
        
        xlabel_len_max = max([len(name) for name in col_name])+3
        heatmap_data = df.values[z2["leaves"], :][:, z1["leaves"]]
        ax3 = fig.add_axes([0.02,xlabel_len_max*0.025, 0.8, 0.9-xlabel_len_max*0.025])
        mesh = ax3.pcolormesh(heatmap_data, cmap=newcmp,vmin=-2, vmax=2)
        # sns.heatmap(heatmap_data,ax=ax3,cbar=None, linewidths=0.01, cmap=newcmp,yticklabels=False,xticklabels=False)
        sns.heatmap(heatmap_data, ax=ax3, cbar=None, linewidths=0, cmap=newcmp, yticklabels=False, xticklabels=False)

        ax3.set_xticks(np.arange(len(col_name)) + 0.5)
        ax3.set_xticklabels(col_name, minor=False, rotation=90)
        ax3.xaxis.set_label_position('bottom')
        ax3.xaxis.tick_bottom()
        pylab.xticks(fontsize=6)

        ax4 = fig.add_axes([0.85,xlabel_len_max*0.025,0.06,(0.9-xlabel_len_max*0.025)/2])
        cb = fig.colorbar(mesh,ax=ax3,cax=ax4,orientation="vertical")
        cb.outline.set_linewidth(0)
        pylab.yticks(fontsize=6)

        fig.savefig("cluster_heatmap_small.png",dpi=150)


    newcmp = get_new_colormap()
    file = "cluster_diff.txt"
    plot_cluster_heatmap_detail(file)
    plot_cluster_heatmap_small(file)




hcluster2()

