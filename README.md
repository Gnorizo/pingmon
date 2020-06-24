# pingmon
Internet Connection Monitor

Periodically test Internet connectivity by pinging a set of highly reliable
public hosts, specifically the DNS servers for Cloudflare, Google, and
OpenDNS. If none of the hostsvrespond to a ping, then log an Internet outage.

To install:
- Install Python 3
- python3 -m venv .venv
- export PATH=.venv/bin:$PATH
- pip install -r requirements.txt

To run:
- Edit constants in pingmon.py to taste, e.g. ITERATION_TIME and LOG_FILENAME
- sudo python3 pingmon.py
