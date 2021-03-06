#! /usr/bin/env python3
# -*- coding: utf-8 -*-

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


# import sys
# reload(sys)
# sys.setdefaultencoding('gbk')

def extract_info_from_annot(file_name):
    """
    :param file_name: query.annot
    :return: dict
    """
    go_info = dict()
    file = open(file_name,"r")
    for line in file:
        protein = line.strip().split("\t")[0]
        go = line.split("\t")[1]
        go_Category = go[0]
        go_num = go[2:12]
        go_term = go[13:].strip()
        if go_num not in go_info.keys():
            go_info[go_num] = [go_term,go_Category,1,[protein]]
        else:
            go_info[go_num][2] += 1
            go_info[go_num][3].append(protein)

    return go_info


def generate_diff_annot(all_annot_file,diff_txt,group):
    """
    1.generate qury_diff.annot
    :param all_annot_file:
    :param diff_txt:
    :return:
    """
    # all_annot_file = "query_all_0171688.fasta.annot"
    # diff_txt = "diff_223.txt"

    name = [line.split("\t")[0] for line in open(all_annot_file,"r")]
    all_annot = [line for line in open(all_annot_file,"r")]
    f3 = lambda term:term.strip() in name and all_annot[name.index(term.strip()):(name.index(term.strip()) + name.count(term.strip()))]
    diff_annot = [term for term in map(f3,open(diff_txt,"r")) if term]
    open("./GO/{0}/query_diff.annot".format(group),"w").write("".join(list(chain(*diff_annot)))) #chain()将多个list合成一个


def generate_topblast(blast_top_hit,diff_txt, group):
    """
    1.generate topblast.txt
    :param blast_top_hit:
    :param diff_txt:
    :return:
    """

    # blast_top_hit = "blast_top_hit.txt"
    # diff_txt = "diff_223.txt"
    name = [line.split("\t")[0] for line in open(blast_top_hit,"r")]
    all_annot = [line for line in open(blast_top_hit,"r")]
    f3 = lambda term:term.strip() in name and all_annot[name.index(term.strip())]
    diff_annot = [term for term in map(f3,open(diff_txt,"r")) if term]

    f = open("./GO/{0}/topblast.txt".format(group),"w")
    f.write("Sequence Name\tSequence Desc\tSequence Length\tTop Hit Desc\tHit Acc\tE-Value\tSimilarity\tBit-Score\tAlignment\tPositive\n")
    f.write("".join(diff_annot))
    f.close()


def generate_bp_mf_cc(bp_mf_cc_merged,go_level_file, group):
    """
    1.generate bp.txt mf.txt cc.txt
    :param go_info_diff:
    :param go_level_file:
    :return:
    """

    def write_bp_mf_cc(file_name,flag,bp_mf_cc):
        f = open("./GO/{0}/{1}".format(group,file_name),"w")
        f.write("Level\tGO ID\tGO Name\tGO Type\t#Seqs\tSequence Names\n")
        f.write("".join(sorted(filter(lambda line:line.split("\t")[3] ==flag,bp_mf_cc),key=lambda s:float(s.split('\t')[0]))))
        f.close()


    level2 = open("./GO/{0}/Level2.txt".format(group),"w")
    bp_mf_cc_merged = "./GO/{0}/{1}".format(group,bp_mf_cc_merged)
    name = {line.split("\t")[0]: line.split("\t") for line in open(bp_mf_cc_merged, "r")}
    go_level = {line.split("\t")[0]:line.strip().split("\t")[1:] for line in open(go_level_file,"r")}
    f4 = lambda term: "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(go_level[term][2],name[term][0],go_level[term][0],go_level[term][1],name[term][1],name[term][2])
    bp_mf_cc = list(map(f4,name))


    write_bp_mf_cc("BP.txt","P",bp_mf_cc)
    write_bp_mf_cc("MF.txt","F",bp_mf_cc)
    write_bp_mf_cc("CC.txt","C",bp_mf_cc)

    # open("./GO/{0}/bp.txt".format(group),"w").write("".join(sorted(filter(lambda line:line.split("\t")[3] =="P",bp_mf_cc),key=lambda s:float(s.split('\t')[0]))))
    # open("./GO/{0}/mf.txt".format(group),"w").write("".join(sorted(filter(lambda line:line.split("\t")[3] =="F",bp_mf_cc),key=lambda s:float(s.split('\t')[0]))))
    # open("./GO/{0}/cc.txt".format(group),"w").write("".join(sorted(filter(lambda line:line.split("\t")[3] =="C",bp_mf_cc),key=lambda s:float(s.split('\t')[0]))))

    level2.write("".join(sorted(filter(lambda line:line.split("\t")[0] =="2",bp_mf_cc),key=lambda s:s.split('\t')[3])))
    level2.close()


