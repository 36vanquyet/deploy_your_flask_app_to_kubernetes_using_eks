'''
Tests for jwt flask app.
'''
import os
import json
import pytest

import main

SECRET = 'quyetc1-secret'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3MDAzOTE1NzcsIm5iZiI6MTY5OTE4MTk3NywiZW1haWwiOiJxdXlldGN2MUBlbWFpbC5jb20ifQ.7oN7mk9Z4V5mTjQjIHhUasEwH5VT0eXAzo05bxw4Cno'
EMAIL = 'quyetcv1@email.com'
PASSWORD = 'mypwd'

@pytest.fixture
def client():
    os.environ['JWT_SECRET'] = SECRET
    main.APP.config['TESTING'] = True
    client = main.APP.test_client()

    yield client



def test_health(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == 'Healthy'


def test_auth(client):
    body = {'email': EMAIL,
            'password': PASSWORD}
    response = client.post('/auth', 
                           data=json.dumps(body),
                           content_type='application/json')

    assert response.status_code == 200
    token = response.json['token']
    assert token is not None
