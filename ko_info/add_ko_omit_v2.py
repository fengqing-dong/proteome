import os
import re
from KO_web_parse_multi_process_v2 import get_ko_data
from KO_web_parse_multi_process_v2 import write_file
import time
import multiprocessing
import random
from multiprocessing import Pool
import time
import shutil

def check_and_backup():
    if os.path.exists("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt"):
        curent_time = time.time()
        ko_info_end_creat_time = os.stat("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt").st_ctime
        # print(ko_info_end_creat_time)
        time_gap = curent_time - ko_info_end_creat_time
        ModifiedTime=time.localtime(os.stat("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt").st_mtime) #文件访问时间  
        y=time.strftime('%Y', ModifiedTime)  
        m=time.strftime('%m', ModifiedTime)  
        d=time.strftime('%d', ModifiedTime)  
        H=time.strftime('%H', ModifiedTime)  
        M=time.strftime('%M', ModifiedTime)

        if time_gap>24*60*60*1.5:
            backup_name = "/home/fdong/auto_protein_analysis/ko_info/ko_info_end_backups/KO_INFO_END_{0}{1}{2}{3}{4}.txt".format(y,m,d,H,M)
            shutil.copy("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt",backup_name)
            print("KO_INFO_END.TXT已经备份，正在更新......")
            os.system("python3 /home/fdong/auto_protein_analysis/ko_info/KO_num_class.py")
            os.remove("/home/fdong/auto_protein_analysis/ko_info/KO_INFO.txt")
        os.remove("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt")




def clean_ko_info(ko_info_end,ko_middle_temp,ko_scraped,num_temp):
    if not ko_middle_temp:
        ko_scraped= []
        num_temp=0
        return (ko_scraped, num_temp)
    for line in ko_middle_temp:
        # print(line)
        if re.match(r"^K\d{5}",line[:6]) and len(re.findall(r"\t",line)) == 3: # 剔除异常行
            match_temp = re.match(r"^K\d{5}",line[:6]).group()
            if match_temp not in ko_scraped:    #去除重复值
                ko_info_end.write(line)
                num_temp += 1   # 已经爬取的数量
                ko_scraped.append(match_temp)
    # ko_middle_temp.close()
    # ko_info_end.close()
    return  (ko_scraped,num_temp)


def get_omit_ko_list(ko_scraped,ko_all_num,num_temp):
    omit_ko_list = list()
    if (ko_all_num - num_temp)!=0:
        ko_all = open("/home/fdong/auto_protein_analysis/ko_info/KO_terms.txt", 'r')
        for ko in ko_all:
             if ko.strip() not in ko_scraped:   #去除已经爬取的
                 omit_ko_list.append(ko.strip())
        # ko_all.close()
    return omit_ko_list



def add_omit_main():
    ko_all = open("/home/fdong/auto_protein_analysis/ko_info/KO_terms.txt", 'r')
    ko_all_num = len(ko_all.readlines())
    ko_all.close()

    num_temp = 0
    ko_scraped = list()
    kegg_ko_omit = list()
    #if os.path.exists("KO_INFO_END.txt"):
    #    os.remove("KO_INFO_END.txt")

    while (ko_all_num - num_temp):
        ko_info_end = open("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt", "a+")  # 所有ko 的所有信息__终版
        try:
            ko_middle_temp = open("/home/fdong/auto_protein_analysis/ko_info/KO_INFO.txt", "r+")  # 多线程爬取的文件，中间含有遗漏
        except:
            ko_middle_temp = None
        # print(ko_all_num,"\t",num_temp)
        (ko_scraped, num_temp) = clean_ko_info(ko_info_end, ko_middle_temp, ko_scraped, num_temp)
        omit_ko_list = get_omit_ko_list(ko_scraped,ko_all_num,num_temp)
        # print("num_temp:\t",num_temp)

        print("omit ko numbers:", len(omit_ko_list))
        if len(omit_ko_list) <= 50:
            print(omit_ko_list)
        # if len(omit_ko_list)==2 and "K06060" in omit_ko_list and "K04225" in omit_ko_list:
        #     break
        # print("omit_ko_list:\t",omit_ko_list)
        # print("kegg_ko_omit:\t",kegg_ko_omit)
        print("*"*30)
        if omit_ko_list == kegg_ko_omit:
            break
        else:
            kegg_ko_omit = omit_ko_list

        if len(omit_ko_list) != 0:
            pool = multiprocessing.Pool(processes=100)
            # file_data = list()
            for line in omit_ko_list:
                ko_list_signle = line.strip()
                # file_data.append(pool.apply_async(get_ko_data, (ko_list_signle,),callback=write_file))
                pool.apply_async(get_ko_data, (ko_list_signle,),callback=write_file)
                time.sleep(random.uniform(0,0.3))
            pool.close()
            pool.join()
            pool.terminate()
            # for line in file_data:
            #     ko_middle_temp.write(line.get())
        ko_middle_temp.close()
        ko_info_end.close()

if __name__ == '__main__':
    start = time.time()  # 计时开始
    # :os.remove("/home/fdong/auto_protein_analysis/ko_info/KO_INFO_END.txt")

    check_and_backup()
    add_omit_main()

    end = time.time()
    m, s = divmod(end - start, 60)  # 转换时间的方法
    h, m = divmod(m, 60)
    print('KO在线爬取任务完成，共耗时%02d小时%02d分%02d秒' % (h, m, s))
