from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectField, FloatField, URLField
from wtforms.validators import DataRequired, URL, InputRequired


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Let me in!")


class CafeForm(FlaskForm):
    cafe_name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('Cafe location on Google Maps Share Link (URL)', validators=[DataRequired(), URL()])
    # img_url = URLField('Image (URL)')
    # location = StringField('Location', validators=[DataRequired()])
    sockets = SelectField('Does it have sockets?', choices=['Yes', 'No'], validators=[DataRequired()])
    toilet = SelectField('Does it have a toilet?', choices=['Yes', 'No'], validators=[DataRequired()])
    wifi = SelectField('Does it have wifi?', choices=['Yes', 'No'], validators=[DataRequired()])
    phone_friendly = SelectField('Can you take phone calls?', choices=['Yes', 'No'], validators=[DataRequired()])
    seats = SelectField('How many seats does it have?', choices=['0-10', '10-20', '20-30', '30-40', '40-50', '50+'], validators=[DataRequired()])
    coffee_price = FloatField('Coffee price:', validators=[InputRequired()])
    submit = SubmitField('Submit')
