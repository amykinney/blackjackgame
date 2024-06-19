#!/usr/local/bin/python3

from wsgiref.handlers import CGIHandler

from flaskapp.app import app

CGIHandler().run(app)