def generate_protein2go(query_diff_annot_file,topblast_file, group):
    """
    1. generate protein2go.txt
    :param query_diff_annot_file:
    :param topblast_file:
    :return:
    """
    topblast_file = "./GO/{0}/{1}".format(group, topblast_file)
    query_diff_annot_file = "./GO/{0}/{1}".format(group, query_diff_annot_file)
    topblast = {line.split("\t")[0]:line.split("\t")[1] for line in islice(open(topblast_file,"r"),1,None)}
    query_diff_annot = [line for line in open(query_diff_annot_file,"r")]
    f5 = lambda line:"{0}\t{1}\t{2}\t{3}\t{4}".format(line.split("\t")[0],topblast[line.split("\t")[0]],line.split("\t")[1][0],line.split("\t")[1][2:12],line.split("\t")[1][13::])
    protein2go = list(map(f5,query_diff_annot))
    f= open("./GO/{0}/protein2go.txt".format(group),"w")
    f.write("SeqName\tHit-Desc\tGO-Group\tGO-ID\tGO-Term\n")
    f.write("".join(protein2go))
    f.close()


def write_info(go_info,outFilename, group=None):
    if group:
        out = open("./GO/{0}/{1}".format(group,outFilename), "w")
    else:
        out = open(outFilename, "w")
    out.write("GO-ID\tTerm\tCategory\tNum\tTestSeqs\n")
    for key in go_info.keys():
        go_info[key][2] = str(go_info[key][2])
        go_info[key][3] = ",".join(go_info[key][3])
        line = "{0}\t{1}\n".format(key, "\t".join(go_info[key]))
        out.write(line)
    out.close()


def get_fasta_len(group_names_all):
    diff_multi = dict()
    for group in group_names_all:
        if group == "all":
            all_total = len(open("./GO/ALL/all.txt", "r").readlines())
        else:
            counts = len(open("./GO/{0}/diff_{0}.txt".format(group), "r").readlines())
            diff_multi[group] = counts
    return diff_multi,all_total

#todo  go富集分析代码修改 ---done
def go_enrich(diff, all_total, group):
    """
    :param diff: the number of diff_protein
    :param all_total: the number of all_protein
    :return: 1
    """

    diff_total = diff[group]
    go_diff = open("./GO/{0}/go_info_diff.txt".format(group), "r")
    enrich = list()

    go_all = open("./GO/ALL/go_info_all.txt", "r")
    map2query_all_list = [line for line in islice(go_all, 1, None)]


    for line in islice(go_diff, 1, None):
        new_line = line.strip().split("\t")
        for line_all in map2query_all_list:
            line_all = line_all.strip().split("\t")

            if new_line[0] == line_all[0]:
                new_line.append(line_all[3])
                enrich.append(new_line)
                break


    p_value_list = list()
    for i in range(len(enrich)):
        map_info = enrich[i]
        diff_in = int(map_info[3])
        all_in = int(map_info[5])
        group_diff = [diff_in, diff_total - diff_in]
        group_no_diff = [all_in - diff_in, all_total - diff_total - (all_in - diff_in)]

        diff = diff_in / diff_total * 100
        ref = all_in / all_total * 100
        try:
            p_value = stats.fisher_exact([group_diff, group_no_diff])[1]
        except:
            print("fisher检验过程中遇到负值，请手动检查，并重新进行富集分析！手动赋予组数据p_value为0.987654321")
            p_value = 0.987654321
        p_value_list.append(p_value)
        if diff > ref:
            over_under = "over"
        else:
            over_under = "under"

        enrich[i].append(str(diff))
        enrich[i].append(str(ref))
        enrich[i].append(str(p_value))
        enrich[i].append(str(over_under))

    fdr_list = multitest.multipletests(p_value_list, method="fdr_bh")[1]
    title = ['GO-ID', 'Term', 'Category', 'FDR', 'P-Value', '#DIFF', '#REF', '%Diff', '%Ref', 'Over/Under', 'TestSeqs']
    enrich_file = open("./GO/{0}/enrich.txt".format(group), "w")
    enrich_file.write('\t'.join(title) + '\n')
    for i in range(len(enrich)):
        line_temp = enrich[i][0:3]+ [str(fdr_list[i]),enrich[i][8], enrich[i][3]] + enrich[i][5:8] + [enrich[i][-1], enrich[i][4]]
        line = "\t".join(line_temp) + "\n"
        enrich_file.write(line)
    enrich_file.close()
    print("执行正常：{0}组GO分析已经完成！".format(group))


