#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
# from itertools import product
import requests
import gzip
import time

def get_go_obo_lastest():
    def un_gz(file_name):
        """ungz zip file"""
        f_name = file_name.replace(".gz", "")
        #获取文件的名称，去掉
        g_file = gzip.GzipFile(file_name)
        #创建gzip对象
        open(f_name, "wb").write(g_file.read())
        #gzip对象用read()打开后，写入open()建立的文件中。
        g_file.close()
        #关闭gzip对象

    # http://data.biobam.com/b2g_res/obo_files/    #GO_OBO文件下载链接
    req = requests.get("http://data.biobam.com/b2g_res/obo_files/go_latest.obo.gz")
    with open("/home/fdong/auto_protein_analysis/go_obo_data/go_lastest.obo.gz", "wb") as f:
        f.write(req.content)
    f.close()

    un_gz("/home/fdong/auto_protein_analysis/go_obo_data/go_lastest.obo.gz")


def parse_go_obo():
    print("正在解析go.obo文件......")
    go_name_list = list()
    go_info_list = list()

    term_pattern = re.compile(r"^\[Term\]")
    Typedef_pattern = re.compile(r"^\[Typedef\]")
    id_pattern = re.compile(r"^id: (GO:\d*)")
    name_pattern = re.compile(r"^name: (.*)")
    namespace_pattern = re.compile(r"^namespace: (.*)")

    is_a_pattern = re.compile(r"^is_a: (GO:\d*)")    #list
    alt_id_pattern = re.compile(r"^alt_id: (GO:\d*)")    #list

    is_absolete_pattern = re.compile(r"^is_obsolete: (true)")
    replace_by_pattern = re.compile(r"^replaced_by: (GO:\d*)")

    consider_pattern = re.compile(r"^consider: (GO:\d*)") #list
    relationship_pattern = re.compile(r"relationship: (.*) (GO:\d*) !") #list


    next_flag = False

    # with open("test_go.txt","r") as f:
    with open("/home/fdong/auto_protein_analysis/go_obo_data/go_lastest.obo","r") as f:
        for line in f:
            line = line.strip()
            if re.findall(Typedef_pattern,line):
                break
            if re.findall(term_pattern,line):
                if next_flag:
                    go_info_temp = [id,name,namespace,alt_id,is_a,is_absolete,replace_by,consider,relationship]
                    go_info_list.append(go_info_temp)
                next_flag = True
                is_a = list()
                consider = list()
                relationship = list()
                alt_id = list()
                is_absolete = False
                replace_by = None
            elif re.findall(id_pattern,line):
                id = re.findall(id_pattern,line)[0]
                go_name_list.append(id)
            elif re.findall(name_pattern,line):
                name = re.findall(name_pattern,line)[0]
            elif re.findall(namespace_pattern,line):
                namespace = re.findall(namespace_pattern,line)[0]
                if namespace=="cellular_component":
                    namespace = "C"
                elif namespace=="biological_process":
                    namespace = "P"
                elif namespace=="molecular_function":
                    namespace = "F"
            elif re.findall(is_a_pattern,line):
                is_a.append(re.findall(is_a_pattern,line)[0])
            elif re.findall(alt_id_pattern,line):
                alt_id.append(re.findall(alt_id_pattern,line)[0])
            elif re.findall(is_absolete_pattern,line):
                is_absolete = True
            elif re.findall(replace_by_pattern,line):
                replace_by = re.findall(replace_by_pattern,line)[0]
            elif re.findall(consider_pattern,line):
                consider.append(re.findall(consider_pattern,line)[0])
            elif re.findall(relationship_pattern,line):
                relationship.append(re.findall(relationship_pattern,line)[0])

    go_info_temp = [id, name, namespace, alt_id, is_a, is_absolete, replace_by, consider, relationship]
    go_info_list.append(go_info_temp)
    return go_name_list,go_info_list


def get_is_a_index(go_name_list,go_info_list):
    print("正在获取is_a关系......")
    is_a_index = dict()
    for go_info in go_info_list:
        if go_info[4]:
            for go in go_info[4]:
                if go not in is_a_index:
                    is_a_index[go] = {go_name_list.index(go_info[0])}
                else:
                    is_a_index[go].add(go_name_list.index(go_info[0]))
    return is_a_index


