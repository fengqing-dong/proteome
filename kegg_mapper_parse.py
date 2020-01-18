from selenium import webdriver
import time
import os
import shutil
import zmail
from urllib import request
import urllib
import re
import lxml
import requests
from bs4 import BeautifulSoup
from scipy import stats
from statsmodels.stats import multitest
from itertools import islice
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import math
import multiprocessing
import sys
import openpyxl


def download_file(download_url, file_name, file_format,diff_or_all):
    #user_ko_txt的file_name 已经加diff_or_all后缀;全部放置在根目录下
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Host': 'www.kegg.jp',
        'Referer': 'https://www.kegg.jp/kegg-bin/blastkoala_result?id=4ceefc5ff725eb0776e7ea17e3af40e2ab3a47a2&passwd=L9fC3n&type=blastkoala'}

    try:
        req = requests.get(download_url, headers=headers, timeout=600)
    except:  #kegg判断为远程攻击，终端访问;;;;网络卡顿等
        print("执行异常：网络超时！")
        if file_format == ".png":
            file_name_format = file_name + file_format
        print("执行异常:{0}图片下载异常，请重新手动下载图片!\n".format(file_name_format))
        pass
    else:
        if file_format == ".png":
            diff_group = diff_or_all.strip().split("_")[1]
            file_name_format = file_name + file_format
            file_downloaded = "./KEGG_diff/{0}/map/{1}".format(diff_group,file_name_format)
        else:
            file_downloaded = file_name + file_format
        if len(req.content) > 1:
            with open(file_downloaded, "wb") as f:
                f.write(req.content)
            f.close()
            # print("{0}文件下载完成！".format(file_downloaded))


def download_map(map_web_rul,diff_or_all):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/65.0.3325.181 Safari/537.36'}
        pattern = re.compile(r"/tmp/mark_pathway.*\.png")
        map_png_url_head = "https://www.kegg.jp"
        map_name = map_web_rul[-25:-17]

        diff_group = diff_or_all.strip().split("_")[1]
        file_name_format = map_name + ".png"
        file_downloaded = "./KEGG_diff/{0}/map/{1}".format(diff_group, file_name_format)

        if not os.path.exists(file_downloaded):
            # req = urllib.request.Request(map_web_rul, headers=headers)
            # response = urllib.request.urlopen(req)
            response = requests.get(map_web_rul,headers=headers)
            response.enconding= "utf-8"
            html = response.text
            #3 html = response.read().decode("windows-1252")
            map_png_url_end = re.findall(pattern, html)[0]
            map_png_url = map_png_url_head + map_png_url_end

            download_file(map_png_url, map_name, ".png",diff_or_all)


def kegg_mapper_parseing(user_ko_filename):
    # 打开网站
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    driver=webdriver.Chrome(executable_path="/home/fdong/auto_protein_analysis/chromedriver",chrome_options=options)
    # driver = webdriver.PhantomJS(executable_path='./phantomjs/bin/phantomjs.exe')
    driver.get("https://www.kegg.jp/kegg/tool/map_pathway.html")

    #上传USER_KO
    file_name = os.path.join(os.getcwd(), user_ko_filename)
    upload = driver.find_element_by_name('uploadfile')
    time.sleep(2)


    # print("name\t",file_name)
    upload.send_keys(file_name)

    # 提交
    submit = driver.find_element_by_xpath('//*[@id="main"]/form/input[2]')
    submit.click()

    # driver.get_screenshot_as_file("6666666666666666.png")
    html = driver.page_source  #直接获取跳转后的页面源码
    map_url_list = list()
    web_head = 'https://www.kegg.jp'
    pattern = re.compile(r"/kegg-bin/show_pathway.*\.coords\+reference")
    download_url = re.findall(pattern, html)
    for i in download_url:
        map_url_list.append(web_head + i)
    return map_url_list


def generate_user_ko_offline(user_ko_all_file,diff_fasta_file,diff_or_all):
    ko_all = open(user_ko_all_file,"r")
    ko_all_dict = dict()
    for line in ko_all:
        line  = line.strip().split("\t")
        if len(line) ==2:
            ko_all_dict[line[0]]=line[1]

    ko_diff = open(diff_fasta_file,"r")
    ko_diff_filename = "user_ko_{0}.txt".format(diff_or_all)
    ko_diff_file = open(ko_diff_filename,"w")
    for line in ko_diff:
        if line[0] ==">":
            protein_name = line.strip()[1:]
            if protein_name in ko_all_dict.keys():
                ko_diff_file.write("{0}\t{1}\n".format(protein_name,ko_all_dict[protein_name]))
            else:
                ko_diff_file.write("{0}\t\n".format(protein_name))

    ko_diff_file.close()
    ko_all.close()
    ko_diff.close()

    return ko_diff_filename


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


