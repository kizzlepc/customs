import logging  
from logging.handlers import TimedRotatingFileHandler 

logFilePath = "running_log"  
logger = logging.getLogger("customs_logger")  
logger.setLevel(logging.INFO)  
handler = TimedRotatingFileHandler(logFilePath,  
                                   when="h",  
                                   interval=1,  
                                   backupCount=7)  
formatter = logging.Formatter('%(asctime)s - %(message)s')  
handler.setFormatter(formatter)  
logger.addHandler(handler)