def enrich_go_plot(group):
    title = ['GO-ID', 'Term', 'Category', 'FDR', 'P-Value', '#DIFF', '#REF', '%Diff', '%Ref', 'Over/Under', 'TestSeqs']
    enrich_go = open("./GO/{0}/enrich_go.txt".format(group), "w")
    enrich_go.write('\t'.join(title) + '\n')

    def get_term_and_percent(bp_mf_cc,enrich_go):
        term= list()
        percent= list()
        try:
            filtered = filter(lambda line: line.split("\t")[9] == "over" and line.split("\t")[2] == bp_mf_cc and float(
                line.split("\t")[4]) < 0.05, open("./GO/{0}/enrich.txt".format(group), "r"))
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
    ax = fig.add_axes([0.9-8.5/width_user,0, 8.5/width_user, 0.98-1/height_user])
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
    ax.set_xticks(range(0, int(p_max+1)+1))
    ax.set_xticklabels(range(0, int(p_max+1)+1), fontProperties=customer_font)

    lengend_offset  = (3-(int(p_max+1) - max(percent_bp[:3])*1.2)/int(p_max+1)*8.5)/8.4 +1
    #以上公式  8.5 为条形所占区域为8.5 inch；3 为legends宽度为3 inch；1.2为适当扩大最后三个条形最长值

    customer_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=24) 
    plt.legend([p3, p2, p1], ['Cellular component','Molecular function', "Biological process"], loc='lower right',
               frameon=True, fontsize=18, bbox_to_anchor=(lengend_offset, 0.035), borderaxespad=0.5)
    plt.title("-Log10(P_value)\n", fontProperties=customer_font,fontweight = "bold")
    # plt.xlim(0, round(p_max)+1) # change

    plt.savefig("./GO/{0}/enrich_go.png".format(group),dpi=150)
    plt.close()


