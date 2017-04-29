# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import calendar
import csv
import threading
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from decorator import decorator
from functools import wraps
from json import dumps
from time import time
from xml.etree import ElementTree

from flask import Response

from main import app  # pylint: disable=relative-import

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
CACHE = {}


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def cache(timeout):
    """
    Cache data from wrapped function with timeout.
    """
    def cached(func, *args, **kwargs):
        """
        Cache data wrapper.
        """
        lock = threading.Lock()
        key = func.__name__

        with lock:
            if key in CACHE:
                age = time() - CACHE[key]['time']
                if age < timeout:
                    return CACHE[key]['result']

            result = func(*args, **kwargs)
            CACHE[key] = {
                'result': result,
                'time': time()
            }
            return result
    return decorator(cached)


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}
    return data


def get_user():
    """
    Extracts user name and avarat from XML file and groups it by user_id.
    """
    with open(app.config['DATA_XML'], 'r') as xmlfile:
        root = ElementTree.parse(xmlfile).getroot()

        for item in root.iter('server'):
            result = '{}://{}'.format(
                item.find('protocol').text,
                item.find('host').text
            )

        data = {
            user.attrib['id']: {
                'name': user.find('name').text,
                'avatar': '{}{}'.format(
                    result,
                    user.find('avatar').text
                )
            }
            for user in root.iter('user')
        }
    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def average_seconds(data, board):
    """
    Calculate average time in seconds and return it as string.
    """
    return str(
        timedelta(seconds=mean(data[board]))
    ).split(".")[0]


def star_end_time(data, user_id):
    """
    Calculate average time when user start the work and when user end the work.
    """
    days_abbr = calendar.day_abbr
    result = {day: {'start': [], 'end': []} for day in days_abbr}

    for item in data[user_id]:
        day = days_abbr[item.weekday()]

        result[day]['start'].append(
            seconds_since_midnight(
                data[user_id][item]['start']
            )
        )
        result[day]['end'].append(
            seconds_since_midnight(
                data[user_id][item]['end']
            )
        )
    for day in result:
        result[day]['start'] = average_seconds(result[day], 'start')
        result[day]['end'] = average_seconds(result[day], 'end')

    return result


def bussines_days(year_month):
    """
    Calculate seconds of worked days in month.
    """
    year, month = year_month
    date = datetime(
        year,
        month,
        calendar.monthrange(year, month)[1]
    )

    return sum([
        1 for x in xrange(1, date.day)
        if datetime(year, month, x).weekday() < 5
    ]) * (60 * 60 * 8)


def get_overtime(data):
    """
    Calculate user overtime and sort it.
    """
    names = get_user()
    result = defaultdict(dict)
    for user in data:
        if str(user) not in names.keys():
            continue
        for item in data[user]:
            start = seconds_since_midnight(
                data[user][item]['start']
            )
            end = seconds_since_midnight(
                data[user][item]['end']
            )
            overtime = end - start
            year_month = (item.year, item.month)

            if user not in result or year_month not in result[user]:
                result[user][year_month] = {'overtime': []}
            result_overtime = result[user][year_month]['overtime']
            result_overtime.append(overtime)

        result_overtime = sum(result_overtime)
        work_days = bussines_days(year_month)

        if result_overtime > work_days:
            finally_overtime = result_overtime - work_days

            if str(user) not in names.keys():
                continue
            result[user] = {
                'name': names[str(user)]['name'],
                'overtime': finally_overtime
            }
        try:
            if 'name' not in result[user][year_month]:
                del result[user]
        except KeyError:
            pass

    return sorted(
        result.items(),
        key=lambda result: result[1]['overtime'],
        reverse=True
    )
