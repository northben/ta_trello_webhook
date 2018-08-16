
# encoding = utf-8

import os
import sys
import time
import datetime
import codecs
import json
import logging


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # trello_key = definition.parameters.get('trello_key', None)
    # trello_token = definition.parameters.get('trello_token', None)
    pass


def collect_events(helper, ew):
    token = helper.get_arg('trello_token')
    TRELLO_API_KEY = helper.get_arg('trello_key')
    index = helper.get_output_index()
    sourcetype = helper.get_sourcetype()
    input_type = helper.get_input_type() or '' + ':' + helper.get_arg('name') or ''

    params = {'token': token, 'key': TRELLO_API_KEY}

    helper.log_info('getting boards for key: {}'.format(TRELLO_API_KEY))

    boards = helper.send_http_request('https://api.trello.com/1/members/me/boards', 'get', parameters=params, payload=None, headers=None, cookies=None, verify=True, cert=None, timeout=None, use_proxy=True)
    try:
        boards = boards.json()
    except ValueError as e:
        helper.log_info('could not decode json for key: {}. response was: {}. error was {}. Exiting.'.format(TRELLO_API_KEY, boards, e))
        return        

    if len(boards) > 0:
        boards = [b['id'] for b in boards]
    else:
        helper.log_info('no boards for key: {}, exiting'.format(TRELLO_API_KEY))
        helper.log_info('boards: {}'.format(boards))
        return

    webhooks_json = helper.send_http_request('https://api.trello.com/1/tokens/{token}/webhooks/?key={key}'.format(token=token, key=TRELLO_API_KEY), 'get').json()

    webhooks = [w['idModel'] for w in webhooks_json]

    unsubscribed_boards = set(boards).difference(webhooks)
    
    helper.log_info('unsubscribed boards: {} key: {}'.format(unsubscribed_boards, TRELLO_API_KEY))

    for board in unsubscribed_boards:
        helper.log_info('requesting webhook for key: {}: board: {}'.format(TRELLO_API_KEY, board))

        webhook_params = {
            "idModel": board,
            "callbackURL": helper.get_arg('callback_url'),
            "description": input_type
        }

        webhook_request = helper.send_http_request('https://api.trello.com/1/tokens/{}/webhooks/?key={}'.format(token, TRELLO_API_KEY), 'post', parameters=webhook_params)
        helper.log_info('response for key: {} board: {}: '.format(TRELLO_API_KEY, board) + webhook_request.text)