def go_level2_plot(group,diff_multi):
    diff_num = diff_multi[group]
    level2 = open("./GO/{0}/Level2.txt".format(group), "r")

    go_name = list()
    nums = list()
    percent = list()
    bp_mf_cc = list()


    for line in level2:
        line = line.strip().split("\t")
        go_name.append(line[2])
        bp_mf_cc.append(line[3])
        nums.append(int(line[4]))
        percent.append(int(line[4])/diff_num)
    plt.rcdefaults()
    # plt.rcParams['font.sans-serif'] = 'Helvetica'
    # plt.style.use('seaborn-ticks')
    cutom_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf", size=18)
    # plt.rcParams['figure.autolayout'] = True

    width = round(len(go_name)/60*14+9)
    if width<12:
        width=12
    height = round((max([len(term) for term in go_name]))/50*6+5)
    plt.rcParams['figure.figsize'] = (width, height)

    fig = plt.figure()
    ax = fig.add_axes([1/width,0.93-4.5/height, 0.95-1/width, 4.2/height])

    mf_num = bp_mf_cc.index('F')
    bp_num = bp_mf_cc.index('P')
    p1 = ax.bar(np.arange(len(bp_mf_cc)-mf_num,len(bp_mf_cc)), nums[0:mf_num], color="#A52A2A", linestyle="-", edgecolor="black", linewidth=2)
    p2 = ax.bar(np.arange(len(bp_mf_cc)-bp_num,len(bp_mf_cc)-mf_num), nums[mf_num:bp_num], color="#7570B3", linestyle="-", edgecolor="black", linewidth=2)
    p3 = ax.bar(np.arange(0, len(bp_mf_cc)-bp_num), nums[bp_num:], color="#D95F02", linestyle="-", edgecolor="black", linewidth=2)


    plt.tick_params(labelsize=16)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['bottom'].set_position(('axes', 0.0))
    ax.spines['left'].set_position(('axes', 0.03))
    # ax.get_xaxis().set_visible(False)
    ax.set_xticks(np.arange(len(go_name)))
    go_name = go_name[bp_num:]+go_name[mf_num:bp_num]+go_name[:mf_num]
    cutom_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf", size=14)
    ax.set_xticklabels(go_name, fontProperties=cutom_font)
    cutom_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf", size=18)
    ax.set_ylabel("\nThe number of proteins", fontProperties=cutom_font)
    ax.set_ylim([0,diff_num])
    ax.set_ybound(upper=diff_num)
    ax.minorticks_on()


    ax2 = ax.twinx()
    ax2.tick_params(labelsize=16)
    ax2.spines['top'].set_color('none')
    ax2.spines['left'].set_color('none')
    ax2.spines['bottom'].set_color('none')
    ax2.spines['right'].set_position(('axes', 0.97))
    ax2.set_ylim([0, 100])
    ax2.set_ylabel("Percentage of Proteins(%)\n", fontProperties=cutom_font)
    ax2.minorticks_off()


    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=90, horizontalalignment='center')
    # plt.legend([p3, p2, p1], ['Molecular function', 'Cellular component', "Biological process"], fontsize=16,
    #            bbox_to_anchor=(0.7, 1.1), ncol=3)
    plt.legend([p3, p2, p1], [ "Biological process",'Molecular function', 'Cellular component'], fontsize=16,loc= 9,bbox_to_anchor=(0.5, 1.2), ncol=3)
    plt.title("fadfadf\n afdadfafda\nsdsd",fontsize=16,color="white")   # 利用title占位，避免legend没有位置显示

    # plt.tight_layout()

    plt.savefig("./GO/{0}/GO_Level2.png".format(group),dpi=150)
    plt.close()