def auto_blast_ko(query_file,email_info, taxid):
    file_name = os.path.join(os.getcwd(), query_file)

    # 打开网站
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    driver=webdriver.Chrome(executable_path="/home/fdong/auto_protein_analysis/chromedriver",chrome_options=options)
    driver.get("https://www.kegg.jp/blastkoala/")

    # 选择物种ID
    elem1 = driver.find_element_by_name('taxid')
    elem1.send_keys(taxid)

    # 选择种群分类
    elem2 = driver.find_element_by_xpath('//*[@id="main"]/form/div[7]/div/input[1]')
    elem2.click()

    # 选择邮箱
    elem1 = driver.find_element_by_name('email')
    elem1.send_keys(email_info[0])
    
    # 上传文件
    upload = driver.find_element_by_name('input_file')
    time.sleep(2)
    upload.send_keys(file_name)
    # driver.save_screenshot("ffff1.png")
    upload.submit()

    # print(upload.get_attribute('value'))

    # driver.save_screenshot("ffff.png")
    # 提交
    # submit = driver.find_element_by_xpath('//*[@id="main"]/form/input[1]')
    # submit.click()
    # driver.save_screenshot("ffff.png")
    # time.sleep(5)
    # driver.refresh()

    # print(driver.current_url)  # 当前页面url
    if driver.current_url == "https://www.kegg.jp/kegg-bin/blastkoala_accept":
        print("执行正常：文件上传成功，等待邮件获取")
    else:
        print("执行异常：网络可能延迟，从新加载中！")

        # 以下注释，当异常时，显示网页中信息

        print("driver.current_url:", driver.current_url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        url = driver.current_url
        # url = 'https://www.kegg.jp/kegg-bin/blastkoala_request'
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("windows-1252")
        soup = BeautifulSoup(html, "lxml")
        print(soup.find("div", id="main").get_text())


def get_email(Identification,contents_line, upload_time,email_info):
    server1 = zmail.server(email_info[0],email_info[1])
    # 邮件内容结构 dict_keys(['date', 'from', 'to', 'subject', 'content-type', 'boundary', 'content', 'contents', 'attachments', 'id'])


    """
    # todo 这种方式得到会得到前一次completed 邮件。。BUG未知
    mail_info = server1.get_info()
    for mail in mail_info:
        mail_time_str = mail['date'][:18].strip()
        mail_time = time.strptime(mail_time_str, "%Y-%m-%d %H:%M:%S")
        if (mail['subject'] == Identification) and (mail_time > upload_time):
            print("upload_time:{}\n".format(upload_time))
            print("mail_time  :{}\n".format(mail_time))
        # if (mail['subject'] ==Identification):
            mail_id = mail['id']
            new_mail = server1.get_mail(mail_id)
            submit_url = new_mail['contents'][contents_line].replace(' (Submit)', '')
            print("执行正常：{} 邮件已经收到，并解析！".format(Identification))
            return submit_url
        """
    try:
        mail = server1.get_latest()
        # mail_time_str = mail['date'][:18].strip()
        # mail_time = time.strptime(mail_time_str, "%Y-%m-%d %H:%M:%S")
        # if (mail['subject'] == Identification) and (mail_time > upload_time):
        #print(mail['subject'])
        #print(Identification)
        if mail['subject'] ==Identification:
            #print("进入for 循环")
            # print("upload_time:{}\n".format(upload_time))
            # print("mail_time  :{0}\tmail_ID:{1}\n".format(mail_time,mail["id"]))
            submit_url = mail["content_text"][0].split("\r\n")[contents_line].replace(' (Submit)', '')
            #print("submit_url:",submit_url)
            # submit_url = mail["content_text"][0].split("\r\n")[8].replace(' (Submit)', '')
            print("执行正常：{} 邮件已经收到，并解析！".format(Identification))
            return submit_url
    except:
        pass


def submit_url_to_kegg(submit_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    req = urllib.request.Request(submit_url, headers=headers)
    response = urllib.request.urlopen(req)
    html = response.read().decode("windows-1252")
    if re.search("Your BlastKOALA job was submitted", html):
        print("执行正常：query.fasta文件已经提交！\n\tKO信息在计算中，请等待分析结果...")
    if re.search("Your job is being calculated", html):
        print("执行异常：重复提交！\n\t文件正在计算！")


def get_urls(BlastKOALA):
    raw_url = requests.get(BlastKOALA)
    time.sleep(2)
    rep = raw_url.text
    pattern = re.compile(r"https://www\.kegg\.jp/kegg-bin/download\?.*/user_ko\.txt")
    download_url = re.search(pattern, rep).group(0)

    pattern = re.compile(r"https://www\.kegg\.jp/kegg-bin/find_pathway_object\?.*/user_ko\.txt")
    pathway_url = re.search(pattern, rep).group(0)
    if download_url and pathway_url:
        print("file_url:", download_url)
        print("pathway_url:", pathway_url)
        print("执行正常：user_ko和pahway链接已经获得！")
    return (download_url, pathway_url)


def get_email_to_analysis(Identification_ko, contents_line, func, upload_time, time_sleep,email_info):
    email_parse_times = 0
    while True:
        submit_url = get_email(Identification_ko, contents_line, upload_time,email_info)
        email_parse_times += 1
        if submit_url:
            return func(submit_url)
            break
        else:
            print("第{0}次收取{1}邮件失败！\t{2}秒后重试！\t{3}".format(email_parse_times, Identification_ko, time_sleep, time.ctime()))
            time.sleep(time_sleep)  # 设置邮件获取频率


def file_generate(diff_or_all):
    try:
        user_ko = open("user_ko_{0}.txt".format(diff_or_all),'r')
        ko = open("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt", 'r')
        ko_terms_list = list()
        ko_dict = dict()
        for line in ko:
            ko_dict[line[:6]] = line
            ko_terms_list.append(line[:6])
        ko.close()
    except FileNotFoundError:
        exit("异常退出：user_ko_all文件不存在！请将该文件与该脚本放置相同路径下！")
#todo  txt文件直接放置到对应文件夹下 ---done
    if diff_or_all == "all":
        query2map = open("./KEGG_all/query2map_{0}.txt".format(diff_or_all), "w")
        mappids = open("./KEGG_all/mappids_{0}.txt".format(diff_or_all), "w")
        map2query = open("./KEGG_all/map2query_{0}.txt".format(diff_or_all), "w")
    else:
        #diff_group = diff_or_all.strip().split("_")[1]
        diff_group  = diff_or_all.replace("diff_","")
        query2map = open("./KEGG_diff/{0}/query2map.txt".format(diff_group), "w")
        mappids = open("./KEGG_diff/{1}/mappids_{0}.txt".format(diff_or_all,diff_group), "w")
        map2query = open("./KEGG_diff/{0}/map2query.txt".format(diff_group), "w")

    query2map.write("Protein ID\tKO\tName\tDefinition\tMap ID\tMap Name\tURL\n")
    map2query.write("Map ID\tMap Name\tSeqs\t#Seqs\tURL\n")

    mappid_list = list()
    map2query_dict = dict()
    user_ko_dict = dict()


    for user_ko_line in user_ko:
        user_ko_line = user_ko_line.strip().split(sep="\t")
        if len(user_ko_line) == 1:
            query2map.write("{0}\t\t\t\t\t\t\n".format(user_ko_line[0]))
        elif len(user_ko_line) == 2:
            user_ko_dict[user_ko_line[0]] = user_ko_line[1]
            try:
                ko_line = ko_dict[user_ko_line[1]]
            except KeyError:
                query2map.write("{0}\t{1}\t\t\t\t\t\n".format(user_ko_line[0], user_ko_line[0]))
            else:
                ko_line = ko_line.split(sep="\t")
                map_ids = ko_line[3].split("||")
                map_ids.pop(0)
                map_ids.pop()
                if map_ids:
                    for map_term in map_ids:
                        map_term = map_term.split("|")
                        # 得到mapid
                        if map_term[0] not in mappid_list:
                            # print(map_term[0])
                            mappid_list.append(map_term[0])
                            mappid_list.append(map_term[1])
                            map2query_dict[map_term[0]] = user_ko_line[0]
                        else:
                            map2query_dict[map_term[0]] += " {}".format(user_ko_line[0])
                        temp2write = u"{0}\t{1}\t{2}\t{3}\t{4}\t{5}\thttp://www.kegg.jp/kegg-bin/show_pathway?{4}+{1}\n".format(
                            user_ko_line[0], user_ko_line[1], ko_line[1], ko_line[2], map_term[0], map_term[1])
                        query2map.write(temp2write)
                else:
                    temp2write = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t\n".format(user_ko_line[0], user_ko_line[1],
                                                                           ko_line[1], ko_line[2], "", "")
                    query2map.write(temp2write)
    query2map.close()


    for i in range(len(mappid_list)):
        if i!=0 and i%2 == 1:
            mappids.write("{0}\t{1}\n".format(mappid_list[i-1],mappid_list[i]))
            protein = map2query_dict[mappid_list[i-1]]
            map_url_ko = [user_ko_dict[i] for i in protein.split(" ") ]
            map_url= "http://www.kegg.jp/kegg-bin/show_pathway?{}+{}".format(mappid_list[i-1],"+".join(map_url_ko))
            map2query.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(mappid_list[i-1],mappid_list[i],protein,len(protein.split(" ")),map_url))
    mappids.close()
    map2query.close()
    print("本地匹配，文件生成正常！")


