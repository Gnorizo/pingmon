'''Internet Connection Monitor

Periodically test Internet connectivity by pinging a set of highly reliable public hosts,
specifically the DNS servers for Cloudflare, Google, and OpenDNS. If none of the hosts
respond to a ping, then log an Internet outage.

Copyright (c) 2020 Chris Russell (Gnorizo)
'''

import ping3
from datetime import datetime, timezone
from humanfriendly import format_timespan
from time import sleep, time

ITERATION_TIME = 300  # Seconds before re-testing Internet connection
PING_TIMEOUT = 0.5  # Seconds for ping to timeout
LOG_FILENAME = './log'  # Output logfile
TARGET_HOSTS = ('1.1.1.1', '8.8.8.8', '208.67.222.222')  # Cloudflare, Google, and OpenDNS DNS servers

ping3.EXCEPTIONS = True  # Throw exception if ping fails: timeout, unknown host, host unreachable, etc.

def is_internet_up():
	'''Returns True if any host in TARGET_HOSTS responds to a ping, or False if none do'''
	for host in TARGET_HOSTS:
		try:
			ping3.ping(host, timeout=PING_TIMEOUT)
			return True
		except:
			continue  # Ping failed, try next host
	return False

def timestamp():
	'''Returns current UTC datetime in ISO 8601 string format'''
	return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def roundbase(x, prec=0, base=10):
	'''Round to the nearest multiple of a base number, supports floats if prec > 0'''
	return round(base * round(float(x) / base), prec)

with open(LOG_FILENAME, 'a') as logfile:

	was_up = is_internet_up()
	monitor_starttime = updown_starttime = time()
	logfile.write('{}: Testing Internet connection every {}\n'.format(timestamp(), format_timespan(ITERATION_TIME)))
	logfile.write('{}: Internet {}\n'.format(timestamp(), 'UP' if was_up else 'DOWN'))
	logfile.flush()

	while True:
		if is_internet_up() != was_up:  # Connectivity changed, either from up->down or down->up
			updown_change = 'DOWN: Uptime' if was_up else 'UP: Downtime'
			updown_time = format_timespan(roundbase(time() - updown_starttime, base=ITERATION_TIME), max_units=2)
			logfile.write('{}: Internet {} was {}\n'.format(timestamp(), updown_change, updown_time))
			logfile.flush()
			was_up = not was_up
			updown_starttime = time()
		sleep(ITERATION_TIME - ((time() - monitor_starttime) % ITERATION_TIME))