# todo 从EXCEL中提取信息---done
# todo 区分itraq和lable free
def get_protein_from_xlsx():
    """
    Get diff/all proteins info form excel files.
    Write down the "protein_all.txt" and "protein_diff_group.txt"
    """
    # todo 文件夹建立
    # todo 文件拷贝

    # todo excel信息提取 ---done
    # todo 文件检查

    workbook = xlrd.open_workbook(u'附件1_蛋白质鉴定列表.xlsx')
    table = workbook.sheets()[0]
    protein_all = table.col_values(0)

    workbook = xlrd.open_workbook(u'附件3_蛋白质定量和差异分析列表.xlsx')
    sheet_names = workbook.sheet_names()  # 查看sheet name  # 确定分组信息
    group_names = [name.replace(" ", "_") for name in sheet_names]
    if not os.path.exists("GO"):
        os.makedirs("GO")
        os.makedirs("GO/ALL")
        for group in group_names:
            os.makedirs("./GO/{0}".format(group))

    protein_diffs_name_list = list()
    for sheet_name in sheet_names:
        worksheet = workbook.sheet_by_name(sheet_name)
        # protein_diffs_list.append(worksheet.col_values(0))
        protein_ids_raw = worksheet.col_values(0)
        protein_fcs = worksheet.col_values(-2)
        protein_P_values = worksheet.col_values(-1)
        protein_col_names = worksheet.row_values(0)
        sample_index_list = list()
        sample_name_list = list()
        group_name = sheet_name.split(" ")
        group_name.remove(group_name[1])
        for name in protein_col_names:
            if "Abundances {0}".format(group_name[0]) in name or "Abundances {0}".format(group_name[1])in name:
                sample_name_list.append(name.replace("Abundances ",""))
                sample_index_list.append(protein_col_names.index(name))

        protein_diff = list()
        diff_proteins_signal =list()
        for i in range(1,len(protein_ids_raw)):
            # print(protein_P_values[i])
            protein_signal = list()
            if (float(protein_P_values[i])<0.05 and (float(protein_fcs[i])>=1.2 or float(protein_fcs[i])<=0.833333)):
                protein_diff.append(protein_ids_raw[i])  # 获取差异蛋白的名称
                protein_signal.append(protein_ids_raw[i])
                for index in sample_index_list:
                    protein_signal.append(str(worksheet.cell_value(i, index)))
            if protein_signal:
                diff_proteins_signal.append(protein_signal)
        protein_diffs_name_list.append(protein_diff)

        cluster = open("./GO/{0}/cluster_diff_{0}.txt".format(sheet_name.replace(" ", "_"),),"w")
        cluster.write('Gene Symbol\t{0}\n'.format("\t".join(sample_name_list)))
        for line in diff_proteins_signal:
            cluster.write("{0}\n".format("\t".join(line)))
        cluster.close()



    protein_diffs_dict = dict(zip(group_names,protein_diffs_name_list))

    # TODO protein ID文件生成  ---done
    open("./GO/ALL/protein_all.txt", "w").write("\n".join(protein_all[1:]))
    for name in protein_diffs_dict:
        open("./GO/{0}/protein_diff_{0}.txt".format(name), "w").write("\n".join(protein_diffs_dict[name]))
    return group_names


#todo 从uniprot数据库查询并下载fasta  ---done
def with_uniprot(group_names):
    """
    Write down the raw fasta file :"query_all_raw.fasta" or "query_diff_[group]_raw.fasta";
    Write down the cleaned fasta file :"query_all.fasta" or "query_diff_[group].fasta";
    Write down the cleaned fasta file :"all.txt" or "diff_[group].txt";
    :param group_names:
    :return:
    """
    for group in group_names:

        if group == "all":
            file_name = "./GO/ALL/protein_all.txt"
        else:
            file_name = "./GO/{0}/protein_diff_{0}.txt".format(group)

        print("正在处理比较组{0}".format(group))
        net_flag = True
        if os.path.exists("./GO/{0}/diff_{0}_raw.fasta".format(group)):
            break
        while net_flag:
            try:
                # 打开网站
                options = webdriver.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")
                driver=webdriver.Chrome(executable_path="/home/fdong/auto_protein_analysis/chromedriver",chrome_options=options)


                # driver = webdriver.Chrome()
                driver.get("https://www.uniprot.org/uploadlists/")

                # 上传文件 并提交
                upload = driver.find_element_by_xpath('//*[@id="uploadfile"]')
                file_upload = os.path.join(os.getcwd(),file_name)
                upload.send_keys(file_upload)
                upload.submit()
                time.sleep(5)

                # "protein_diff_{0}.txt"
                raw_fasta_file = file_name.replace("protein_","")
                raw_fasta_file = raw_fasta_file.replace(".txt","_raw.fasta")
                if "yourlist" in driver.current_url:
                    yourlist = re.findall(r"query=yourlist:(.*?)&",driver.current_url)[0]
                    download_url = "https://www.uniprot.org/uniprot/?query=yourlist:{0}&format=fasta&force=true&cols=yourlist({0}),id,entry%20name,reviewed,protein%20names,genes,organism,length&sort=yourlist:{0}".format(yourlist)
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"}

                    req = requests.get(download_url, headers=headers, timeout=600)
                    if len(req.content) > 1:
                        with open(raw_fasta_file, "wb") as f:
                            f.write(req.content)
                        f.close()
                driver.quit()
                net_flag = False
            except:
                driver.quit()
                print("{0}分组uniprot网页处理异常！".format(group))
                net_flag = True


        fasta_raw = open(raw_fasta_file,"r")
        fasta2txt = open(raw_fasta_file.replace("_raw.fasta", ".txt"), "w")
        raw_fasta_file = raw_fasta_file.replace("_raw", "")
        if "diff" in raw_fasta_file:
            fasta_clean = open(raw_fasta_file.replace("diff","query_diff"),"w")
        elif "all" in raw_fasta_file:
            fasta_clean = open(raw_fasta_file.replace("all", "query_all"), "w")

        for line in fasta_raw:
            if ">" in line:
                line = ">{0}\n".format(re.findall(r">(?:tr|sp)\|(.+)\|",line)[0])
                fasta2txt.write(line[1:])
                fasta_clean.write(line)
            else:
                fasta_clean.write(line)
        fasta_raw.close()
        fasta_clean.close()
        fasta2txt.close()
        if "all" != group:
            query2kegg = "query_diff_{0}.fasta".format(group).replace("_VS_","")
            shutil.copy("./GO/{0}/query_diff_{0}.fasta".format(group), "./GO/{0}".format(query2kegg))
        else:
            shutil.copy("./GO/ALL/query_all.fasta","./GO")


