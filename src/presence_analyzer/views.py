# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging

from flask import abort
from flask import redirect
from flask.ext.mako import render_template  # pylint: disable=no-name-in-module, import-error
from mako.exceptions import TopLevelLookupException

from main import app  # pylint: disable=relative-import
from utils import (  # pylint: disable=relative-import
    star_end_time,
    get_data,
    get_user,
    group_by_weekday,
    jsonify,
    mean
)


log = logging.getLogger(__name__)  # pylint: disable=invalid-name

links = {
    'presence_weekday.html': 'Presence by weekday',
    'mean_time_weekday.html': 'Presence mean time',
    'presence_start_end.html': 'Presence start-end',
}


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('presence_weekday.html')


@app.route('/<template>')
def dynamic_routes(template):
    """
    Create dynamic routes and render template.
    """
    try:
        active = links[template]
    except KeyError:
        active = None

    try:
        return render_template(
            template,
            pages=links,
            active=active,
        )
    except TopLevelLookupException:
        abort(404)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/users_xml', methods=['GET'])
@jsonify
def users_xml():
    """
    User listing for dropdown from xml file.
    """
    data = get_user()
    return [
        {
            'user_id': idx,
            'name': name['name'],
            'avatar': name['avatar']
        }
        for idx, name in data.iteritems()
    ]


@app.route('/api/v1/get_avatar/<int:user_id>', methods=['GET'])
@jsonify
def get_avatar(user_id):
    """
    Get user avatar path by id.
    """
    data = get_user()
    if str(user_id) not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    return {
        'user_id': user_id,
        'avatar': data[str(user_id)]['avatar']
    }


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]
    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end(user_id):
    """
    Return average time when user start the work and when user end the work.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)
    return star_end_time(data, user_id)
