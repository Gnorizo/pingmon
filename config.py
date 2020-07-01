from datetime import timezone

ITERATION_TIME = 300  # Seconds between re-testing the Internet connection
LOG_FILENAME = None  # Output to stdout
# LOG_FILENAME = './log'  # Output to log file
PING_TIMEOUT = 0.5  # Seconds for ping to timeout
TARGET_HOSTS = ('1.1.1.1', '8.8.8.8', '208.67.222.222')  # Cloudflare, Google, and OpenDNS DNS servers
TIMEZONE = timezone.utc  # Timezone for log entries
