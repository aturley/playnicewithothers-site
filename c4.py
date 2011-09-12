import datetime
import logging
import os
import random
import re
from django.utils import simplejson
from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

def display_key():
    return db.Key.from_path('C4', 'display')

class Display(db.Model):
    user_id = db.StringProperty()


class MainPage(webapp.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        pass

class ChannelBroker(webapp.RequestHandler):
    def get(self):
        game_id = "c4"
        user_id = self.request.get("user_id")
        token = channel.create_channel(user_id + game_id)
        json_token = simplejson.dumps({"token" : token})
        self.response.out.write(json_token)
        display = Display(parent=display_key())
        display.user_id = user_id
        display.put()

class ControllerMessage(webapp.RequestHandler):
    def post(self):
        game_id = "c4"
        user_id = self.request.get("user_id")
        vote = self.request.get("vote")
        data = {"user_id" : user_id, "vote" : vote}
        json_token = simplejson.dumps(data)
        self.response.out.write(json_token)
        displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
        game_id = "c4"
        for d in displays:
            channel.send_message(d.user_id + game_id, json_token)

application = webapp.WSGIApplication([
        ('/c4', MainPage),
        ('/c4/controllermessage', ControllerMessage),
        ('/c4/channelbroker', ChannelBroker)])


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
