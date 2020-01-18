#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import multiprocessing
from itertools import islice
from scipy import stats
from statsmodels.stats import multitest
from itertools import chain
import xlrd
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
from kegg_mapper_parse import main_func
from go_enrich import main_process
from go_enrich import init_processes
import sys

# reload(sys)
# sys.setdefaultencoding('gbk')
def get_taxid():
    taxid = u'9606'
    confirm = "N"
    while confirm.upper() == "N":
        reset = input("\n默认物种编号为：9606，是否修改物种编号【Y/N】：")
        if reset.upper() == "Y":
            taxid = input("请输入物种编号：")
            print("输入物种编号如下：{0}".format(taxid))
            confirm = input("请确定输入信息是否正确[Y/N]:").strip()
            if confirm not in "ynYN":
                print("确认输入有误，请重新输入！")
                confirm = "n"
        elif reset.upper() == "N":
            taxid = u'9606'
            break
    print("当前物种编号：{0}".format(taxid))
    return taxid

def input_email():
    print(
        "备用邮箱列表(密码都为zmail1234):\nzmail_test@126.com\nzmail_test1@126.com\nzmail_test2@126.com\nzmail_test3@126.com\nzmail_test4@126.com\nzmail_test5@126.com\nzmail_test6@126.com\n")
    email_temp = 'zmail_test6@126.com'
    email_password_temp = "zmail1234"
    confirm = "N"
    while confirm[0].upper() == 'N':
        reset_email = input("默认邮箱：zmail_test6@126.com；密码：zmail1234\n是否修改邮箱[Y/N]:")
        if reset_email.upper() == "Y":
            email = input("请输入新邮箱：").strip()
            email_password = input("请输入邮箱密码:").strip()
            print("输入邮箱信息如下：\n邮箱：{0}\n密码：{1}".format(email, email_password))
            confirm = input("请确定输入信息是否正确[Y/N]\t恢复默认邮箱请输入【R】: ").strip()
            if confirm.upper() not in "YNynRr":
                print("\n确认信息有误，请重新输入")
                confirm = "n"
            if confirm.upper() == "R":
                email = email_temp
                email_password = email_password_temp
                break
        elif reset_email.upper() == "N":
            email = email_temp
            email_password = email_password_temp
            break
    print("正在使用的邮箱：{0}\t密码：{1}\n如果邮箱有误请结束程序，重新运行！".format(email, email_password))
    return (email, email_password)



def run_blast2go_cli(taxid,group_names):

    print(">"*30+"运行blast2go_shell脚本"+"<"*30)
    print("工作路径:【{0}】".format(os.getcwd()))
    print("Annotation文件路径:【{0}】".format("/project/" + os.getcwd().split("/")[-1]))
    fasta_file_name = "GO/query_all.fasta"
    raw_path = os.getcwd()
    fasta_file_name = os.path.join(os.getcwd(),fasta_file_name)
    print(fasta_file_name)
    annot_file_dir = os.getcwd().split("/")[-1]
    print(annot_file_dir)
    cli_path = "/genechem/program/blast2go_cli_v1.4.4" #"/home/lijuan.chen/blast2go_commandline/blast2go_cli_v1.3.3"
    os.chdir(cli_path)
    #print(os.getcwd())
    command = "bash blast2go_shell.sh {0} uniprot-reviewed%3Ayes+taxonomy%3A{1}.fasta {2}".format(fasta_file_name, taxid, annot_file_dir)
    os.system(command)
    os.chdir(raw_path)
    cli_path = "/project" #"/home/lijuan.chen/blast2go_commandline/blast2go_cli_v1.3.3"
    annot_file_dir = os.getcwd().split("/")[-1]
    all_annot_file = cli_path + "/"  +  annot_file_dir + "/" + "query_all.fasta.annot"
# blast_top_hit = "blast2go命令结果"
    blast_top_hit = cli_path + "/"  +  annot_file_dir + "/" + "blast_top_hit.txt"
# go_level_file = "来自go_level_parse.py命令结果"
    go_level_file = "/home/fdong/auto_protein_analysis/go_obo_data/level_file_detail.txt"
# todo 为每个分组建立文件夹，在每个文件夹中生成文件

    main_process(group_names, all_annot_file, blast_top_hit, go_level_file)

    # return(annot_file_dir)
    
    
    
if __name__ == "__main__":
    start = time.time()
    
    email_info = input_email()
    taxid = get_taxid()
    map_download_flag = None
    if len(sys.argv)==2 and sys.argv[1]=="m":
        map_download_flag = True
 

    group_names = init_processes()
    for i in range(2):
        if i==0:
            p = multiprocessing.Process(target=run_blast2go_cli,args=(taxid,group_names))
            p.start()
        else:
            p2 = multiprocessing.Process(target=main_func,args=(taxid,email_info,map_download_flag))
            p2.start()
    
    
    end = time.time()
    m, s = divmod(end - start, 60)  # 转换时间的方法
    h, m = divmod(m, 60)
    print('main任务完成，共耗时%02d小时%02d分%02d秒' % (h, m, s))