def generating_go_level_confirm(is_a_index,go_name_list,go_info_list):  #多重细节调整和完善
    print("正在生成go_level文件......")

    # id: GO:0005575
    # name: cellular_component   cell
    # namespace: cellular_component
    # alt_id: GO:0008372
    #
    # id: GO:0008150
    # name: biological_process
    # namespace: biological_process
    # alt_id: GO:0000004
    # alt_id: GO:0007582
    # alt_id: GO:0044699
    #
    # id: GO:0003674
    # name: molecular_function
    # namespace: molecular_function
    # alt_id: GO:0005554
    # print("is_a_index:",len(is_a_index))
    # for key in is_a_index:
    #     print(key,"\t",is_a_index[key])
    level_dict = {"GO:0005575":"cellular_component", "GO:0008150":"biological_process", "GO:0003674":"molecular_function"}
    level = 1
    # go_level = list(go_name_list)
    go_info_list_change = list(go_info_list)
    for go in level_dict:
        go_info_list_change.remove(go_info_list[go_name_list.index(go)])
    level_file_detail = open("/home/fdong/auto_protein_analysis/go_obo_data/level_file_detail.txt", "w")
    level_checked = list()
    parsed_go_level = dict()
    while level_dict:
        level_dict_temp = dict()
        # for (level_parent,go_info) in product(level_dict,go_info_list_change):   #todo 效率优化 ---done
        #     if level_parent in go_info[4] and level_dict[level_parent] == go_info[2]:  # is_a 判断//bp_mf_cc分区判断
        for level_parent in level_dict:      # 优化后代码
            if level_parent in is_a_index:      # 优化后代码
                for index in is_a_index[level_parent]:    # 优化后代码
                    go_info = go_info_list[index]      # 优化后代码
                    if go_info[0] not in level_checked:
                        level_checked.append(go_info[0])
                        level_dict_temp[go_info[0]] = level_dict[level_parent]
                        go_info_list_change.remove(go_info)
        for term in level_dict:
            temp = go_info_list[go_name_list.index(term)]
            info = [temp[0],temp[1],temp[2],str(level)+"\n"]
            level_file_detail.write("\t".join(info))
            parsed_go_level[temp[0]] = str(level)
            if temp[3]:
                for term_alt in temp[3]:   #todo 添加alt_id ---done
                    info = [term_alt, temp[1], temp[2], str(level) + "\n"]
                    level_file_detail.write("\t".join(info))
                    parsed_go_level[term_alt] = str(level)
        # print("level_dict",len(level_dict))
        level_dict = dict(level_dict_temp)
        level += 1


    for term in go_info_list_change:    #TODO 处理obsoleted go ---done
        if term[-3]:  #todo replace_by ---done
            try :
                level = parsed_go_level[term[-3]]
            except KeyError:
                print(term)
                parsed_go_level[term[-3]]="0"
                level = parsed_go_level[term[-3]]

            info = [term[0], term[1], term[2], level + "\n"]  #parsed_go_level中可能不存在term[-3]
            level_file_detail.write("\t".join(info))
            parsed_go_level[term[0]] = level
            if term[-3]:
                for term_alt in term[3]:   #todo obsoleted go 添加alt_id ---done
                    info = [term_alt, term[1], term[2], level + "\n"]
                    level_file_detail.write("\t".join(info))
                    parsed_go_level[term_alt] = level
            #except:
            #    print(term)
            #    info=[term[0],term[1],term[2],"0\n"]
            #    level_file_detail.write("\t".join(info))
        else:
            info = [term[0], term[1], term[2], "0\n"]
            level_file_detail.write("\t".join(info))
            if term[3]:
                for term_alt in term[3]:  # todo obsoleted go 添加alt_id ---done
                    info = [term_alt, term[1], term[2], "0\n"]
                    level_file_detail.write("\t".join(info))
                    parsed_go_level[term_alt] = "0"


