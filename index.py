#!/usr/bin/python3

from bottle import get

@get('/pastafari')
def home():

    return "Trick"