def file_move(diff_multi):
# todo 多分组时文件夹生成和文件移动 ---done

    for diff_or_all  in diff_multi.keys():
        diff_group = diff_or_all.split("_")[1]
        ko_file_name = "user_ko_{0}.txt".format(diff_or_all)
        try:
            shutil.move(ko_file_name, "KEGG_diff/{0}".format(diff_group))
        except:
            os.remove("KEGG_diff/{0}/{1}".format(diff_group,ko_file_name))
            shutil.move(ko_file_name, "KEGG_diff/{0}".format(diff_group))

    for file in os.listdir():
        if "all" in file and "fasta" not in file and "user_ko_all" not in file:
            try:
                shutil.move(file, 'KEGG_all')
            except:
                os.remove("KEGG_all/{0}".format(file))
                shutil.move(file, 'KEGG_all')


def kegg_enrich(diff_multi,all_total):
    for diff_or_all in diff_multi.keys():
        diff_total = diff_multi[diff_or_all]
        #diff_group = diff_or_all.strip().split("_")[1]
        diff_group = diff_or_all.replace("diff_",'')

        #todo 进入多分组的子文件夹后富集分析  ---done
        map2query_diff = open("./KEGG_diff/{0}/map2query.txt".format(diff_group), "r")
        enrich = list()
        for line in islice(map2query_diff, 1, None):
            line = line.strip().split("\t")
            new_line = line[:4]

            map2query_all = open("./KEGG_all/map2query_all.txt", "r")
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
                over_under = "Over"
            else:
                over_under = "Under"

            enrich[i].append(str(diff))
            enrich[i].append(str(ref))
            enrich[i].append(str(p_value))
            enrich[i].append(str(over_under))
        fdr_list = multitest.multipletests(p_value_list, method="fdr_bh")[1]
