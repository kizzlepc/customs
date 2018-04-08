# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import threading
from contextlib import closing
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from customs.utils.model import CustomsTable, db_connect
from customs.utils.log import logger
from customs.utils import update_admin_type
mutex = threading.Lock()

class CustomsPipeline(object):
    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=db_connect())()

    def close_spider(self, spider):
        self.session.close()  
    
    def process_item(self, item, spider):
        datas = dict(item)
        try:
            customs = CustomsTable(**datas)
            query = self.session.query(CustomsTable).filter(CustomsTable.customs_code==datas.get('customs_code')).first()
            if query:
                logger.info("已存在----------:{}".format(query.enterprise_name))
            else:
                create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                customs.update_time = create_time
                customs.create_time = create_time
                
                self.session.add(customs)
                self.session.commit()                                
                logger.info("新记录插入$$$$$$$$$$:{}".format(customs.enterprise_name))  
                if mutex.acquire(1):
                    import traceback
                    try:
                        update_admin_type.complete_info()
                    except:
                        print(traceback.print_exc())
                    mutex.release()  
                logger.info("完成=======================================")            
        except Exception as e:
            logger.info('管道异常**********:{}'.format(str(e)))
            
            
'''
import threading
from contextlib import closing
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from customs.utils.model import CustomsTable, db_connect
from customs.utils.log import logger
from customs.utils import update_admin_type
mutex = threading.Lock()

class CustomsPipeline(object):    
    def process_item(self, item, spider):
        datas = dict(item)
        try:
            with closing(sessionmaker(bind=db_connect())()) as session:
                customs = CustomsTable(**datas)
                query = session.query(CustomsTable).filter(CustomsTable.customs_code==datas.get('customs_code')).first()
                if query:
                    logger.info("已存在----------:{}".format(query.enterprise_name))
                else:
                    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    customs.update_time = create_time
                    customs.create_time = create_time
                    
                    session.add(customs)
                    session.commit()                                
                    logger.info("新记录插入$$$$$$$$$$:{}".format(customs.enterprise_name))  
                    if mutex.acquire(1):
                        import traceback
                        try:
                            update_admin_type.complete_info()
                        except:
                            print(traceback.print_exc())
                        mutex.release()  
                    logger.info("完成=======================================")            
        except Exception as e:
            logger.info('管道异常**********:{}'.format(str(e)))
'''
