from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app=app
    db.init_app(app)

# Models

class User(db.Model):
    """ user class """

    __tablename__ = 'users'

    username = db.Column(db.String(20),
                         primary_key=True,
                         unique=True,
                         nullable=False)

    password = db.Column(db.Text,
                         nullable=False)
    
    email = db.Column(db.String(50),
                      unique=True,
                      nullable=False)
    
    first_name = db.Column(db.String(30),
                           nullable=False)
    
    last_name = db.Column(db.String(30),
                           nullable=False)
    
    feedback = db.relationship("Feedback", backref='user')
    
    def __repr__(self):
        return f'<User {self.first_name} / {self.last_name} / {self.username} / {self.email}>'
    
    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        """ register a user, hashing their password """

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')

        user = cls(username=username, password=hashed_utf8, first_name=first_name, last_name=last_name, email=email)
        
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """ validate that user exists and password is correct 
            return user if valid , false if incorrect 
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
class Feedback(db.Model):
    """ feedback class """

    __tablename__ = 'feedback'

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True)
    
    title = db.Column(db.String(100),
                        nullable=False)
    
    content = db.Column(db.Text,
                        nullable=False)
    
    username = db.Column(db.String(20),
                            db.ForeignKey('users.username', ondelete='CASCADE'),
                            nullable=False)
    
    def __repr__(self):
        return f'<Feedback {self.title} / {self.username}>'