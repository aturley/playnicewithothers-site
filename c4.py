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
from google.appengine.api import taskqueue
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
    interval = db.IntegerProperty()
    state = db.StringProperty()
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

def create_game_tasks(interval, game):
    for i in range(46):
        t = taskqueue.Task(url="/c4/timer", countdown=(interval * (i + 1)), params = {"game":game})
        t.add("c4timer")

def start_game():
    game = get_game_store()
    if (game.state == None):
        game.state = "playing"
        game.put()
        create_game_tasks(game.interval, game.game)
        send_start_game(game.interval)

def create_new_game(interval):
    games = db.GqlQuery("SELECT * FROM Game WHERE ANCESTOR IS :1 ORDER BY game DESC LIMIT 1", game_key())
    old_game_store = None
    if (games.count() != 0):
        for g in games:
            old_game_store = g
    game_store = Game(parent=game_key())
    if old_game_store:
        game_store.game = old_game_store.game + 1
    else:
        game_store.game = 0
    game_store.turn = 0
    game_store.interval = interval
    game_store.put()
    clear_board()
    send_new_game()
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

def send_player_count(player_count):
    data = {"type":"playercount", "count" : player_count}
    json_player_count = simplejson.dumps(data)
    game_id = "c4"
    displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
    for d in displays:
        channel.send_message(d.user_id + game_id, json_player_count)

def send_turn_finished(board, turn, winner, winning, interval):
    piece_map = {board.red:"r", board.black:"b", None:"_"}
    data = {"type":"turnfinished", "board":''.join([piece_map[x] for x in board.board_array]), "turn":turn, "winner":winner, "winning":winning, "interval":interval}
    json_turn_finished = simplejson.dumps(data)
    game_id = "c4"
    displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
    for d in displays:
        channel.send_message(d.user_id + game_id, json_turn_finished)

def send_new_game():
    data = {"type":"newgame"}
    json_new_game = simplejson.dumps(data)
    game_id = "c4"
    displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
    for d in displays:
        channel.send_message(d.user_id + game_id, json_new_game)

def send_start_game(interval):
    data = {"type":"startgame", "interval":interval}
    json_start_game = simplejson.dumps(data)
    game_id = "c4"
    displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 LIMIT 10", display_key())
    for d in displays:
        channel.send_message(d.user_id + game_id, json_start_game)

class MainPage(webapp.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        pass

class TimerHandler(webapp.RequestHandler):
    def handle(self):
        game_store = get_game_store()
        if game_store.state == "playing":
            game_id = "c4"
            game = self.request.get("game")
            if (game == ""):
                game = -1
            else:
                game = int(game)
            if (game_store.game == game):
                finish_turn()
    def get(self):
        self.handle()
    def post(self):
        self.handle()

def clear_board():
    board = c4board.Board()
    board_store = get_board_store()
    board.db_store_game_state(board_store)
    board_store.put()

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
        displays = db.GqlQuery("SELECT * FROM Display WHERE ANCESTOR IS :1 and user_id = :2", display_key(), user_id)

        display_store = None
        for d in displays:
            display_store = d

        if display_store == None:
            display_store = Display(parent=display_key())
            display_store.user_id = user_id
            display_store.put()

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
            v.put()
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
        game_state = get_game_store()
        send_player_count(len(game_state.red_team) + len(game_state.black_team))
        self.response.out.write(json_team)

class NewGameHandler(webapp.RequestHandler):
    def get(self):
        interval = self.request.get("interval")
        if interval == "":
            interval = 10
        else:
            interval = int(interval)
        create_new_game(interval)
        self.response.out.write("ok")

class StartGameHandler(webapp.RequestHandler):
    def get(self):
        start_game()
        self.response.out.write("ok")

class FinishTurnHandler(webapp.RequestHandler):
    def get(self):
        finish_turn()
        self.response.out.write("ok")

def finish_turn():
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
    move = None
    if len(valid_votes) == 0:
        move = random.randint(0,7)
    else:
        top = valid_votes[0][1]
        if (votes.count(top) == 1):
            # if no tie, use most popular
            move = valid_votes[0][0]
        else:
            # else, if there was a tie, pick random highest
            top_votes = [x[0] for x in valid_votes if x[1] == top]
            move = random.choice(top_votes)
    team_map = [board.black, board.red]
    board.play(team_map[game.turn % 2], move)
        
    win = board.find_winner()
    winning_team = None
    winning_spots = None
    if (win != None):
        win_map = {board.red:"red", board.black:"black"}
        winning_team = win_map[win[0]]
        winning_spots = win[1]
        game.state = "won"
        
    board.db_store_game_state(board_store)
    board_store.put()

    old_turn = game.turn

    game.turn += 1
    game.put()

    send_turn_finished(board, old_turn, winning_team, winning_spots, game.interval)

application = webapp.WSGIApplication([
        ('/c4', MainPage),
        ('/c4/timer', TimerHandler),
        ('/c4/team', TeamHandler),
        ('/c4/vote', VoteHandler),
        ('/c4/fakevotes', FakeVotes),
        ('/c4/board', BoardHandler),
        ('/c4/finishturn', FinishTurnHandler),
        ('/c4/newgame', NewGameHandler),
        ('/c4/startgame', StartGameHandler),
        ('/c4/channelbroker', ChannelBroker)])


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
