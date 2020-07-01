'''Internet Connection Monitor

Periodically test Internet connectivity by pinging a set of highly reliable public hosts,
specifically the DNS servers for Cloudflare, Google, and OpenDNS. If none of the hosts
respond to a ping, then log an Internet outage.

Copyright (c) 2020 Chris Russell (Gnorizo)
'''

import os
import ping3
import sys
from config import *
from datetime import datetime, timedelta, timezone
from humanfriendly import format_timespan
from time import sleep

ITERATION_TIME = min(ITERATION_TIME, 3600)  # Max iteration time is hourly
ping3.EXCEPTIONS = True  # Throw exception if ping fails: timeout, unknown host, host unreachable, etc.

def is_internet_up():
    '''Return True if any host in TARGET_HOSTS responds to a ping, or False if not'''
    for host in TARGET_HOSTS:
        try:
            ping3.ping(host, timeout=PING_TIMEOUT)
            return True
        except PermissionError:
            sys.exit('pingmon: must run as root')
        except:
            continue  # Ping failed, try next host
    return False

def roundbase(x, prec=0, base=10):
    '''Round to the nearest multiple of a base number, supports floats if prec > 0'''
    return round(base * round(float(x) / base), prec)

def midnight(dt):
    '''Return datetime with time zeroed to midnight (00:00:00), preserves timezone'''
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def seconds(starttime, endtime):
    '''Return the numnber of seconds between starttime and endtime, rounded to ITERATION_TIME'''
    return roundbase((endtime - starttime).total_seconds(), base=ITERATION_TIME)

def seconds_today(starttime, now):
    '''Return the number of seconds between starttime and now that occured today, rounded to ITERATION_TIME'''
    return seconds(max(starttime, midnight(now)), now)

def seconds_yesterday(starttime, now):
    '''Return the number of seconds between starttime and now that occured yesterday, rounded to ITERATION_TIME'''
    today = midnight(now)
    yesterday = today - timedelta(days=1)
    return seconds(max(starttime, yesterday), today) if starttime < today else 0

def timestamp(dt):
    '''Return datetime in ISO 8601 string format'''
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ') if dt.tzinfo is timezone.utc else dt.isoformat()

with (
    open(LOG_FILENAME, 'a', buffering=1)
    if LOG_FILENAME else
    os.fdopen(os.dup(sys.stdout.fileno()), 'w')  # Log to stdout if LOG_FILENAME is None
) as logfile:

    been_up = is_internet_up()
    monitor_starttime = datetime.now(TIMEZONE)  # Time that monitoring started
    event_starttime = monitor_starttime  # Time of last event: Internet went up or down, or monitoring started
    today = midnight(monitor_starttime)
    total_time = [0, 0]  # total_time[up]: [True] = today's uptime, [False] = today's downtime

    logfile.write('{}: Testing Internet connection every {}\n'.format(
        timestamp(monitor_starttime),
        format_timespan(ITERATION_TIME))
    )
    logfile.write('{}: Internet {}\n'.format(timestamp(monitor_starttime), 'UP' if been_up else 'DOWN'))

    while True:
        now = datetime.now(TIMEZONE)

        if midnight(now) > today:  # Log the prior day's total downtime
            total_time[been_up] += seconds_yesterday(event_starttime, now)
            logfile.write('{}: Total downtime for {} was {} ({:.2%})\n'.format(
                timestamp(now),
                today.date(),
                format_timespan(total_time[False]),  # Total downtime
                total_time[False] / sum(total_time)  # Percentage downtime
            ))
            today = midnight(now)
            total_time = [0, 0]

        if is_internet_up() != been_up:  # New event: Connectivity changed from DOWN->UP or UP->DOWN
            total_time[been_up] += seconds_today(event_starttime, now)
            logfile.write('{}: Internet {} was {}\n'.format(
                timestamp(now),
                'DOWN: Uptime' if been_up else 'UP: Downtime',
                format_timespan(seconds(event_starttime, now), max_units=2)
            ))
            been_up = not been_up
            event_starttime = now

        sleep(ITERATION_TIME - ((datetime.now(TIMEZONE) - monitor_starttime).seconds % ITERATION_TIME))
