from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# create a Flask Instance
app = Flask(__name__)

# set the secret key
app.config['SECRET_KEY'] = 'mysecretkey'

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize the database
db = SQLAlchemy(app)

# Create a class to represent the user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Create a String
    def __repr__(self):
        return '<Name: {}>'.format(self.name)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    return render_template('add_user.html')



@app.route('/')
def index():
    favorite_pizza = ["Peperoni", "Cheese", "Hawaiian"]
    first_name = "Kenny"
    stuff = "This is some bold text"
    flash('Welcome to my website')
    return render_template('index.html', first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# create custom error pages

# Invalid URL


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server Error


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# create name page


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully!')
    return render_template('name.html', form=form, name=name)


if __name__ == '__main__':
    app.run(debug=True)
