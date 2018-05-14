import logging
logging.basicConfig(filename='test.log',level=logging.DEBUG)
from datetime import datetime, timedelta
date_time = datetime.today().strftime('%Y-%m-%d %H-%M')
today = date_time.split(' ')[0]
###########################
curTime = date_time.split(' ')[1]

logging.debug('START this minute '+ curTime)