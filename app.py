from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_ckeditor import CKEditor
from sqlalchemy import true
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from web_forms import LoginForm, PostForm, NameForm, PasswordForm, UserForm, SearchForm
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# create a Flask Instance
app = Flask(__name__)
ckeditor = CKEditor(app)
# set the secret key
app.config['SECRET_KEY'] = 'mysecretkey'

# Upload folder
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Add Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://feoptvpmodxjze:3e542b105d161c13135e80efb84d3a923b90e2fbeb7ad7663a0b8599bf494327@ec2-3-226-163-72.compute-1.amazonaws.com:5432/d3g5rukiub3gtl'

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# create a blog post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    post_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Blog post ' + str(self.id)


# Create a class to represent the user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    password_hash = db.Column(db.String(120))
    profile_pic = db.Column(db.String(200), nullable=True)
    posts = db.relationship('Post', backref='poster', lazy=True)

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


@ app.route('/admin')
@ login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash('Sorry, must be admin to view this page!!!')
        return redirect(url_for('dashboard'))


@ app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Post(title=form.title.data,
                    content=form.content.data,
                    post_id=poster,
                    slug=form.slug.data)
        # clear the form
        form.title.data = ''
        form.content.data = ''
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
        name_to_update.about_author = request.form['about_author']

        # check for profile picture
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            # grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)

            # create a unique name for the image
            pic_name = str(uuid.uuid1()) + '_' + pic_filename

            # save the image
            saver = request.files['profile_pic']

            # save pic_filename to the database
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User Updated Successfully')
                return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
            except:
                flash('There was an issue updating the user')
                return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

        else:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)


# delete records from the database
@ app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
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
    else:
        flash('You are not authorized to delete this user')
        return redirect(url_for('dashboard'))


# create logout page
@ app.route('/logout', methods=['GET', 'POST'])
@ login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('login'))


# create login page
@ app.route('/login', methods=['GET', 'POST'])
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


@ app.route('/posts/delete/<int:id>')
@ login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:

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

    else:
        flash('Post was not deleted, you are not the author')
        posts = Post.query.order_by(Post.date_posted)
        return render_template('post.html', posts=posts)


@ app.route('/posts/<int:id>')
def posts(id):
    post = Post.query.get_or_404(id)
    return render_template('posts.html', post=post)


@ app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@ login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        # update the database
        db.session.add(post)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts', id=post.id))

    if current_user.id == post.poster.id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)

    else:
        flash('You are not the author of this post')
        posts = Post.query.order_by(Post.date_posted)
        return render_template('post.html', posts=posts)


@ app.route('/post')
def post():
    # Get the posts from the database
    posts = Post.query.order_by(Post.date_posted)
    return render_template('post.html', posts=posts)


# pass to navbar
@ app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# create search function
@ app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        # Get data from form
        post.searched = form.searched.data
        # query the database
        posts = posts.filter(Post.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Post.title).all()
        return render_template('search.html', form=form, searched=post.searched, posts=posts)


# update database
@ app.route('/update/<int:id>', methods=['GET', 'POST'])
@ login_required
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


@ app.route('/user/')
def user():

    return render_template('user.html')


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
