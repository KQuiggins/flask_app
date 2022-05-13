from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    favorite_pizza = ["Peperoni", "Cheese", "Hawaiian"]
    first_name = "Kenny"
    stuff = "This is some bold text"
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


if __name__ == '__main__':
    app.run(debug=True)
