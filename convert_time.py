from datetime import datetime
import time

format = '%a, %d %b %Y %H:%M:%S %Z'
str_format = '%d %b %Y %H:%M:%S'


def convert_time_str_to_epoch(date_str):
    utc_time = datetime.strptime(date_str, format)
    return utc_time.timestamp()


def convert_epoch_to_str(epoch):
    return time.strftime(str_format, time.localtime(epoch))


if __name__ == '__main__':
    epoch = convert_time_str_to_epoch('Sat, 21 Jul 2018 06:24:03 GMT')
    print(convert_epoch_to_str(epoch))