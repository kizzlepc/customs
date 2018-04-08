import requests
import re
import os
import time
import base64
from PIL import Image
import json
import time
from datetime import datetime
import math
from scrapy import settings
from customs.utils.randoms import POOLS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
proxies = { "http": "", "https": "", }

def get_code():
    input_path = '.'+os.sep+'code.gif'
    out_path = '.'+os.sep+'code.png'
    im = Image.open(input_path)
    im.save(out_path)
    f = open(out_path,'rb')
    base64_string = base64.b64encode(f.read()).decode('utf8') 
    f.close()

    img_url = 'http://192.168.4.115:8080/decaptcha'

    data={
    'image':base64_string,
    'project':'customs',
    }
    res= requests.post(img_url,data=data)
    res_json = json.loads(res.text)
    return res_json.get('label')

def get_code2():
    input_path = '.'+os.sep+'code.gif'
    out_path = '.'+os.sep+'code.png'
    im = Image.open(input_path)
    im.save(out_path)
    exe_path = BASE_DIR+os.sep+'utils'+os.sep
    png_path = BASE_DIR+os.sep+'rundir'+os.sep
    return os.popen('python '+exe_path+'predict_captcha.py '+png_path+'code.png').read()

def task(campany_name, customs_code):
    while True:
        thisip = POOLS.random_ip()
        proxies['http'] = 'http://'+thisip
        proxies['https'] = 'http://'+thisip
        try:
            res_list = []
            customs_url = 'http://query.customs.gov.cn/HYW2007DataQuery/CompanyQuery.aspx'
            headers = {
                'Host': 'query.customs.gov.cn',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; LCTE)'
            }
            res = requests.get(customs_url, headers=headers, proxies=proxies)
            #time.sleep(3)
            html = res.text
            #print(html)
            if html.find('请稍后') is not -1:
                #print(html)
                sleep_time = re.search(r'请稍后\((.+?)秒后\)再试', html).group(1)
                time.sleep(math.ceil(float(sleep_time)))
                continue
            __VIEWSTATE = re.search(r'id=\"__VIEWSTATE\" value=\"(.+?)\"', html).group(1)
            __EVENTVALIDATION = re.search(r'id=\"__EVENTVALIDATION\" value=\"(.+?)\"', html).group(1)
            #print(__VIEWSTATE)
            #print(__EVENTVALIDATION)
            code_url1 = re.search(r'<div id=\"verifyIdentityImage\".+?>(.+?)</div>', res.text, re.S).group(1)
            code_url2 = re.search(r'src=\"(.+?)\"', code_url1).group(1)
            code_url = 'http://query.customs.gov.cn'+code_url2
            code_url = re.sub(r'&amp;','&',code_url)
            res = requests.get(code_url, headers=headers, proxies=proxies)
            html = res.text
            #time.sleep(3)
            if res.text.find('请稍后') is not -1:
                #print(html)
                sleep_time = re.search(r'请稍后\((.+?)秒后\)再试', html).group(1)
                time.sleep(math.ceil(float(sleep_time)))
                continue

            with open('.'+os.sep+'code.gif', 'wb') as f:
                f.write(res.content)
            #code_name = input('input code:')
            # 替换自己的验证码识别
            code_name = get_code()

            #import traceback
            #try:
                #code_name = get_code2().strip()
            #except:
                #print(traceback.print_exc())
            #print(code_name)

            data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':__VIEWSTATE,
                '__EVENTVALIDATION':__EVENTVALIDATION,
                'txtCompanyName':campany_name,
                'txtVerifyNumber':code_name,
                'btnSubmit':'查询',
            }
            res = requests.post(customs_url,data=data, proxies=proxies)
            html = res.text
            #print(html)
            #time.sleep(3)
            if html.find('请稍后') is not -1:
                #print(html)
                sleep_time = re.search(r'请稍后\((.+?)秒后\)再试', html).group(1)
                time.sleep(math.ceil(float(sleep_time)))
                continue
            if res.text.find('验证码错误，请重新输入') is not -1:
                #print('验证码错误')
                continue
            #data_tr = re.search(r'<tr class=\"grid-color01\".+?>.+?</tr>', res.text, re.S).group()
            data_tr_list = re.findall(r'<tr class=\"grid-color.+?\".+?>.+?</tr>', res.text, re.S)
            for data_tr in data_tr_list:
                #print(data_tr)
                list_td = [re.sub(r'&nbsp;', '', x) for x in re.findall(r'<td.+?>(.+?)</td>', data_tr)]
                customs_name = list_td[0]
                new_customs_code = list_td[1]
                customs_category = list_td[3]
                create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if customs_code == new_customs_code:

                    res_list.append(0)
                    res_list.append(list_td[0])
                    res_list.append(list_td[1])
                    res_list.append(list_td[2])
                    res_list.append(list_td[3])
                    res_list.append(list_td[4])
                    res_list.append(create_time)
                    res_list.append(create_time)
                    res_list.append(1)
            return res_list
        except:
            #time.sleep(7)
            res_list = []
            customs_url = 'http://query.customs.gov.cn/HYW2007DataQuery/CompanyQuery.aspx'
            headers = {
                'Host': 'query.customs.gov.cn',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; LCTE)'
            }
            res = requests.get(customs_url, headers=headers, proxies=proxies)
            #time.sleep(3)
            html = res.text
            
            if html.find('请稍后') is not -1:
                #print(html)
                sleep_time = re.search(r'请稍后\((.+?)秒后\)再试', html).group(1)
                time.sleep(math.ceil(float(sleep_time)))
                continue
      
if __name__ == '__main__':
    campany_name = '广州市誉泰国际物流有限公司'
    customs_code = '440128Z2A7'
    admin_type = task(campany_name, customs_code)
    print(admin_type)