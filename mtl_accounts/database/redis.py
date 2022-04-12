import os

import redis


def redis_conn():
    try:
        REDIS_HOST = os.getenv("REDIS_HOST")
        REDIS_PORT = os.getenv("REDIS_PORT")
        REDIS_DATABASE = os.getenv("REDIS_DATABASE")
        rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)
    except:
        print("redis connection failure")
    return rd
