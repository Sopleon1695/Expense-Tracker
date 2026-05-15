from flask import Flask
from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/geek_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'geek_user'  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)  
    password = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow) 


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Successful")

#class Category(db.Model):
   # __tablename__ = 'user-category'
   # id =db.Column(db.Integer,primary_key=True)
   # user_id =db.Column(db.Integer,db.Foreignkey('geek-user.id'),nullable=False)
    #ctg_name =db.Column(db.String(50),nullable=False)
    #ctg_type =db.Column(db.String(50),nullable=False)
    




