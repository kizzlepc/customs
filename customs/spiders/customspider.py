# -*- coding: utf-8 -*-
import re
import codecs
import scrapy
import requests
import hashlib
import pytesseract
from bsddb3 import db
from scrapy.http import Request
from customs.utils.randoms import POOLS
from customs.utils import denoise
from customs.utils import myconfig
from customs.items import CustomsItem
from customs.utils.log import logger


class CustomspiderSpider(scrapy.Spider):
    name = 'customspider'
    start_urls = ['http://credit.customs.gov.cn/ccppCopAction/getDetail.action',
                  'http://credit.customs.gov.cn/ccppCopAction/createImage.action?0.9816241041897973', 
                  'http://credit.customs.gov.cn/ccppCopAction/queryCopIn.action',
                  'http://credit.customs.gov.cn/ccppCopAction/getDetail.action?seqNo={}&saicSysNo={}',]
    session = requests.session()

    def start_requests(self):
        thisua = POOLS.random_user_agent()
        headers = {'User-Agent': thisua}
        query_strs = self.get_datas("cutword.txt")
        for query in query_strs:
            if self.is_update(query):
                logger.info('跳过>>>>>>>>>>:{}'.format(query.strip()))
                continue
            self.mark_update(query)            
            while 1:
                res = self.session.get(self.start_urls[0], headers=headers)
                value_search = re.search(r'hidden\" value=\"(.+?)\"', res.text)
                value = ''
                if value_search:
                    value = value_search.group(1)           
                res = self.session.get(self.start_urls[1], headers=headers)
                img_code = self.auto_verify_code(res.content)
                data = {
                    'copName': query,
                    'sf': value,
                    'randomCode': img_code,
                    '.x': '0',
                    '.y': '0',
                }
                response = self.session.post(self.start_urls[2], data=data, headers=headers)
                err_msg_re = re.search(r"var errMsg = '(.+?)';", response.text)
                if err_msg_re:
                    err_msg = err_msg_re.group(1)
                    logger.info('{}--{}'.format(err_msg, query.strip()))
                    if err_msg.find('输入的验证码不正确，请重新输入') is 0:
                        continue
                    else:
                        break
                No_list = re.findall(r'onclick=\"getDetail\(\'(.+?)\',\'(.+?)\'\);', response.text)
                for no in No_list:
                    seqNo = no[0]
                    saicSysNo = no[1]
                    if self.is_exists(seqNo+saicSysNo):
                        logger.info('去重..........:{}--{}'.format(seqNo, saicSysNo))
                        continue
                    logger.info('{}--{}'.format(seqNo, saicSysNo))
                    self.mark_exists(seqNo+saicSysNo)
                    while 1:                        
                        target_url = self.start_urls[3].format(seqNo,saicSysNo)
                        headers['Accept-Language'] = 'zh-CN'
                        resp = self.session.get(target_url, headers=headers)
                        if not re.search(r'<!-- 注册信息 -->(.+)<!-- 信用等级 -->', resp.text, re.S):
                            logger.info('页面出错$$$$$$$$$$:{}--{}'.format(seqNo, saicSysNo))
                            self.clear_exists(seqNo+saicSysNo)
                            logger.info(resp.text)
                            continue
                        yield Request(self.start_urls[0], meta={'resp':resp, 'seqNo':seqNo, 'saicSysNo':saicSysNo}, callback=self.parse, dont_filter=True)
                        break
                break
                         
    def get_datas(self, path):
        datas = []
        try:
            with codecs.open(path, 'r', encoding='utf8') as f:
                datas = f.readlines()
        except:
            with open(path, 'r') as f:
                datas = f.readlines()
        return datas  
          
    def auto_verify_code(self, binary):
        image = denoise.denoise_code(binary)

        code = pytesseract.image_to_string(image, lang="fontyp")
        res = re.sub(r'\W', '', code)
        auto_res = res.lower()
        if len(auto_res) is not 6:
            return '123456'
        return auto_res
   
    def parse(self, response):
        resp = response.meta.get('resp')
        register_info = self.parse_html(resp)
        item = CustomsItem()
        for key,value in myconfig.REGISTER_INFOS.items():
            item[key] = register_info[value]
        yield item
        
    def parse_html(self, response):
        html = response.text
        register_infos = re.search(r'<!-- 注册信息 -->(.+)<!-- 信用等级 -->', html, re.S).group(1)
        register_dict = self.format_register(self.get_info(register_infos))
        register_dict['注册日期'] = register_dict['注册日期'].replace('年','-').replace('月','-').replace('日', '')
        return register_dict

    def format_register(self, datas):
        title = [str(datas[x]).strip() for x in range(len(datas)) if x % 2 is 0 ]
        value = [str(datas[y]).strip() for y in range(len(datas)) if y % 2 is not 0]
        return dict(zip(title, value))

    def get_info(self, re_info):
        info_list = re.findall(r'<td(.+?)</td>', re.sub(r'\s+', ' ', re_info), re.S)
        new_list = []
        for info in info_list:
            info = info.replace('>', '').replace('colspan=\"3\"', '').replace('\\', '\\\\')
            try:
                if info.find('getApanage') is not -1:
                    temp = re.search(r'getApanage\(\'(.+?)\'', info).group(1)
                    info = myconfig.APANAGE.get(temp, temp)
                elif info.find('getTradeType') is not -1:
                    temp = re.search(r'getTradeType\(\'(.+?)\'', info).group(1)
                    info = myconfig.TRADE_TYPE.get(temp, temp)
                elif info.find('getSpecialTradeZone') is not -1:
                    temp = re.search(r'getSpecialTradeZone\(\'(.+?)\'', info).group(1)
                    info = myconfig.SPECIAL_TRADE_ZONE.get(temp, temp)
                elif info.find('getRevoke') is not -1:
                    temp = re.search(r'getRevoke\(\'(.+?)\'', info).group(1)
                    info = myconfig.REVOKE.get(temp[0:1], temp)
                elif info.find('getType') is not -1:
                    temp = re.search(r'getType\(\'(.+?)\'', info).group(1)
                    info = myconfig.TYPE.get(temp, temp)
                elif info.find(r'checkbox') is not -1:
                    info = ''
            except:
                info = ''
            new_list.append(info)
        return new_list       

    def is_exists(self, md):
        _, _md, _ =(lambda f,g,d:(g.open('md.db',dbtype=f.DB_HASH, flags=f.DB_CREATE), g.get(str(d).encode('utf8')), g.close()))(db, db.DB(), self.md5_str(md))
        if _md: 
            return True
        else:
            return False 

    def mark_exists(self, md):
        (lambda f,g,d:(g.open('md.db',dbtype=f.DB_HASH, flags=f.DB_CREATE), g.put(str(d).encode('utf8'), b'1'), g.close()))(db, db.DB(), self.md5_str(md))

    def clear_exists(self, md):
        (lambda f,g,d:(g.open('md.db',dbtype=f.DB_HASH, flags=f.DB_CREATE), g.delete(str(d).encode('utf8')), g.close()))(db, db.DB(), self.md5_str(md))
        
    def is_update(self, de):
        _, _de, _ =(lambda f,g,d:(g.open('de.db',dbtype=f.DB_HASH, flags=f.DB_CREATE), g.get(str(d).encode('utf8')), g.close()))(db, db.DB(), self.md5_str(de))
        if _de: 
            return True
        else:
            return False 

    def mark_update(self, de):
        (lambda f,g,d:(g.open('de.db',dbtype=f.DB_HASH, flags=f.DB_CREATE), g.put(str(d).encode('utf8'), b'1'), g.close()))(db, db.DB(), self.md5_str(de))
        
    def md5_str(self, strs):
        m = hashlib.md5(strs.encode('utf8'))
        return m.hexdigest()