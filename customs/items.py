# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CustomsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    social_credit_code = scrapy.Field()
    customs_code = scrapy.Field()
    register_date = scrapy.Field()
    org_code = scrapy.Field()
    enterprise_name = scrapy.Field()
    registered_customs = scrapy.Field()
    address = scrapy.Field()
    admin_area = scrapy.Field()
    economics_area = scrapy.Field()
    category = scrapy.Field()
    special_area = scrapy.Field()
    industry = scrapy.Field()
    validity_period = scrapy.Field()
    types_trade = scrapy.Field()
    customs_flag = scrapy.Field()
    report = scrapy.Field()
