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
from google.appengine.ext import deferred
import c4board

def board_key():
    return db.Key.from_path('C4', 'board')

class Board(db.Model):
    """Models board state."""
    rows = db.IntegerProperty()
    columns = db.IntegerProperty()
    board_array = db.ListProperty(str)

def vote_key():
    return db.Key.from_path('C4', 'vote')

class Vote(db.Model):
    """Models votes."""
    user_id = db.StringProperty()
    vote = db.IntegerProperty()
    turn = db.IntegerProperty()
    game = db.IntegerProperty()

def game_key():
    return db.Key.from_path('C4', 'game')

class Game(db.Model):
    """Models the game."""
    red_team = db.ListProperty(str)
    black_team = db.ListProperty(str)
    # black goes first
    turn = db.IntegerProperty()
    game = db.IntegerProperty()
    next_user_team = db.StringProperty()
    def add_user_and_update(self, user_id):
        t = self.next_user_team
        if (t == None):
            t = "black"
        if (t == "black"):
            self.black_team.append(user_id)
            self.next_user_team = "red"
        else:
            self.red_team.append(user_id)
            self.next_user_team = "black"
        self.put()
        return t
    def can_user_vote(self, user_id):
        turn_map = ["black", "red"]
        if self.red_team.count(user_id) > 0:
            team = "red"
        elif self.black_team.count(user_id) > 0:
            team = "black"
        else:
            return False
        return turn_map[self.turn % 2] == team

def get_game_store():
    game_store = None
    try:
        games = db.GqlQuery("SELECT * FROM Game WHERE ANCESTOR IS :1 ORDER BY game DESC LIMIT 1", game_key())
        for g in games:
            game_store = g
    except:
        pass

    if (game_store == None):
        game_store = Game(parent=game_key());
        game_store.game = 0;
        game_store.turn = 0;
        game_store.put()
    return game_store

def create_new_game():
    games = db.GqlQuery("SELECT * FROM Game WHERE ANCESTOR IS :1 ORDER BY game ASC LIMIT 1", game_key())
    old_game_store = None
    if (games.count() != 0):
        for g in games:
            old_game_store = g
    game_store = Game(parent=game_key());
    game_store.game = old_game_store.game + 1
    game_store.turn = 0;
    game_store.put()
    return game_store

def get_user_team(user_id):
    game_store = get_game_store()
    if (game_store.red_team.count(user_id) > 0):
        return "red"
    if (game_store.black_team.count(user_id) > 0):
        return "black"

    # if we're here then the user is not on a team
    return game_store.add_user_and_update(user_id)

def display_key():
    return db.Key.from_path('C4', 'display')

class Display(db.Model):
    user_id = db.StringProperty()

def send_votes(votes):
    data = {"type":"votes", "votes" : votes}
    json_votes = simplejson.dumps(data)
    game_id = "c4"
    displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
    for d in displays:
        channel.send_message(d.user_id + game_id, json_votes)

def send_turn_finished(board, winner, winning):
    piece_map = {board.red:"r", board.black:"b", None:"_"}
    data = {"type":"turnfinished", "board":''.join([piece_map[x] for x in board.board_array]), "winner":winner, "winning":winning}
    json_turn_finished = simplejson.dumps(data)
    game_id = "c4"
    displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
    for d in displays:
        channel.send_message(d.user_id + game_id, json_turn_finished)

