import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UsersModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return f"{self.login},{self.password}"


class WordModel(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String())
    word = db.Column(db.String())

    def __repr__(self):
        return f"{self.id}, {self.category}, {self.word}"


class UsersStatisticsModel(db.Model):
    __tablename__ = 'users_statistics'

    user_id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    games_num = db.Column(db.Integer(), default=0)
    win_rate = db.Column(db.Float(), default=0)
    wins_num = db.Column(db.Integer(), default=0)
    best_time = db.Column(db.DateTime(), default=0)
    cur_win_streak = db.Column(db.Integer(), default=0)
    best_win_streak = db.Column(db.Integer(), default=0)

    def __init__(self, user_id, games_num=0, win_rate=0, wins_num=0, best_time=datetime.datetime.now(),
                 cur_win_streak=0, best_win_streak=0):
        self.user_id = user_id
        self.games_num = games_num
        self.win_rate = win_rate
        self.wins_num = wins_num
        self.best_time = best_time
        self.cur_win_streak = cur_win_streak
        self.best_win_streak = best_win_streak

    def __repr__(self):
        return f"{self.user_id}, {self.games_num}, " \
               f"{self.win_rate},{self.wins_num}, " \
               f"{self.best_time}, {self.cur_win_streak}, " \
               f"{self.best_win_streak}"
