from dataclasses import dataclass
import bcrypt, datetime
from flask_login import UserMixin


class sample:
    """ define samples """
    pass

class run:
    """ define a run """
    pass

class result:
    pass

class preparation:
    pass

class pipeline:
    pass

class job:
    pass

class feature:
    pass

class cluster:
    pass

@dataclass
class HPLC_settings:
    column: str
    instrument: str
    gradient: str
    pressure: float
    flux: float
    temp: float


class User(UserMixin):
    def __init__(self, ID: int, username: str, email: str, password_hash: str):
        self.id = ID
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.datetime.now()
        self.user_dict = self.to_dict()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash
        }

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