#        title = ['MapID', 'MapName', '#DIFF', '#REF', '%Diff', '%Ref', 'P_Value', 'FDR', 'over_under', 'DiffSeqs']
        title = ['Map ID', 'Map Name', '#Diff', 'P_Value', 'FDR', 'Over/Under', 'DiffSeqs']
        enrich_filename = "./KEGG_diff/{0}/enrichment.txt".format(diff_group)
        rich_file = open(enrich_filename, "w")

        rich_file.write('\t'.join(title) + '\n')
        enrich = sorted(enrich,key=lambda s:float(s[7]))
        for i in range(len(enrich)):
#            line_temp = enrich[i][0:2] + enrich[i][3:8] + [str(fdr_list[i])] + [enrich[i][8]] + [enrich[i][2]]
            line_temp = enrich[i][0:2] + [enrich[i][3]]+[enrich[i][7]] + [str(fdr_list[i])] + [enrich[i][8]] + [enrich[i][2]]
            line = "\t".join(line_temp) + "\n"
            rich_file.write(line)

        rich_file.close()

        ### todo 测试以下代码 ---done 正常
        enrich_kegg = open("./KEGG_diff/{0}/enrich_kegg.txt".format(diff_group), "w")
        enrich_kegg.write('\t'.join(title) + '\n')
