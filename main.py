from functools import wraps
from flask import Flask, Markup, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, CafeForm
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import get_map_code, get_map_place_img

API_KEY = '####GOOGLE MAPS API KEY####'
G_API = 'https://www.google.com/maps/embed/v1/place?'
PLACEHOLDER_MAP = f'https://www.google.com/maps/embed/v1/place?key={API_KEY}&q=place_id:ChIJPXZIogjRrBQRoDgTb_rRcGQ'

db = SQLAlchemy()
app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] ='####A SECRET KEY####'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafe_and_wifi.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

db = SQLAlchemy(app)
ckeditor = CKEditor(app)
login_manager = LoginManager(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250))
    has_sockets = db.Column(db.Integer)
    has_toilet = db.Column(db.Integer)
    has_wifi = db.Column(db.Integer)
    can_take_calls = db.Column(db.Integer)
    seats = db.Column(db.Integer)
    coffee_price = db.Column(db.Integer)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


app.app_context().push()
db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.id != 1:
                return abort(403)
            else:
                return f(*args, **kwargs)
        return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    all_cafes = db.session.query(Cafe).all()

    # Set a placeholder card info
    cafe_info = Cafe.query.get(0)
    new_info = request.args.get('cafe_id')
    if new_info:
        cafe_info = Cafe.query.get(new_info)
    cafe_query_code = get_map_code(cafe_name='Science Gallery London', cafe_location='London Bridge')
    map_code = f'https://www.google.com/maps/embed/v1/place?key={API_KEY}&q=place_id:{cafe_query_code}'

    #Get data for selected cafe from info btn
    cafe_name = request.args.get('cafe_name')
    cafe_loc = request.args.get('cafe_loc')

    # Get google maps data for selected cafe
    if cafe_name:
        cafe_query_code = get_map_code(cafe_name, cafe_loc)
        map_code = f'https://www.google.com/maps/embed/v1/place?key={API_KEY}&q=place_id:{cafe_query_code}'
    return render_template("index.html", cafes=all_cafes, cafe_info=cafe_info, map_code=map_code)


@login_required
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    map_code = PLACEHOLDER_MAP
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to add a Cafe.")
            return redirect(url_for("login"))
        else:
            # Change form data from str into int
            list_answers = [form.sockets.data, form.toilet.data, form.wifi.data, form.phone_friendly.data]
            numeric_answers = [1 if item == 'Yes' else 0 for item in list_answers]

            # Try to fetch data from google maps
            try:
                cafe_name, img, location = get_map_place_img(form.map_url.data)
            except:
                flash("An unexpected error accrued. Please try again.")
                return redirect(url_for("add_cafe"))

            # Check for existing cafe and correct url
            if Cafe.query.filter_by(name=cafe_name).first():
                flash("This cafe already exists")
                return redirect(url_for('add_cafe'))

            if 'goo.gl' not in form.map_url.data:
                flash(Markup('Please use a proper share link from google maps :)'
                             '<a href="https://support.google.com/maps/answer/144361?hl=en&co=GENIE.Platform%3DAndroid"'
                             'class="alert-link" target="blank_"> See how</a>'))
                return redirect(url_for('add_cafe'))

            # Add new cafe to db
            new_cafe = Cafe(
                name=cafe_name,
                map_url=form.map_url.data,
                img_url=img,
                location=location,
                has_sockets=numeric_answers[0],
                has_toilet=numeric_answers[1],
                has_wifi=numeric_answers[2],
                can_take_calls=numeric_answers[3],
                seats=form.seats.data,
                coffee_price=f'${str(form.coffee_price.data)}',
            )
            db.session.add(new_cafe)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template('cafe_add.html', form=form, map=map_code)


@admin_only
@app.route("/edit-cafe/<int:cafe_id>", methods=["GET", "POST"])
def edit_cafe(cafe_id):
    map_code = PLACEHOLDER_MAP
    cafe = Cafe.query.get(cafe_id)
    edit_form = CafeForm(
        cafe_name=cafe.name,
        map_url=cafe.map_url,
        coffee_price=str(cafe.coffee_price).strip('$'),
    )
    if edit_form.validate_on_submit():
        # Check if URL is good /Only google maps SHARE url will work/
        if 'goo.gl' not in edit_form.map_url.data:
            flash(Markup('Please use a proper share link from google maps :)'
                         '<a href="https://support.google.com/maps/answer/144361?hl=en&co=GENIE.Platform%3DAndroid"'
                         'class="alert-link" target="blank_"> See how</a>'))
            return redirect(url_for('edit_cafe', cafe_id=cafe_id))

        cafe.name = edit_form.cafe_name.data
        cafe.map_url = edit_form.map_url.data
        cafe.has_sockets = edit_form.sockets.data
        cafe.has_toilet = edit_form.toilet.data
        cafe.has_wifi = edit_form.wifi.data
        cafe.can_take_calls = edit_form.phone_friendly.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = f'${str(edit_form.coffee_price.data)}'
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('cafe_add.html', form=edit_form, map=map_code, cafe=cafe, is_edit=True)


@admin_only
@app.route("/delete/<int:cafe_id>")
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if exists
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('register'))

        # Add new user
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_email = form.email.data
        login_password = form.password.data
        user = User.query.filter_by(email=login_email).first()

        if user:
            if check_password_hash(user.password, login_password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Wrong Password, please try again.')
                return redirect(url_for('login'))
        else:
            flash('That Email does not exist, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, debug=True)
