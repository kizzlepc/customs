from pymysql import connect
from contextlib import closing
from customs.utils import customs_query
import time
from customs.utils.log import logger
from customs.utils import  myconfig


def get_connect():
    return connect(host=myconfig.HOST, port=myconfig.PORT, database=myconfig.DATABASE, user=myconfig.USER, password=myconfig.PASSWORD, charset=myconfig.CHARSET)

def jsf_connect():
    return connect(host=myconfig.JSF_HOST, port=myconfig.JSF_PORT, database=myconfig.JSF_DATABASE, user=myconfig.JSF_USER, password=myconfig.JSF_PASSWORD, charset=myconfig.JSF_CHARSET)
    
def complete_info():
    with closing(jsf_connect()) as jsf_conn, closing(get_connect()) as conn:
        with closing(jsf_conn.cursor()) as jsf_cur, closing(conn.cursor()) as cur:
            count = 0
            while True:
                sql = 'SELECT customs_code,enterprise_name,register_date FROM ent_custom_registration_info WHERE ent_admin_type is null ORDER BY id desc LIMIT %s,10'%str(count+0)
                resualt = cur.execute(sql)
                if resualt:
                    for res in cur.fetchall():
                        campany_name = res[1]
                        customs_code = res[0]
                        register_date = res[2]
                        jsf_sql = 'select enterprise_admin_type from ent_custom_registration_info where custom_code=\"%s\"'%customs_code
                        resualt_count = jsf_cur.execute(jsf_sql)
                        if resualt_count:
                            update_sql = ''
                            for jsf_res in jsf_cur.fetchall():
                                if jsf_res[0]:
                                    update_sql = 'update ent_custom_registration_info set ent_admin_type=\"%s\" where customs_code=\"%s\"'%(jsf_res[0], customs_code)
                                else:
                                    update_sql = 'update ent_custom_registration_info set ent_admin_type=\"NULL\" where customs_code=\"%s\"'%(customs_code)
                            cur.execute(update_sql)
                            conn.commit()
                            logger.info('success'+str(customs_code))
                        else:
                            ent_admin_type = customs_query.task(campany_name, customs_code)
                            if ent_admin_type:
                                update_sql = 'update ent_custom_registration_info set ent_admin_type=\"%s\" where customs_code=\"%s\"'%(ent_admin_type[4], customs_code)
                                cur.execute(update_sql)
                                conn.commit()
                                insert_sql = ''
                                if ent_admin_type[5]:
                                    ent_admin_type.append(register_date)
                                    insert_sql = "INSERT INTO ent_custom_registration_info(id,enterprise_name,custom_code,report_type,enterprise_admin_type,registration_period,create_time,update_time,data_status,registration_period_bak) VALUES(%s, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %s, \'%s\')"%(*ent_admin_type,)
                                else:
                                    params = []
                                    params.append(ent_admin_type[0])
                                    params.append(ent_admin_type[1])
                                    params.append(ent_admin_type[2])
                                    params.append(ent_admin_type[3])
                                    params.append(ent_admin_type[4])
                                    params.append(ent_admin_type[6])
                                    params.append(ent_admin_type[7])
                                    params.append(ent_admin_type[8])
                                    params.append(register_date)
                                    insert_sql = "INSERT INTO ent_custom_registration_info(id,enterprise_name,custom_code,report_type,enterprise_admin_type,create_time,update_time,data_status,registration_period_bak) VALUES(%s, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %s, \'%s\')"%(*params,)
                                jsf_sql = 'select enterprise_admin_type from ent_custom_registration_info where custom_code=\"%s\"'%customs_code
                                resualt_count = jsf_cur.execute(jsf_sql)
                                if resualt_count:
                                    logger.info('exit...')
                                else:                                        
                                    jsf_cur.execute(insert_sql)
                                    jsf_conn.commit()
                                    logger.info('success..ip')
                            else:
                                update_sql = 'update ent_custom_registration_info set ent_admin_type=\"NULL\" where customs_code=\"%s\"'%(customs_code)
                                cur.execute(update_sql)
                                conn.commit()
                                logger.info('no record'+str(count))
                                time.sleep(3)
                                count +=1                                    
                else:
                    logger.info('结束...')
                    break
       
if __name__ == '__main__':
    while True:
        try:
            complete_info()
        except:
            continue