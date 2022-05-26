from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from web_forms import LoginForm, PostForm, NameForm, PasswordForm, UserForm

# create a Flask Instance
app = Flask(__name__)

# set the secret key
app.config['SECRET_KEY'] = 'mysecretkey'

# Add Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users'

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# create a blog post model


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    def __repr__(self):
        return 'Blog post ' + str(self.id)



# Create a class to represent the user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    password_hash = db.Column(db.String(120))

    @ property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @ password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return '<Name: {}>'.format(self.name)



# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




@ app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data,
                    author=form.author.data,
                    slug=form.slug.data)
        # clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # add the post to the database
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')

    return render_template('add_post.html', form=form)






# create dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
        except:
            flash('There was an issue updating the user')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    
    return render_template('dashboard.html')




# delete records from the database
@ app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = User.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('The user was successfully deleted')

        our_users = User.query.order_by(User.date_added)
        return render_template('add_user.html',
                               form=form,
                               name=name,
                               our_users=our_users)

    except:
        flash("There was a problem deleting the user. Try Again...")
        return render_template('add_user.html',
                               form=form,
                               name=name,
                               our_users=our_users)



# create logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('login'))


# create login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            # check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password')
        else:
            flash('No user found')
    return render_template('login.html', form=form)





@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted')
        posts = Post.query.order_by(Post.date_posted)
        return render_template('post.html', posts=posts)

    except:

        flash('Post was not deleted')
        posts = Post.query.order_by(Post.date_posted)
        return render_template('post.html', posts=posts)


@app.route('/posts/<int:id>')
def posts(id):
    post = Post.query.get_or_404(id)
    return render_template('posts.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # update the database
        db.session.add(post)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)


@app.route('/post')
def post():
    # Get the posts from the database
    posts = Post.query.order_by(Post.date_posted)
    return render_template('post.html', posts=posts)






# update database
@ app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = UserForm()
    name_to_update = User.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
        except:
            flash('There was an issue updating the user')
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


@ app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(
                form.password_hash.data, "sha256")
            user = User(username=form.username.data, name=form.name.data, email=form.email.data,
                        favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!')
    our_users = User.query.order_by(User.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@ app.route('/')
def index():

    flash('Welcome to my website')
    return render_template('index.html')


@ app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

    # create custom error pages

    # Invalid URL


@ app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server Error


@ app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# create name page


@ app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully!')
    return render_template('name.html', form=form, name=name)

# create password test page


@ app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():

    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    # validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # clear form
        form.email.data = ''
        form.password_hash.data = ''
        # Look up user by email
        pw_to_check = User.query.filter_by(email=email).first()

        # check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', form=form, email=email, password=password, pw_to_check=pw_to_check, passed=passed)


if __name__ == '__main__':
    app.run(debug=True)
