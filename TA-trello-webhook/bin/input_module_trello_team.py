
# encoding = utf-8

import os
import sys
import time
import datetime


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # trello_team = definition.parameters.get('trello_team', None)
    # trello_key = definition.parameters.get('trello_key', None)
    # trello_token = definition.parameters.get('trello_token', None)
    # callback_url = definition.parameters.get('callback_url', None)
    pass

def collect_events(helper, ew):
    token = helper.get_arg('trello_token')
    team = helper.get_arg('trello_team')
    TRELLO_API_KEY = helper.get_arg('trello_key')
    index = helper.get_output_index()
    sourcetype = helper.get_sourcetype()
    input_type = helper.get_input_type() or '' + ':' + helper.get_arg('name') or ''
    input_name = helper.get_arg('name')
    callback_url = helper.get_arg('callback_url')

    params = {'token': token, 'key': TRELLO_API_KEY}

    helper.log_info('{}: getting boards for team: {}'.format(input_name, team))
    boards = helper.send_http_request('https://api.trello.com/1/organizations/{}/boards'.format(team), 'get', parameters=params, payload=None, headers=None, cookies=None, verify=True, cert=None, timeout=None, use_proxy=True)

    board_ids = [b['id'] for b in boards.json()]

    helper.log_info("{}: boards for team: {} are: {}".format(input_name, team, board_ids))

    subscribed_boards = helper.send_http_request('https://api.trello.com/1/tokens/{token}/webhooks/?key={key}'.format(token=token, key=TRELLO_API_KEY), 'get')

    subscribed_board_ids = [w['idModel'] for w in subscribed_boards.json()]

    helper.log_info('{}: subscribed boards are: {}'.format(input_name, subscribed_board_ids))

    unsubscribed_boards = set(board_ids).difference(subscribed_board_ids)

    helper.log_info('{}: unsubscribed boards are: {}'.format(input_name, unsubscribed_boards))

    for board in unsubscribed_boards:
        helper.log_info('{}: requesting webhook for board: {} with callback url: {}'.format(input_name, board, callback_url))

        webhook_params = {
            "idModel": board,
            "callbackURL": callback_url,
            "description": input_type
        }

        webhook_request = helper.send_http_request('https://api.trello.com/1/tokens/{}/webhooks/?key={}'.format(token, TRELLO_API_KEY), 'post', parameters=webhook_params)
        helper.log_info('{}: response for board: {}: {}'.format(input_name, board, webhook_request.text))
