import time
from datetime import datetime
from babel.dates import format_date, parse_date

import config


class DateUtil:

    # Return naive datetime object in UTC
    @staticmethod
    def utcNow():
        return datetime.utcnow()

    # Return current epoch time
    @staticmethod
    def epoch():
        return int(time.time())
        # return int(time.mktime(time.gmtime()))

    # Return current local date
    @staticmethod
    def localDateNow():
        return datetime.now().date()

    # Return current local date in current language format
    @staticmethod
    def formattedLocalDateNow(format="short"):
        return DateUtil.formattedLocalDate(DateUtil.localDateNow(), format)

    # Return date in current language format
    @staticmethod
    def formattedLocalDate(date, format="short"):
        return format_date(date, format=format, locale=config.displayLanguage[:2])

    # Parse date string in language format into date object
    @staticmethod
    def parseDate(date):
        return parse_date(date, locale=config.displayLanguage[:2])

    # Convert datetime to UTC epoch datetime
    @staticmethod
    def datetimeToEpoch(dt):
        return int(dt.strftime('%s'))

    # Convert struct_time to epoch
    @staticmethod
    def stimeToEpoch(t):
        return time.mktime(t)

    # Seconds between local timezone and UTC timezone
    @staticmethod
    def secondsBetweenLocalAndUtc():
        return int(DateUtil.stimeToEpoch(time.gmtime()) - DateUtil.stimeToEpoch(time.localtime()))

def test_epoch():
    print(DateUtil.epoch())
    print(time.gmtime())
    print(time.localtime())
    print(DateUtil.stimeToEpoch(time.gmtime()))
    print(DateUtil.stimeToEpoch(time.localtime()))

    diff = DateUtil.secondsBetweenLocalAndUtc()
    print(diff)

def test_formats():
    config.displayLanguage = "en_US"
    dateStr = DateUtil.formattedLocalDateNow()
    print(dateStr)
    # 2/23/21
    config.displayLanguage = "zh"
    dateStr = DateUtil.formattedLocalDateNow()
    print(dateStr)
    # 2021/2/23
    config.displayLanguage = "de"
    dateStr = DateUtil.formattedLocalDateNow()
    print(dateStr)
    # 23.02.21
    dateObj = DateUtil.parseDate(dateStr)
    print(dateObj)
    # 2021-02-23
    print(DateUtil.localDateNow())
    # 2021-02-23

if __name__ == "__main__":
    test_formats()