class MainPage(webapp.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        pass

class TimerHandler(object):
    def handleTimer(self):
        game_id = "c4"
        data = {"type" : "timer"}
        json_data = simplejson.dumps(data)
        displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
        for d in displays:
            channel.send_message(d.user_id + game_id, json_data)

def get_board_store():
    board_store = None
    try:
        boards = db.GqlQuery("SELECT * FROM Board WHERE ANCESTOR IS :1 LIMIT 1", board_key())
        board = c4board.Board();
        if (boards.count() != 0):
            for b in boards:
                board_store = b
    except:
        pass

    if (board_store == None):
        board_store = Board(parent=board_key());
        board.db_store_game_state(board_store)
        board_store.put()
    return board_store

class Play(webapp.RequestHandler):
    def get(self):
        board = c4board.Board()
        board_store = get_board_store()
        board.db_load_game_state(board_store)

class BoardHandler(webapp.RequestHandler):
    def get(self):
        board = c4board.Board()
        board_store = get_board_store()
        board.db_load_game_state(board_store)
        piece_map = {board.red:"r", board.black:"b", None:"_"}
        board_obj = {"board" : [piece_map[x] for x in board.board_array], "rows": board.rows, "columns" : board.columns}
        json_board = simplejson.dumps(board_obj)
        self.response.out.write(json_board)

class ChannelBroker(webapp.RequestHandler):
    def get(self):
        game_id = "c4"
        user_id = self.request.get("user_id")
        token = channel.create_channel(user_id + game_id)
        json_token = simplejson.dumps({"token" : token})
        self.response.out.write(json_token)
        displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
        if displays.count() == 0:
            display = Display(parent=display_key())
            display.user_id = user_id
            display.put()

class FakeVotes(webapp.RequestHandler):
    def get(self):
        votes = [int(x) for x in self.request.get("votes").split("_")]
        send_votes(votes)
        self.response.out.write(OK)

def get_turn_votes(turn, game):
    vote_list = [0] * 7
    votes = db.GqlQuery("SELECT * FROM Vote WHERE ANCESTOR IS :1 and turn = :2 and game = :3", vote_key(), turn, game)
    for v in votes:
        vote_list[v.vote] += 1
    return vote_list

def get_updated_votes(user_id, vote, turn, game):
    vote_list = [0] * 7
    votes = db.GqlQuery("SELECT * FROM Vote WHERE ANCESTOR IS :1 and turn = :2 and game = :3", vote_key(), turn, game)
    voted = False;
    for v in votes:
        if (v.user_id == user_id):
            v.vote = vote
            voted = True
            vote_list[vote] += 1
        else:
            vote_list[v.vote] += 1
    if not voted:
        vote_list[vote] += 1
        user_vote = Vote(parent=vote_key())
        user_vote.user_id = user_id
        user_vote.vote = vote
        user_vote.turn = turn
        user_vote.game = game
        user_vote.put()
    return vote_list

class VoteHandler(webapp.RequestHandler):
    def post(self):
        game_id = "c4"
        user_id = self.request.get("user_id")
        vote = int(self.request.get("vote"))
        game_store = get_game_store()
        if (game_store.can_user_vote(user_id)):
            votes = get_updated_votes(user_id, vote, game_store.turn, game_store.game)
            send_votes(votes)
        self.response.out.write("OK")

class TeamHandler(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        team = get_user_team(user_id)
        team_obj = {"team" : team}
        json_team = simplejson.dumps(team_obj)
        self.response.out.write(json_team)

class NewGameHandler(webapp.RequestHandler):
    def get(self):
        create_new_game()
        self.response.out.write("ok")

class FinishTurnHandler(webapp.RequestHandler):
    def get(self):
        board = c4board.Board()
        board_store = get_board_store()
        board.db_load_game_state(board_store)
        game = get_game_store()
        votes = get_turn_votes(game.turn, game.game)
        # get (position, votes) pairs
        vote_positions = [x for x in enumerate(votes)]

        # first, remove invalid votes
        valid_votes = []
        for i in range(7):
            if(board.test_play(i)):
                valid_votes.append(vote_positions[i])
            
        # sort the valid votes
        valid_votes.sort(cmp=lambda x, y: y[1] - x[1])

        # then check for ties
        top = valid_votes[0][1]
        move = None
        if (votes.count(top) == 1):
            # if no tie, use most popular
            move = valid_votes[0][0]
        else:
            # else, if there was a tie, pick random highest
            top_votes = [x[0] for x in valid_votes if x[1] == top]
            move = random.choice(top_votes)
        team_map = [board.black, board.red]
        board.play(team_map[game.turn % 2], move)
        
        # TODO: check for a winner
        
        board.db_store_game_state(board_store)
        board_store.put()

        game.turn += 1
        game.put()

        send_turn_finished(board, None, None)

        self.response.out.write("ok")

application = webapp.WSGIApplication([
        ('/c4', MainPage),
        ('/c4/team', TeamHandler),
        ('/c4/vote', VoteHandler),
        ('/c4/fakevotes', FakeVotes),
        ('/c4/board', BoardHandler),
        ('/c4/finishturn', FinishTurnHandler),
        ('/c4/newgame', NewGameHandler),
        ('/c4/channelbroker', ChannelBroker)])


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
