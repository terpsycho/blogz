from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:alldemblogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    valid_routes = ['login', 'register', 'list_blogs', 'index']
    if request.endpoint not in valid_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("You are logged in, pal!")
            return redirect('/newpost')
        if not user:
            flash('This user does not exist. Soz.', 'error')
        elif user.password != password:
            flash('Wrong password. Try again or give up forever.', 'error')
            

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error = False
        existing_user = User.query.filter_by(username=username).first()


    #Username Errors
        if not username:
            flash('Worst user name ever. Also, it is invalid. Try again.', 'error') 
            username = ''
            error= True

        elif len(username) <= 2 or len(username) > 19:
            flash('Too short? Too long? One of these is true about your username. Try again.', 'error') 
            username = ''
            error= True

        elif ' ' in username:
            flash('Wedonotallowspacesinourusernames.', 'error') 
            username = ''
            error= True


    #Password Errors
        elif not password:
            flash('Invalid password. Enter a valid one.', 'error')
            error= True

        elif len(password) <= 2 or len(password) > 19:
            flash('Too short? Too long? One of these is true about your password. Try again.', 'error')
            error = True

        elif ' ' in password:
            flash('Wedonotallowspacesinourpasswords.', 'error')
            error= True




    #Verify Password Errors
        elif not verify == password:

            flash("The passwords do not match. Double check 'em!", 'error')
            error= True



    #Already Signed Up Errors
        elif username and existing_user:

            flash('Copycat! This user already exists. Login or try a different name.', 'error')
            error = True


    #No Errors 

        if not existing_user and not error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    
        else:
            password = ''
            verify = ''
            username = username
            

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods = ['GET'])
def index():
    users = User.query.all()

    id = request.args.get('id')
    blogs = Blog.query.filter_by(owner_id = id).all()

    if id:
        return render_template('one_user.html', blogs = blogs)
    else:
        return render_template('index.html', users = users)


@app.route('/blog', methods=['GET'])
def list_blogs():
    blogs = Blog.query.all()
    users = User.query.all()

    blog_id = request.args.get('id')
    blog = Blog.query.filter_by(id=blog_id).first()
  

    user_id = request.args.get('user_id')
    user_blogs = Blog.query.filter_by(owner_id = user_id).all()
    
    
    if blog_id:
        blog_user = blog.owner_id
        user = User.query.filter_by(id=blog_user).first()
        return render_template('one_post.html', blog=blog, user=user)
    
    
    elif user_id:
        return render_template('one_user.html', blogs=user_blogs)

    else: 
        return render_template('blog.html',title="Dis Lil Blog O' Mine!", 
            blogs=blogs, users=users)
    
  

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        owner_id = owner.id

        if title == "":
            flash("Put a title on your blog, friend.")
            return render_template('add_post.html', body = body)
        if body == "":
            flash("You can't have a blog without content. WRITE!")
            return render_template('add_post.html', title = title)
        
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        blog = Blog.query.filter_by(title=title).first()
        user = User.query.filter_by(id = owner_id).first()

        return render_template('one_post.html', blog = blog, user = user)

    else: 
        return render_template('add_post.html')

if __name__ == '__main__':
    app.run()