def processing_fasta_file(filename):

    """
    This function has been canceled!!!!!
    1.generate diff.txt
    2.generate query_diff/all.fasta
    :param filename: raw fasta file ,which is download form uniprot databases
    :return:
    """
    #生成diff.txt
    f1= lambda line: ">" in line and re.findall(r"\|(.*)\|",line)[0]
    protein_id = [term for term in map(f1,open(filename,"r")) if term]
    open("diff_{0}.txt".format(len(protein_id)),"w").write("\n".join(protein_id))

    #生成query_diff/all.fasta
    f2 = lambda line: (">" in line and ">" + re.findall(r"\|(.*)\|",line)[0]) or line.strip()
    query = [line for line in map(f2,open(filename,"r"))]
    open("query_{}.txt".format("all"),"w").write("\n".join(query))


def go_level_merge(go_info_diff,group):

    go_info_diff = "./GO/{0}/{1}".format(group, go_info_diff)

    go_tree_down2up = eval(open("/home/fdong/auto_protein_analysis/go_obo_data/go_tree_down2up.txt","r").read())
    go_tree_up2down = eval(open("/home/fdong/auto_protein_analysis/go_obo_data/go_tree_up2down.txt","r").read())

    def parsed_up2down(go, go_tree_up2down):
        child_go = set()
        while go:
            go_temp = set()
            if type(go) == str:
                go = [go]
            for go_term in go:
                try:
                    go_temp.update(go_tree_up2down[go_term])
                except KeyError:
                    pass
            go = set(go_temp)
            child_go.update(go)
        return child_go


    def parsed_down2up(go, go_tree_down2up):
        parent_go = set()
        while go:
            go_temp = set()
            if type(go) == str:
                go = [go]
            for go_term in go:
                try:
                    go_temp.update(go_tree_down2up[go_term])
                except KeyError:
                    pass
            go = set(go_temp)
            parent_go.update(go)
        return parent_go


    go_protein_dict = dict()
    for line in islice(open(go_info_diff, "r"), 1, None):
        line = line.split("\t")
        go_protein_dict[line[0]] = set(line[-1].strip().split(","))

    for go in list(go_protein_dict.keys()):
        child_go = parsed_up2down(go, go_tree_up2down)
        for child in child_go:
            if child in go_protein_dict:
                go_protein_dict[go].update(go_protein_dict[child])   # 将其子节点的蛋白加到当前节点中

        parent_go = parsed_down2up(go, go_tree_down2up)
        for parent in parent_go:
            if parent in go_protein_dict:
                go_protein_dict[parent].update(go_protein_dict[go])   #父节点存在时，将当前节点的蛋白更新到父节点中
            else:
                go_protein_dict[parent] = go_protein_dict[go]        #父节点存在时，添加父节点

    bp_mf_cc_merged = open("./GO/{0}/bp_mf_cc_merged.txt".format(group),"w")

    for go in go_protein_dict:
        protein = go_protein_dict[go]
        line = "{0}\t{1}\t{2}\n".format(go,str(len(protein)),",".join(protein))
        bp_mf_cc_merged.write(line)
    bp_mf_cc_merged.close()