#        enrich_kegg.write(''.join(sorted(filter(lambda line: line.split("\t")[8] == "Over" and float(line.split("\t")[6]) < 0.05, open(enrich_filename, "r")),key=lambda s: float(s.split("\t")[6]))[:10]))
        enrich_kegg.write(''.join(sorted(filter(lambda line: line.split("\t")[5] == "Over" and float(line.split("\t")[3]) < 0.05, open(enrich_filename, "r")),key=lambda s: float(s.split("\t")[3]))[:10]))
        enrich_kegg.close()
    print("执行正常：富集分析已经完成！")


def enrich_kegg_plot(diff_multi):
    for diff_or_all in diff_multi.keys():
        #diff_or_all = diff_or_all.strip().split("_")[1]
        diff_or_all = diff_or_all.replace("diff_","")
        file = open("./KEGG_diff/{0}/enrich_kegg.txt".format(diff_or_all), "r")

        name = list()
        p_value = list()
        for line in islice(file, 1, None):
            line = line.split("\t")
            name.append(line[1])
#            p_value.append(-math.log(float(line[6]), 10))
            p_value.append(-math.log(float(line[3]), 10))


        name.reverse()
        p_value.reverse()
        if not p_value:
            print("{0}组无富集结果！".format(diff_or_all))
            continue


        p_max = max(p_value)

        plt.rcdefaults()
        customer_font = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf")

        # (width, height)
        len_max = max([len(term) for term in name])
        # print(len_max)
        width_user = round(len_max / 40 * 6.1 + 5)
        height_user = 0.6 * len(p_value) + 2

        # plt.rcParams['figure.autolayout'] = True
        plt.rcParams['figure.figsize'] = (width_user, height_user)
        fig = plt.figure()
        ax = fig.add_axes([0.95 - 5 / width_user, 0.05, 5 / width_user, 0.95 - 1 / height_user])
        # ax = fig.add_axes([0.1,0.1, 0.8, 0.8])
        # ax = plt.axes()
        ax.barh(np.arange(0, len(name)), p_value, height=0.6, color="#483D8B", linestyle="-", edgecolor="black",
                linewidth=2)

        ax.spines['bottom'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.xaxis.set_ticks_position('top')
        ax.spines['top'].set_position(('axes', 0.99))
        ax.set_yticks(np.arange(len(p_value))) 
        customer_font2 = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=16)
        ax.set_yticklabels(name,fontProperties=customer_font2)

        # ax.set_xticks(range(0, int(p_max + 1) + 1))
        ax.set_xlim(0,int(p_max + 1)+1)
        customer_font2 = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=22)
        plt.xticks(fontProperties=customer_font2)
        # plt.xticks(size=18,fontProperties=customer_font)
        #  plt.xticks(fontdict={"fontsize":22},fontProperties=customer_font)
        # ax.set_xticklabels(range(0, int(p_max + 1) + 1), fontdict={'fontsize': 22}, fontProperties=customer_font)
        customer_font2 = FontProperties(fname=r"/home/fdong/auto_protein_analysis/Helvetica.ttf",size=22)
        plt.title("-Log10(P_Value)\n", y=1.025, fontProperties=customer_font2,fontweight="bold")
        # plt.xlim(0, round(p_max)+1) # change
        plt.savefig("./KEGG_diff/{0}/enrich_kegg.tiff".format(diff_or_all),dpi=150)
        plt.close()





def get_fasta_len():
    diff_multi = dict()
    if os.path.exists("GO"):
        file_list = os.listdir("GO")
    else:
        file_list = os.listdir()
    for file in file_list:
        counts = 0
        if file[-5:].upper() == "FASTA":
            if os.path.exists("GO"):
                fh = open("./GO/{0}".format(file), "r")
            else:
                fh = open(file,"r")
            for line in fh:
                if line[0] == ">":
                    counts += 1

            if re.search("diff", file):
                diff_or_all = re.findall(r"query_(diff_.*)\.fasta", file, re.IGNORECASE)[0]
                diff_multi[diff_or_all] = counts
            elif re.search("all", file):
                all_total = counts

    return diff_multi,all_total


def check_map(map_url_list,diff_or_all):
    diff_group = diff_or_all.split("_")[1]
    map_list = os.listdir("./KEGG_diff/{0}/map".format(diff_group))
    if len(map_list) == len(map_url_list) and len(map_list)>0:
        print("执行正常：{0}图片下载完全！".format(diff_or_all))
    elif len(map_list) < len(map_url_list):
        for map in map_list:
            for map_url in map_url_list:
                if map[:8] in map_url:
                    map_url_list.remove(map_url)
        for map_url_remain in map_url_list:
            download_map(map_url_remain, diff_or_all)


