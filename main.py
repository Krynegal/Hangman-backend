import time
from datetime import datetime
from random import randint

import flask
import psycopg2
import sqlalchemy.exc
from flask import request
from flask_migrate import Migrate
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey, DateTime

from models import db, UsersModel, WordModel
from models import UsersStatisticsModel
import statistic as stat
import os
from dotenv import load_dotenv

load_dotenv()

app = flask.Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/game/word', methods=['GET'])
def get_word():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    metadata = MetaData(engine)
    if not sqlalchemy.inspect(engine).has_table("words"):
        words = Table('words', metadata,
                      Column('id', Integer(), primary_key=True),
                      Column('category', String(200), nullable=False),
                      Column('word', String(200), unique=True, nullable=False))
        metadata.create_all()

    word_count_db = db.session.query(WordModel).count()
    if word_count_db != 0:
        rand_id = randint(1, word_count_db)
        word = db.session.query(WordModel).get(rand_id)
        word_dict = vars(word)
        word_dict.pop("_sa_instance_state")
        print(word_dict)
        return word_dict
    return {"word": ""}


@app.route('/stats/<userId>', methods=['GET'])
def stats_get(userId):
    userId = int(userId)
    user_stat = db.session.query(UsersStatisticsModel).get(int(userId))
    user_stat_dict = vars(user_stat)
    print(user_stat_dict)
    user_stat_dict.pop("_sa_instance_state")
    dt = str(user_stat_dict.pop("best_time"))
    user_stat_dict["best_time"] = dt[-6::]
    print(user_stat_dict)
    return user_stat_dict


@app.route('/stats', methods=['POST'])
def update_stats():
    json = request.get_json()
    print(json)

    won = json["won"]
    user_id = json["user_id"]
    # получаем запись пользователя
    user_stat = db.session.query(UsersStatisticsModel).get(user_id)
    user_stat_dict = vars(user_stat)
    print(user_stat_dict)
    cur_games_num = user_stat_dict["games_num"]
    cur_wins_num = user_stat_dict["wins_num"]
    cur_best_time = user_stat_dict["best_time"]
    # cur_avg_time = user_stat_dict["avg_time"]
    cur_win_streak = user_stat_dict["cur_win_streak"]
    cur_best_win_streak = user_stat_dict["best_win_streak"]

    # update games num
    cur_games_num += 1
    user_stat.games_num = cur_games_num

    # update wins num
    wins_num = 1 if won else 0
    cur_wins_num += wins_num
    user_stat.wins_num = cur_wins_num

    if won:
        # update best time
        duration = float(json["duration"])
        duration_timestamp = stat.get_time_from_unix_time(duration)
        print("duration_timestamp: ", duration_timestamp)
        if duration_timestamp < cur_best_time:
            user_stat.best_time = duration_timestamp


    # update win rate
    win_rate = cur_wins_num / cur_games_num
    user_stat.win_rate = win_rate

    # update win streak
    if won:
        cur_win_streak += 1
        user_stat.cur_win_streak = cur_win_streak
        # update best win streak
        if cur_win_streak > cur_best_win_streak:
            user_stat.best_win_streak = cur_win_streak
    else:
        user_stat.cur_win_streak = 0

    print(vars(user_stat))
    db.session.commit()
    return "get stats"


@app.route('/users/signUp', methods=['POST'])
def signUp():
    print("sign up")
    json = request.get_json()
    print(json)
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    metadata = MetaData(engine)
    if not sqlalchemy.inspect(engine).has_table("users"):
        users = Table('users', metadata,
              Column('id', Integer(), primary_key=True),
              Column('login', String(200), unique=True, nullable=False),
              Column('password', String(200), nullable=False))
        users_stat = Table('users_statistics', metadata,
              Column('user_id', Integer(), ForeignKey('users.id'), primary_key=True),
              Column('games_num', Integer()),
              Column('win_rate', Float()),
              Column('wins_num', Integer()),
              Column('best_time', DateTime()),
              Column('cur_win_streak', Integer()),
              Column('best_win_streak', Integer()))
        metadata.create_all()


    login = json['login']
    password = json['password']
    new_user = UsersModel(login=login, password=password)
    login = db.session.query(UsersModel).filter_by(login=login).first()
    if not login:
        # создаем юзера
        db.session.add(new_user)
        db.session.commit()
        print(new_user.id, new_user)
        # создаем статистику юзера
        new_user_stat = UsersStatisticsModel(user_id=new_user.id)
        db.session.add(new_user_stat)
        db.session.commit()
        return {"id": new_user.id, "login": login}
    return {"id": -1}


@app.route('/users/login', methods=['POST'])
def login():
    json = request.get_json()
    print(json)
    login = json['login']
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    if sqlalchemy.inspect(engine).has_table("users"):
        if db.session.query(UsersModel).filter_by(login=login).first():
            user = db.session.query(UsersModel.id, UsersModel.login, UsersModel.password).filter_by(login=login).all()[0]
            if user[2] == json["password"]:
                return {"id": user[0], "login": user[1]}
    return {"id": -1}


app.run(host="0.0.0.0", port=5000, debug=True)