def txt2excel(group):
    path = "./GO/{0}/".format(group)
    command = "perl /home/fdong/auto_protein_analysis/TXToXLSX.pl {0}GO.xlsx {0}topblast.txt {0}protein2go.txt {0}BP.txt {0}MF.txt {0}CC.txt {0}enrich.txt".format(
        path)
    os.system(command)


def hcluster2(group):


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
        df.to_csv("./GO/{0}/cluster_data.txt".format(group))
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

        fig.savefig("./GO/{0}/cluster_heatmap.png".format(group),dpi=150)

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

        fig.savefig("./GO/{0}/cluster_heatmap_small.png".format(group),dpi=150)


    newcmp = get_new_colormap()
    file = "./GO/{0}/cluster_diff_{0}.txt".format(group)
    plot_cluster_heatmap_detail(file)
    plot_cluster_heatmap_small(file)


def main_process():
    group_names = get_protein_from_xlsx()
    group_names_all = list(group_names)
    group_names_all.append("all")
    with_uniprot(group_names_all)


    diff_multi, all_total = get_fasta_len(group_names_all)
    print(diff_multi)
    print(all_total)
    # todo 衔接kegg_mapper_parse.py   #移动文件至KEGG文件夹
    # todo 衔接blast2go命令
    # all_annot_file = "来自blast2go命令结果"
    for file in os.listdir():
        if "query_all" in file and file[-5:]=="annot":
            all_annot_file = file
        # else:
        #    print("query_diff_annot_file不存在!!!") 
    #all_annot_file = "query_all_3422.fasta.annot"
    # blast_top_hit = "blast2go命令结果"
    if os.path.exists("blast_top_hit.txt"):
        blast_top_hit = "blast_top_hit.txt"
    else:
        print("blast_top_hit文件不存在!!")
    
    # go_level_file = "来自go_level_parse.py命令结果"
    go_level_file = "/home/fdong/auto_protein_analysis/go_obo_data/level_file_detail.txt"
    #  todo 为每个分组建立文件夹，在每个文件夹中生成文件

    go_info_all = extract_info_from_annot(all_annot_file)
    write_info(go_info_all, "./GO/ALL/go_info_all.txt")


    for group in group_names:
        diff_txt = "./GO/{0}/diff_{0}.txt".format(group)
        generate_diff_annot(all_annot_file, diff_txt, group)
        go_info_diff = extract_info_from_annot("./GO/{0}/query_diff.annot".format(group))
        write_info(go_info_diff, "go_info_diff.txt",group)
        # write_info(go_info_diff, "query_diff.annot", group)
        generate_topblast(blast_top_hit, diff_txt, group)
        go_level_merge("go_info_diff.txt", group)
        generate_bp_mf_cc("bp_mf_cc_merged.txt", go_level_file, group)
        generate_protein2go("query_diff.annot", "topblast.txt", group)
        go_enrich(diff_multi,all_total,group)
        enrich_go_plot(group)
        go_level2_plot(group, diff_multi)
        txt2excel(group)
        # hcluster2(group)


if __name__ == "__main__":
    start = time.time()
    main_process()
    end = time.time()
    m, s = divmod(end - start, 60)  # 转换时间的方法
    h, m = divmod(m, 60)
    print('任务完成，共耗时%02d小时%02d分%02d秒' % (h, m, s))


# todo go链、go低层次protein向上合并 ---done
# todo label-free项目处理
# todo 物种确定
# todo KEGG部分画图----done
# todo 聚类分析   ---DONE

