import time


class DateUtil:

    def epoch():
        return int(time.mktime(time.gmtime()))
