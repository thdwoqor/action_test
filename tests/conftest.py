import os

import pytest
from faker import Faker
from mtl_accounts.main import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE = f'postgresql://{os.getenv("POSTGRESQL_USER")}:{os.getenv("POSTGRESQL_PASSWORD")}@{os.getenv("POSTGRESQL_HOST")}:{os.getenv("POSTGRESQL_PORT")}/{os.getenv("POSTGRESQL_DATABASE")}?client_encoding=utf8'


@pytest.fixture(scope="session")  # 테스트 실행시 한번만 실행
def app():
    app = create_app()
    return app


@pytest.fixture(scope="session")
def session():
    db = create_engine(DATABASE)
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db))


@pytest.fixture(scope="session")
def user():
    fake = Faker("ko_KR")
    return {
        "jti": "11111111-1111-1111-1111-111111111111",
        "type": "access",
        "fresh": "false",
        "displayName": fake.name(),
        "givenName": "null",
        "jobTitle": fake.job(),
        "mail": fake.email(),
        "provider": "office365",
        "role": "default",
    }
