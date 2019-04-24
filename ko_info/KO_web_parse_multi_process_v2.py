import multiprocessing
import time
# from multiprocessing import Pool
from bs4 import BeautifulSoup
import requests
import os
import random

# import urllib
# from urllib import request

def web(ko_num):
    headers = {'Connection': 'keep-alive',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               "Host": "www.genome.jp"
               }
    # url = "http://www.genome.jp/dbget-bin/www_bget?"+ KO_NUM
    url = "http://www.kegg.jp/dbget-bin/www_bget?ko:" + ko_num
    # req = urllib.request.Request(url, headers=headers)
    # response = urllib.request.urlopen(req)
    # html = response.read().decode("windows-1252")
    response = requests.get(url,headers=headers)
    response.encoding = "utf-8"
    html = response.text
    # print(html)
    # print("child:",os.getppid(),"\tparents:",os.getpid())
    if response.status_code != 200:
        # print("The web of %s is filed !" % ko_num)
        print(ko_num,"\tparent:", os.getppid(), "\tchild:", os.getpid())
        # print(multiprocessing.current_process().name)
    return html

def name_definition(soup):
    name = list()
    divs = soup.find_all("div", style="width:555px;overflow-x:auto;overflow-y:hidden", limit=3)
    for divw in divs:
        try:
            if divw.div and divw.div.get_text():
                name.append(divw.div.get_text().strip())
        except AttributeError:
            continue
    return name

def pathway(soup):
    pathway = list()
    tags = soup.find_all(name="tr")
    status = False
    ff = 0
    for tag in tags[0].find_all("td"):
        try:
            if tag.nobr.a.string[0] == "k":
                try:
                    temp = tag.div.nobr.a.string
                except:
                    ko_info_temp = tag.nobr.a.string
                    status = True
            else:
                status = False
        except:
            pass

        if status and tag.string != None:
            status = False
            pathway.append(ko_info_temp)
            pathway.append(tag.string.strip())
        ff+=1
    return pathway

def get_ko_data(ko_num):
    html = web(ko_num)

    soup = BeautifulSoup(html, "lxml")
    KO = soup.code.get_text()[0:6]
    # print(KO)
    name = name_definition(soup)
    pathway_info = pathway(soup)


    ggg = "||"
    for i in range(int(len(pathway_info) / 2)):
        ggg = ggg + pathway_info[(2 * i)] + "|" + pathway_info[(2 * i + 1)] + "||"
    line = KO + "\t" + name[0].replace(u"\xa0", u"") + "\t" + name[1].replace(u"\xa0", u"") + "\t" + ggg.replace(
        u"\xa0", u"") + "\n"
    # file_out = open("KO_INFO333.txt", "a+")
    # file_out.write(line)
    # file_out.close()
    return line


def write_file(result):
    file_out = open("/home/fdong/auto_protein_analysis/ko_info/KO_INFO.txt", "a+")
    file_out.write(result)





def parse_start(file_in_name):
    start = time.time()  # 计时开始
    pool = multiprocessing.Pool(processes=100)
    file_in = open(file_in_name, "r")

    # file_data = list()
    for line in file_in:
        ko_num = line.strip()
        # file_data.append(pool.apply_async(get_ko_data,(ko_num,),callback=write_file))
        pool.apply_async(get_ko_data,(ko_num,),callback=write_file)
        time.sleep(random.uniform(0,0.25))
    pool.close()
    pool.join()
    pool.terminate()


    # file_out = open(file_out_name, "w")
    # for line in file_data:
    #     file_out.write(line.get())
    # file_out.close()
    end = time.time()
    m, s = divmod(end - start, 60)  # 转换时间的方法
    h, m = divmod(m, 60)
    print('KO在线爬取任务完成，共耗时%02d小时%02d分%02d秒' % (h, m, s))



# class _ko_web_parse:
#     ko_num_count = 0
#
#     def __init__(self, ko_num):
#         self.ko_num = ko_num
#         ko_web_parse.ko_num_count += 1
#         if ko_web_parse.ko_num_count % 1000 == 0:
#             print("%s ko have been parsed!\n" % ko_web_parse.ko_num_count)
#
#     # 网页爬取
#     def web(self):
#         headers = {'Connection': 'keep-alive',
#                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
#                    'Accept-Encoding': 'gzip, deflate',
#                    'Accept-Language': 'zh-CN,zh;q=0.9',
#                    "Host": "www.genome.jp"
#                    }
#         # url = "http://www.genome.jp/dbget-bin/www_bget?"+ KO_NUM
#         url = "http://www.kegg.jp/dbget-bin/www_bget?ko:" + self.ko_num
#         req = urllib.request.Request(url, headers=headers)
#         response = urllib.request.urlopen(req)
#         html = response.read().decode("windows-1252")
#         if response.status != 200:
#             print("The web of %s is filed !" % self.ko_num)
#         return html
#
#     # 爬取KO号对应名称
#     def name_definition(self, soup):
#         name = list()
#         divs = soup.find_all("div", style="width:555px;overflow-x:auto;overflow-y:hidden", limit=3)
#         for divw in divs:
#             try:
#                 temp = divw.div
#                 if divw.div and divw.div.get_text():
#                     name.append(divw.div.get_text().strip())
#             except AttributeError:
#                 continue
#         return name
#
#     # pathway
#     def pathway(self, soup):
#         pathway = list()
#         tags = soup.find_all(name="tr")
#         status = False
#         for tag in tags[0].find_all("td"):
#             try:
#                 if tag.nobr.a.string[0] == "k":
#                     try:
#                         temp = tag.div.nobr.a.string
#                     except:
#                         ko_info_temp = tag.nobr.a.string
#                         status = True
#                 else:
#                     status = False
#             except:
#                 pass
#
#             if status and tag.string != None:
#                 status = False
#                 pathway.append(ko_info_temp)
#                 pathway.append(tag.string.strip())
#         return pathway
#
#     def get_ko_data(self,file_out_name):
#         html = self.web()
#         soup = BeautifulSoup(html, "lxml")
#         KO = soup.code.get_text()[0:6]
#         name = self.name_definition(soup)
#         pathway_info = self.pathway(soup)
#
#         ggg = "||"
#         for i in range(int(len(pathway_info) / 2)):
#             ggg = ggg + pathway_info[(2 * i)] + "|" + pathway_info[(2 * i + 1)] + "||"
#         line = KO + "\t" + name[0].replace(u"\xa0", u"") + "\t" + name[1].replace(u"\xa0", u"") + "\t" + ggg.replace(
#             u"\xa0", u"") + "\n"
#         file_out = open(file_out_name, "a+")
#         file_out.write(line)
#         file_out.close()


############多进程
if __name__ == '__main__':
    file_in_name = "/home/fdong/auto_protein_analysis/ko_info/KO_terms.txt"
    file_out_name = "/home/fdong/auto_protein_analysis/ko_info/KO_INFO.txt"
    if os.path.exists(file_out_name):
        os.remove(file_out_name)
    parse_start(file_in_name)


