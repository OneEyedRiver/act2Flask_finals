from flask import render_template, Flask, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import SubmitField, SearchField, RadioField, StringField, SelectField
from sqlalchemy import or_
from datetime import datetime
from wtforms.validators import DataRequired
app=Flask(__name__)
app.config['SECRET_KEY']='susi'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'

db=SQLAlchemy(app)

class Users(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    
    fullName=db.Column(db.String(50), nullable=False)
    institution=db.Column(db.String(50), nullable=False)
    email=db.Column(db.String(50), nullable=False)
    contact=db.Column(db.String(50), nullable=False)
    package=db.Column(db.String(50), nullable=False)

    date=db.Column(db.DateTime, default=datetime.utcnow)
    position=db.Column(db.String(50), nullable=False)
    department=db.Column(db.String(50), nullable=False)

def __repr__(self):
    return '<Name %r>' % self.name

class userForms(FlaskForm):
    fullName=StringField("Full Name", validators=[DataRequired()])
    institution=StringField("institution")
    email=StringField("email")
    contact=StringField("contact")
    package=RadioField("package", choices=[
        ("1000", "Seminar Fee"),
        ("5000", "Seminar Fee w/ accomodation"),
        ("8000", "Seminar Fee w/ food"),
    ])

    position=SelectField("package", choices=[
        ("President", "President"),
        ("Executive", "Executive"),
        ("Audience", "Audience"),
    ])
    department=SelectField("package", choices=[
        ("BSCS", "BSCS"),
        ("BSIT", "BSIT"),
        ("BSA", "BSA"),
    ])
    submit= SubmitField('Enter')



@app.route('/register', methods=['POST', 'GET'])
def register():
    form= userForms()

    if form.validate_on_submit():
        userExistAdd=Users.query.filter_by(email=form.email.data).first()

        if userExistAdd is None:
            newUser=Users(
                fullName=form.fullName.data,
                institution=form.institution.data,
                email=form.email.data,

                contact=form.contact.data,
                package=form.package.data,

                position=form.position.data,
                department=form.department.data,
            )

            db.session.add(newUser)
            db.session.commit()
            return redirect(url_for('register'))
    return render_template('register.html', form=form)


@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/viewz', methods=['POST','GET'])
def viewz():
    search=request.args.get('search')

    if search is None:
        all_users=Users.query.order_by(Users.date).all()
    else:
        all_users=Users.query.filter(or_(
            Users.institution.contains(search)
        )).order_by(Users.date).all()
    return render_template('viewz.html', all_users=all_users)