from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class CreatePost(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    subtitle=StringField('Subtitle',validators=[DataRequired()])
    image_url=StringField('Image URL',validators=[DataRequired()])
    body=CKEditorField('Body',validators=[DataRequired()])
    submit=SubmitField('Create Post')


class Register(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Register')


class Login(FlaskForm):
    email=StringField('Email',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Login')

class CommentForm(FlaskForm):
    comment=CKEditorField('',validators=[DataRequired()])
    submit=SubmitField('Post Comment')

