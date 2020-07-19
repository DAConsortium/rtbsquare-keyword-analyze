from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, password):
        self.id = id
        self.password = password
    