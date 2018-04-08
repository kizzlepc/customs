# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from customs.utils.myconfig import HOST, PORT, DATABASE, USER, PASSWORD, CHARSET


Base = declarative_base()

def db_connect():
    return create_engine("mysql+mysqlconnector://%s:%s@%s/%s?charset=%s"%(USER, PASSWORD, HOST, DATABASE, CHARSET))

def create_table():
    engine = db_connect()
    Base.metadata.create_all(engine)

class CustomsTable(Base):
    __tablename__ = 'ent_custom_registration_info'

    id = Column(Integer, primary_key=True)
    social_credit_code = Column('social_credit_code', String(64), comment='统一社会信用代码')
    customs_code = Column('customs_code', String(32), unique=True, comment='海关注册编码')
    register_date = Column('register_date', DateTime, comment='注册日期')
    org_code = Column('org_code', String(32), comment='组织机构代码')
    enterprise_name = Column('enterprise_name', String(64), comment='企业中文名称')
    registered_customs = Column('registered_customs', String(64), comment='注册海关')
    address = Column('address', String(200), comment='工商注册地址')
    admin_area = Column('admin_area', String(64), comment='行政区划')
    economics_area = Column('economics_area', String(64), comment='经济区划')
    category = Column('category', String(32), comment='经营类别')
    special_area = Column('special_area', String(64), comment='特殊贸易区域')
    industry = Column('industry', String(64), comment='行业种类')
    validity_period = Column('validity_period', String(32), comment='报关有效期')
    types_trade = Column('types_trade', String(64), comment='跨境贸易电子商务类型')
    customs_flag = Column('customs_flag', String(32), comment='海关注销标志')
    report = Column('report', String(32), comment='年报情况')
    ent_admin_type = Column('ent_admin_type', String(64), comment='企业管理类别')
    update_time = Column('update_time', DateTime)
    create_time = Column('create_time', DateTime, comment='dd创建时间')
    src = Column('src', String(32), comment='dd来源')
    

if __name__ == '__main__':
    create_table()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    