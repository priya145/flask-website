from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

with open('C:/flask3/templates/config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key ='super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)

mail=Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


db=SQLAlchemy(app)

class Feedback(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Booking(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    paid =  db.Column(db.Integer, nullable=False)
    remain=db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(12), nullable=True)
    occassion = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    




@app.route("/")
def home():
	return render_template('index.html' , params=params)




@app.route("/dashboard", methods = ['GET', 'POST'] )
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts=Booking.query.all()
        return render_template('dashboard.html' , params=params , posts=posts)

    if request.method=='POST':
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if(username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            posts=Booking.query.all()
            return render_template('dashboard.html', params=params ,posts=posts)

    return render_template('login.html', params=params)



@app.route("/Feedback", methods = ['GET', 'POST'])
def feedback():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        entry = Feedback(name=name, email = email, message = message, date= datetime.now() )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New feedback from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message
                          )
    return render_template('contact.html' , params=params)

@app.route("/book", methods = ['GET', 'POST'])
def booking():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        paid = request.form.get('paid')
        remain = request.form.get('remain')
        date = request.form.get('date')
        occassion = request.form.get('occassion')
        message = request.form.get('message')
        entry = Booking(name=name, email = email, phone=phone, paid=paid, remain=remain, date=date, occassion=occassion,message = message )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New booking from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = occassion + "\n" + message + "\n" + phone + "\n" + date
                          )
    return render_template('book.html' , params=params)




@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method=='POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            paid = request.form.get('paid')
            remain = request.form.get('remain')
            date = request.form.get('date')
            occassion = request.form.get('occassion')
            message = request.form.get('message')

            if sno=='0':
                post=Booking(name=name, email = email, phone=phone, paid=paid, remain=remain, date=date, occassion=occassion,message = message )
                db.session.add(post)
                db.session.commit()

            else:
                post=Booking.query.filter_by(sno=sno).first()
                post.name=name
                post.email=email
                post.phone=phone
                post.paid=paid
                post.remain=remain
                post.date=date
                post.occassion=occassion
                post.message=message
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Booking.query.filter_by(sno=sno).first()
        return render_template('edit.html' , params=params , post=post )




@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post=Booking.query.filter_by(sno =sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')




app.run(debug=True)