def generating_go_tree_up2down(is_a_index, go_name_list,go_info_list):
    print("正在生成go关系(up2down)......")
    level_set = {"GO:0005575", "GO:0008150", "GO:0003674"}
    go_tree = dict()
    while level_set:
        level_set_temp = set()
        for level_parent in level_set:
            node_child = set()
            if level_parent in is_a_index:
                for index in is_a_index[level_parent]:    # 优化后代码
                    go_info = go_info_list[index]
            # for go_info in go_info_list:
            #     if level_parent in go_info[4]:
                    level_set_temp.add(go_info[0])
                    node_child.add(go_info[0])
            go_tree[level_parent] = node_child   # 当level seed无子节点，自动赋值空list
            temp = go_info_list[go_name_list.index(level_parent)]  # level_parent对应的go_info
            if temp[3]:
                # alt_id 所对应的go没有 [term]这个模块，即不在go_info_list中
                # for (term_alt,go_info) in product(temp[3],go_info_list): #todo 添加alt_id ---done

                #     if term_alt in go_info[4]:
                for term_alt in temp[3]:
                    # if term_alt in is_a_index:
                    #     for index in is_a_index[level_parent]:
                    #         go_info = go_info_list[index]
                    #         go_tree[temp[0]].add(go_info[0])     #补充alt_id所对应的子节点
                    go_tree[term_alt] = go_tree[temp[0]]
        level_set = set(level_set_temp)
        # print(len(level_set))


    #todo obsoleted_go在go_tree中的关系处理
    for term in go_info_list:    #TODO 处理obsoleted go 
        if term[-3]:  #todo replace_by ---done
            try:
                go_tree[term[0]] = go_tree[term[-3]]
            except KeyError:
                print(term)
                go_tree[term[0]]=go_tree[term[-3]]=set()
            if term[3]:
                for term_alt in term[3]:   #todo obsoleted go 添加alt_id ---done
                    go_tree[term_alt] = go_tree[term[-3]]


    go_tree_file = open("/home/fdong/auto_protein_analysis/go_obo_data/go_tree_up2down.txt","w")
    go_tree_file.write(str(go_tree))
    go_tree_file.close()


def generating_go_tree_down2up(go_info_list):
    print("正在生成go关系(down2up)......")
    go_tree_down2up = dict()
    for go_info in go_info_list:
        go_tree_down2up[go_info[0]] = set(go_info[4])    #is_A
        if go_info[3]:                              #alt_id
            for go_term in go_info[3]:
                    go_tree_down2up[go_term] = set(go_info[4])

    for go_info in go_info_list:
        if go_info[-3]:                             #replace_by
            go_tree_down2up[go_info[0]] = go_tree_down2up[go_info[-3]]
            if go_info[3]:
                for go_term in go_info[3]:
                    go_tree_down2up[go_term] = go_tree_down2up[go_info[-3]]


    go_tree_file = open("/home/fdong/auto_protein_analysis/go_obo_data/go_tree_down2up.txt","w")
    go_tree_file.write(str(go_tree_down2up))
    go_tree_file.close()


#todo is_obsolete 的go ---done
def generate_obsolered_go():
    non_obsolete_file = open("level.txt","r")
    non_obsolete_go = [term.strip() for term in non_obsolete_file if "level" not in term]
    non_obsolete_file.close()
    obsolete_go = [term for term in go_name_list if term not in non_obsolete_go]
    open("obsoleted_go.txt","w").write("\n".join(obsolete_go))


if __name__ == '__main__':
    start = time.time()

    get_go_obo_lastest()

    go_name_list, go_info_list = parse_go_obo()   # 8s
    is_a_index = get_is_a_index(go_name_list,go_info_list) #80s

    generating_go_level_confirm(is_a_index,go_name_list,go_info_list)   #420s,230s
    generating_go_tree_up2down(is_a_index,go_name_list, go_info_list) #660  110s
    generating_go_tree_down2up(go_info_list)



    end = time.time()
    m, s = divmod(end - start, 60)  # 转换时间的方法
    h, m = divmod(m, 60)
    print('任务完成，共耗时%02d小时%02d分%02d秒' % (h, m, s))






























