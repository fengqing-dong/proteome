#!/usr/bin/env python
# coding=utf-8

def test():
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




