__author__ = 'mrkaiser'


from rdio import Rdio
from rdio_consumer_credentials import RDIO_CREDENTIALS
import logging
from flask import Flask, session, redirect, make_response, request

app = Flask(__name__)


@app.route('/login')
def login():
    #clear all of our auth cookies
    #begin auth
    rdio = Rdio(RDIO_CREDENTIALS)
    app.logger.debug(request.host)
    url = rdio.begin_authentication(callback_url='http://'+request.host+'/callback')
    redirect_to_rdio = redirect(url)
    #save our request token in cookies
    response = make_response(redirect_to_rdio)
    app.logger.info(rdio.token)
    response.set_cookie('rt', rdio.token[0], expires=60*60*24)
    response.set_cookie('rts', rdio.token[1], expires=60*60*24)
    #go to Rdio to authenticate the app
    return response

@app.route('/callback')
def callback():
    app.logger.info('yayyyyyy')
    #get the state from cookies and the query string
    request_token = request.cookies.get('rt')
    request_token_secret = request.cookies.get('rts')
    verifier = request.args['oauth_verifier']
    app.logger.info(request_token+'rts'+request_token_secret+'verifer'+verifier)
    #make sure we have everything we need
    if request_token and request_token_secret and verifier:
        rdio = Rdio(RDIO_CREDENTIALS, (request_token, request_token_secret))
        rdio.complete_authentication(verifier)
        app.logger.info('blah'+rdio.token)
        redirect_to_home = redirect('/')
        response = make_response(redirect_to_home)
        app.logger.info(rdio.token[0])
        response.set_cookie('at', rdio.token[0], expires=60*60*24*14)   # expires in two weeks
        response.set_cookie('ats', rdio.token[1], expires=60*60*24*14)  # expires in two weeks
        response.set_cookie('rt', '', expires=-1)
        response.set_cookie('rts', '', expires=-1)
        return response
    else:
        response_to_home = make_response(redirect('/'))
        return response_to_home

@app.route('/')
def hello():
    return 'Hello'


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True)