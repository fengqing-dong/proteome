import re
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Host': 'www.kegg.jp',
    'Referer': 'https://www.kegg.jp/kegg-bin/blastkoala_result?id=691b38cf30da70e04213f30424f5f0a38de2ddcb&passwd=lFMeny&type=blastkoala'}
ko_raw_url = "https://www.kegg.jp/kegg-bin/download_htext?htext=ko00001&format=htext&filedir="
req = requests.get(ko_raw_url, headers=headers)
with open("/home/fdong/auto_protein_analysis/ko_info/ko00000.TXT", "wb") as f:
    f.write(req.content)
f.close()


sep = "\t"
file_out = open("/home/fdong/auto_protein_analysis/ko_info/ko_num_class.txt",'w')
title = "A_class\tA_discription\tB_class\tB_discription\tC_class\tC_discription\tKO number\tDiscription\n"
file_out.write(title)

file_out2 = open("/home/fdong/auto_protein_analysis/ko_info/KO_terms.txt",'w')
ko_temp_list = list()
with open("/home/fdong/auto_protein_analysis/ko_info/ko00000.TXT","r") as file_in:
    for line in file_in:
        if line[0] == "A":
            A_ko_temp = re.findall(r"^A(\d*)",line)[0]
            A_discription_temp = re.findall(r"^A\d*(.*)",line)[0]
            # print(A_ko_temp)
            # print(A_discription_temp)
        if line[0] == "B" and len(line)>2:
            B_ko_temp = re.findall(r"^B\s{2}(\d*)",line)[0]
            B_discription_temp = re.findall(r"^B\s{2}\d*(.*)",line)[0]
        if line[0] == "C":
            C_ko_temp = re.findall(r"^C\s{4}(\d*)", line)[0]
            C_discription_temp = re.findall(r"^C\s{4}\d*(.*)", line)[0]
        if line[0] == "D":
            D_ko_temp = re.findall(r"^D\s{6}(K\d*)", line)[0]
            D_discription_temp = re.findall(r"^D\s{6}K\d{5}\s{2}(.*)", line)[0]# +'\n'
            ko_list = [A_ko_temp, A_discription_temp,
                       B_ko_temp, B_discription_temp,
                       C_ko_temp, C_discription_temp,
                       D_ko_temp, D_discription_temp,
                       ]
            file_out.write(sep.join(ko_list) + "\n")
            if D_ko_temp and D_ko_temp not in ko_temp_list:
                ko_temp_list.append(D_ko_temp)
                file_out2.write(D_ko_temp+"\n")

file_in.close()
file_out.close()
file_out2.close()



# ko_num_class
# KO_web_parse_multi_process
# add_ko_omit


