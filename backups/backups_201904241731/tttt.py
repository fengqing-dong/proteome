#!/usr/bin/env python
# coding=utf-8
import sys
from go_enrich import hcluster2

if len(sys.argv)>1:
    group = sys.argv[1]
    hcluster2(group)
else:
    print("请输入分组信息")


