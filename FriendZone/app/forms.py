from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, SubmitField, BooleanField, DateField, widgets, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.fields import TextAreaField
from app.crypto import compare, PassPolicy
from app.models import *

passpol = PassPolicy(length=10, classes=3)

class LoginForm(Form):
    email    = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit   = SubmitField('Submit')

    def validate_password(self, field):
        try:
            user = User.query.filter_by(email=self.email.data).one()
            if not compare(self.password.data, user.password):
                raise Exception
            return True
        except:
            raise ValidationError("Invalid username or bad password")

class SignupForm(LoginForm):
    name      = StringField("Name:", validators=[DataRequired(), Length(max=50)])
    email     = StringField('Email:', validators=[Length(max=100), DataRequired()])
    birthday  = DateField('Birthday (MM/DD/YYYY):', validators=[DataRequired()], format='%m/%d/%Y')
    nickname  = StringField('Nickname:', validators=[Length(max=40)])
    bio       = TextAreaField('Bio:', validators=[Length(max=5000)])
    linkname  = StringField('Link Name:', validators=[DataRequired(), Length(max=20)])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired()])

    def validate_password(self, field):
        if not passpol.checkpw(self.password.data):
            raise ValidationError(", ".join(passpol.errors))
        return True

    def validate_confirm_password(self, field):
        if not self.password.data == self.confirm_password.data:
            raise ValidationError("Passwords do not match")
        return True

    def validate_linkname(self, field):
        if len(User.query.filter_by(linkname=field.data).all()):
            raise ValidationError("That linkname has already been chosen!")

    def validate_email(self, field):
        if len(User.query.filter_by(email=field.data).all()):
            raise ValidationError("That email address is already in use")

    def validate_birthday(self, field):
        if field.data.year < 1900:
            raise ValidationError("Year must be => 1900")

class CKTextAreaWidget(widgets.TextArea):
    '''Fancy text editor widget
    Parent: wtforms.widgets.TextArea
    '''
    def __call__(self, field, **kwargs):
        '''Make the class of the widget ckeditor so the input box is replaced
        with CKEditor
        Returns: the result of the parent __call__ function
        '''
        if kwargs.get('class'):
            kwargs['class'] += " ckeditor"
        else:
            kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    '''Fancy text editor field
    Parent: wtforms.fields.TextAreaField
    Attribute:
        widget - the CKTextAreaWidget to use for this text area
    '''
    widget = CKTextAreaWidget()

class PostForm(Form):
    content = CKTextAreaField('Content', validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField("Submit")

class SearchForm(Form):
    query = StringField('Search for: ', validators=[DataRequired(), Length(max=200)])
    search_type = SelectField("Search type", validators=[DataRequired()], choices=[("Users", "Users"), ("Posts", "Posts")])
    submit = SubmitField("Search!")
