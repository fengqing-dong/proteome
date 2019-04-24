
import time
import os
from scipy import stats
from statsmodels.stats import multitest
from itertools import islice
import numpy as np
import math

def kegg_enrich(diff_total,all_total,diff_file,all_file):
    # print(diff_total)
    diff_total = float(diff_total)
    all_total = float(all_total)
#    for diff_or_all in diff_multi.keys():
#        diff_total = diff_multi[diff_or_all]
#        diff_group = diff_or_all.strip().split("_")[1]
#

        #todo 进入多分组的子文件夹后富集分析  ---done

#    map2query_diff = open("./KEGG_diff/{1}/map2query_{0}.txt".format(diff_or_all, diff_group), "r")
    map2query_diff = open(diff_file,"r")
    enrich = list()
    for line in islice(map2query_diff, 1, None):
        line = line.strip().split("\t")
        new_line = line[:4]

#        map2query_all = open("./KEGG_all/map2query_all.txt", "r")
        map2query_all = open(all_file,"r")
        for line_all in islice(map2query_all, 1, None):
            line_all = line_all.strip().split("\t")
            if line[0] == line_all[0]:
                new_line.append(line_all[3])
                enrich.append(new_line)
                map2query_all.close()
                break

    p_value_list = list()
    for i in range(len(enrich)):
        map_info = enrich[i]
        diff_in = int(map_info[3])
        all_in = int(map_info[4])
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
    title = ['ID', 'Name', '#DIFF', '#REF', '%Diff', '%Ref', 'P_Value', 'FDR', 'over_under', 'DiffSeqs']
#    enrich_filename = "./KEGG_diff/{1}/enrich_end_{0}.txt".format(diff_or_all, diff_group)
    rich_file = open("enrich.txt", "w")

    rich_file.write('\t'.join(title) + '\n')
       

    for i in range(len(enrich)):
        line_temp = enrich[i][0:2] + enrich[i][3:8] + [str(fdr_list[i])] + [enrich[i][8]] + [enrich[i][2]]
        line = "\t".join(line_temp) + "\n"
        rich_file.write(line)

    rich_file.close()

    ### todo 测试以下代码 ---done 正常
#    enrich_kegg = open("./KEGG_diff/{0}/enrich_kegg.txt".format(diff_group), "w")
#    enrich_kegg.write('\t'.join(title) + '\n')
#    enrich_kegg.write(''.join(sorted(filter(lambda line: line.split("\t")[8] == "over" and float(line.split("\t")[6]) < 0.05, open(enrich_filename, "r")),key=lambda s: float(s.split("\t")[6]))[:10]))
#    enrich_kegg.close()
    print("执行正常：富集分析已经完成！")


if __name__ =="__main__":
    import sys
    diff_num = sys.argv[1]
    all_num = sys.argv[2]
    diff_file = sys.argv[3]
    all_file = sys.argv[4]
    kegg_enrich(diff_num,all_num,diff_file,all_file)    





























