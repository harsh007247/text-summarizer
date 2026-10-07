import os
import sys
import logging


logging_str="[%(asctime)s: %(levelname)s: %(module)s: %(message)s:]"
log_dir="logs"
log_filepath=os.path.join(log_dir,"running_logs.log")
os.makedirs(log_dir,exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format=logging_str,

    handlers=[#handlers mtlb ki log ko bhejna kha h 
        logging.FileHandler(log_filepath),#yhan jaa rha h created file ke andar
        logging.StreamHandler(sys.stdout)#or yhan prr terminal prr jaa rha h
    ]
)

logger=logging.getLogger("textsummarizerlogger")