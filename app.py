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
    
    reference_no=db.Column(db.String(50), nullable=True, unique=True)
    payment_date=db.Column(db.DateTime, nullable=True)
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
    reference_no=StringField('Reference No.')
    submit= SubmitField('Enter')



@app.route('/register', methods=['POST', 'GET'])
@app.route('/register/<int:id>', methods=['POST', 'GET'])
def register(id = None):
    form= userForms()
    search= request.args.get('search')
    isUpdate=id is not None
    user_to_edit=Users.query.get(id) if isUpdate else None

    setdate= datetime(2025,11,9)
    
    
    if form.validate_on_submit():

        if isUpdate is False:
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

                    reference_no=None if form.reference_no.data == "" else form.reference_no.data,

                    payment_date = None if form.reference_no.data == "" else datetime.utcnow()

                )

                db.session.add(newUser)
                db.session.commit()
                flash("User Added", 'success')
                return redirect(url_for('register'))
            else:
                flash("Email Already Exist", "warning")
        else:
            userExistEdit=Users.query.filter(Users.email == form.email.data, Users.id != id).first()

            if userExistEdit is None:
                
                user_to_edit.fullName=form.fullName.data
                user_to_edit.institution=form.institution.data
                user_to_edit.email=form.email.data

                user_to_edit.contact=form.contact.data
                user_to_edit.package=form.package.data

                user_to_edit.position=form.position.data
                user_to_edit.department=form.department.data

                user_to_edit.reference_no=None if form.reference_no.data == "" else form.reference_no.data
                user_to_edit.payment_date = None if form.reference_no.data == "" else datetime.utcnow()
                try:
                    db.session.commit()
                    flash("Success Updating", "success")
                    return redirect(url_for('register'))
                except:
                    flash("Failed Updating", "warning")
    if search:
        selected=Users.query.filter(Users.id == search).first()
        if selected:
            isUpdate=True
            id=selected.id
            form.fullName.data=selected.fullName
            form.institution.data=selected.institution
            form.email.data=selected.email

            form.contact.data=selected.contact
            form.package.data=selected.package

            form.position.data=selected.position
            form.department.data=selected.department

            form.reference_no.data=selected.reference_no
            flash(f"User Found:{selected.id}", 'success')




        else:
            flash(f"User not Found", 'warning')
    
    if datetime.now() > setdate:
        expired=True
    else:
        expired=False
    return render_template('register.html', form=form, isUpdate=isUpdate, user_id=id, expired=expired)


@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/viewz', methods=['POST','GET'])
def viewz():
    search=request.args.get('search')
    status_paid=request.args.get('status_paid')
    if search is None:
        all_users=Users.query.order_by(Users.date).all()

    else:
        if search != "":
            match status_paid:            
                case 'paid':
                    all_users=Users.query.filter(or_(
                        Users.institution.contains(search),
                        Users.fullName.contains(search)
                    ), Users.reference_no.is_not(None)).order_by(Users.date).all()
                case 'unpaid':
                    all_users=Users.query.filter(or_(
                        Users.institution.contains(search),
                        Users.fullName.contains(search)
                    ), Users.reference_no.is_(None)).order_by(Users.date).all()
                case _:
                        all_users=Users.query.filter(or_(
                        Users.institution.contains(search),
                        Users.fullName.contains(search)
                    )).order_by(Users.date).all()
        else:
            match status_paid:            
                case 'paid':
                    all_users=Users.query.filter(Users.reference_no.is_not(None)).order_by(Users.date).all()
                case 'unpaid':
                    all_users=Users.query.filter(Users.reference_no.is_(None)).order_by(Users.date).all()
                case _:
                    all_users=Users.query.order_by(Users.date).all()
    return render_template('viewz.html', all_users=all_users)