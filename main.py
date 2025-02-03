from flask import Flask, render_template, redirect, url_for,request,flash,abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,relationship
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from form import CreatePost, Register, Login, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_gravatar import Gravatar
import os


'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''


    

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
Bootstrap5(app)

ckeditor = CKEditor()
ckeditor.init_app(app)


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id : Mapped[int] = mapped_column(Integer,db.ForeignKey("user.id"))
    author = relationship("User",back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class User(db.Model,UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(250), nullable=False)
    email: Mapped[str]=mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str]=mapped_column(String(250), nullable=False)
    posts= relationship("BlogPost",back_populates="author")
    comments=relationship("Comment",back_populates="author")

class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    post_id : Mapped[int] = mapped_column(Integer,db.ForeignKey("blog_post.id"))
    author_id : Mapped[int] = mapped_column(Integer,db.ForeignKey("user.id"))

    author=relationship("User",back_populates="comments")    



login_manager=LoginManager()
login_manager.init_app(app)

login_manager.login_view="login"


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)



def admin_only(func):
    
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return func(*args,**kwargs)
        else:
            abort(403)

    return wrapper



@app.route('/login',methods=["GET","POST"])
def login():
    
    f=Login()

    if f.validate_on_submit():
        email=f.email.data
        password=f.password.data

        user=User.query.filter_by(email=email).first()
        
        if not user:
            flash("Email does not exist")

        elif check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for("get_all_posts"))
       
        else:
            flash("Password is incorrect")
    return render_template("login.html",f=f)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))

@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = []

    result=db.session.execute(db.select(BlogPost)).scalars().all()

    posts=result

    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>',methods=["GET","POST"])
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    #requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id )).scalar()
    requested_post=db.get_or_404(BlogPost,post_id)
    f=CommentForm()


    if f.validate_on_submit():

        if not current_user.is_authenticated:
            flash("You need to login to comment")
            

        new_comment=Comment(comment=f.comment.data,post_id=post_id,author_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()

        CommentForm.comment.data=""
        f.comment.data=""

        return redirect(url_for("show_post",post_id=post_id))


       

    all_comments=db.session.execute(db.select(Comment).where(Comment.post_id == post_id )).scalars().all()
    print(all_comments)

    return render_template("post.html", post=requested_post,f=f,comments=all_comments)


@app.route('/create_post',methods=["GET","POST"])
@login_required
def add_new_post():

    f=CreatePost()

    if f.validate_on_submit():
        new_post=BlogPost(title=f.title.data,
                          subtitle=f.subtitle.data,
                          date=date.today(),
                          img_url=f.image_url.data,
                          author_id=current_user.id,
                          body=f.body.data)

        with app.app_context():
            db.session.add(new_post)
            db.session.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html",f=f)


@app.route("/edit_post/<int:post_id>",methods=["GET","POST"])
@login_required
def edit_post(post_id):
    f=CreatePost()

    if f.validate_on_submit():
        result=db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()

        result.title=f.title.data
        result.subtitle=f.subtitle.data
        result.img_url=f.image_url.data
        result.author_id=current_user.id
        result.body=f.body.data

        db.session.commit()
        return redirect(url_for("get_all_posts"))

    else:

        result=db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()

        f.title.data=result.title
        f.subtitle.data=result.subtitle
        f.image_url.data=result.img_url
        f.body.data=result.body

        return render_template("edit-post.html",f=f)


@app.route("/delete-post/<post_id>")
@admin_only
def delete_post(post_id):

    result=db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(result)
    db.session.commit()


    return redirect(url_for("get_all_posts"))

@app.route("/register",methods=["GET","POST"])
def register():
    f=Register()
   
    if f.validate_on_submit():
        email=f.email.data
        password=generate_password_hash(f.password.data,"pbkdf2:sha256")
        name=f.name.data

        new_user=User(name=name,email=email,password=password)

        user=db.session.execute(db.select(User).where(User.email==email)).scalar()

        if user:
            flash("You have already registered with email " + email)
            return redirect(url_for("login"))


        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("get_all_posts"))


    return render_template("register.html",f=f)





# TODO: add_new_post() to create a new blog post

# TODO: edit_post() to change an existing blog post

# TODO: delete_post() to remove a blog post from the database

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
