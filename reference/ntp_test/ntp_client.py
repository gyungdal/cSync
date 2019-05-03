import ntplib
from adjust_time import set_sys_time
from time import ctime


c = ntplib.NTPClient()
response = c.request('europe.pool.ntp.org', version=3)
# response = c.request('127.0.0.1', port='12345')

print(ctime(response.tx_time))
set_sys_time(response.tx_time)