def txt2excel(group):
    path = "./KEGG_diff/{0}/".format(group)
    command = "perl /home/fdong/auto_protein_analysis/TXToXLSX.pl {0}KEGG.xlsx {0}query2map.txt {0}map2query.txt {0}enrichment.txt".format(path)
    os.system(command)


def main_func(taxid=None,email_info=None,map_download=None):
    # 任务开始
    # print(os.listdir("GO"))
    #print(os.getcwd())
    if os.path.exists("GO"):
        file_list= os.listdir("GO")
    else:
        file_list = os.listdir()
    file_list.sort()
    print(file_list)
    for file in file_list:
      #   print(file)
        if file[-5:].upper() == "FASTA" and file[0:5].upper() == "QUERY":
            if os.path.exists("GO"):
                file= "./GO/{0}".format(file)
            print("\n","*"*30,"\n")
            print("执行正常：正在处理{0}文件！".format(file))
            #TODO 文件夹检查---done
        
            if re.search("diff",file):
                diff_or_all = re.findall(r"query_(diff_.*)\.fasta",file, re.IGNORECASE)[0]
                # diff_group = diff_or_all.split("_")[1:]
                diff_group = diff_or_all.replace("diff_","")
                if not os.path.exists("KEGG_diff/{0}".format(diff_group)):
                    os.makedirs("KEGG_diff/{0}".format(diff_group))
                ko_diff_filename = generate_user_ko_offline("user_ko_all.txt", file, diff_or_all)
                file_generate(diff_or_all)
                if map_download:
                    os.makedirs("KEGG_diff/{0}/map".format(diff_group))               
                    map_url_list = kegg_mapper_parseing(ko_diff_filename)
                    print("执行正常：正常下载{0}图片,共{1}张图片".format(diff_or_all, len(map_url_list)))
                    pool = multiprocessing.Pool(processes=130)
                    for map_web_rul in map_url_list:
                        try:
                            # download_map(map_web_rul, diff_or_all)
                            pool.apply_async(download_map,(map_web_rul,diff_or_all))
                        except:
                            print("执行异常：图片{0}下载异常".format(map_web_rul[-25:-17]))
                    pool.close()
                    pool.join()
                    check_map(map_url_list, diff_or_all)
                txt2excel(diff_group)
            elif re.search("all",file, re.IGNORECASE):
                diff_or_all = "all"
                if not os.path.exists("KEGG_all"):
                    os.makedirs("KEGG_all")
                if not os.path.exists("user_ko_all.txt"):
                    # print(taxid,email_info)
                    if not (taxid and email_info):
                        email_info = input_email()
                        taxid = get_taxid()
                    # break
                    diff_or_all = "all"
                    if not os.path.exists("KEGG_all"):
                        os.makedirs("KEGG_all")
                    upload_time = time.localtime()
                    # #提交
                    auto_blast_ko(file,email_info, taxid)
                    # 第一封邮件
                    Identification_ko_accepted = '[KEGG BlastKOALA] Request accepted'
                    get_email_to_analysis(Identification_ko_accepted, 8, submit_url_to_kegg, upload_time, 60, email_info)
                    # 第二封邮件
                    Identification_ko_completed = '[KEGG BlastKOALA] Job completed'
                    (download_url, pathway_url) = get_email_to_analysis(Identification_ko_completed, 4, get_urls, upload_time,600, email_info)
                    # 下载文件
                    file_name = "user_ko_{0}".format(diff_or_all)
                    download_file(download_url, file_name, ".txt",diff_or_all)
                file_generate(diff_or_all)



    #富集分析
    (diff_multi, all_total) = get_fasta_len()
    kegg_enrich(diff_multi,all_total)
    enrich_kegg_plot(diff_multi)
  
    # 移动文件
    file_move(diff_multi)


if __name__ == '__main__':
    """
    实现多组分析
    输入一个email
    taxid输入
    user_ko_diff本地生成
    diff_fasta的kegg途径通过KEGG MAPPER网站完成
    multi线程下载图片
    """
    start = time.time()
    
    map_download_flag = None   #控制是否下载KEGG中的图片
    if len(sys.argv)==2 and sys.argv[1]=="m":
        map_download_flag = True
    main_func(map_download=map_download_flag)

    end = time.time()
    m, s = divmod(end - start, 60)  # 转换时间的方法
    h, m = divmod(m, 60)
    print('任务完成，共耗时%02d小时%02d分%02d秒' % (h, m, s))
























