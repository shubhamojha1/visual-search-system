from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ImageIndex(db.model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    embedding = db.Column(LargeBinary, nullable=False)

    def __repr__(self):
        return f'<ImageIndex {self.filename}>'