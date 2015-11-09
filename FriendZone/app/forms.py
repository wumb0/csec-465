from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, SubmitField, BooleanField, DateField
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
            return False

class SignupForm(LoginForm):
    name      = StringField("Name:", validators=[DataRequired(), Length(max=50)])
    email     = StringField('Email:', validators=[Length(max=100), DataRequired()])
    birthday  = DateField('Birthday (MM/DD/YYYY):', validators=[DataRequired()], format='%m/%d/%Y')
    nickname  = StringField('Nickname:', validators=[Length(max=40)])
    bio       = TextAreaField('Bio:', validators=[Length(max=5000)])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired()])

    def validate_password(self, field):
        if not passpol.checkpw(self.password.data):
            raise ValidationError(", ".join(passpol.errors))
        return True

    def validate_confirm_password(self, field):
        if not self.password.data == self.confirm_password.data:
            raise ValidationError("Passwords do not match")
        return True

