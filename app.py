from flask import Flask,render_template,request,url_for,redirect,session,logging,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash
import pickle
import numpy as np
import random
import smtplib
from flask_mail import Mail, Message
import secrets
from flask import Blueprint


popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))
famous_books = pickle.load(open('famous_books.pkl','rb'))



app = Flask(__name__)
bootstrap = Bootstrap(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Vaibhav Gupta/Desktop/book-recommender-system-master (1)/book-recommender-system-master/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


app.secret_key ="vibho"



class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    message = db.Column(db.Text)



class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




wishlist_items = []

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    book_title = ''
    if request.method == 'POST':
        book_title = request.form['book_title']
        book_author = request.form['book_author']
        wishlist_items.append((book_title, book_author))
        flash(f'{book_title} has been added to your wishlist!', 'success')
    return render_template('wishlist.html', items=wishlist_items)

@app.route('/remove_wishlist', methods=['POST'])
def remove_wishlist():
    book_title = request.form['book_title']
    book_author = request.form['book_author']
    if (book_title, book_author) in wishlist_items:
        wishlist_items.remove((book_title, book_author))
        flash(f'{book_title} has been removed from your wishlist!', 'danger')
    else:
        flash(f'{book_title} was not found in your wishlist', 'warning')
    return redirect(url_for('wishlist'))








@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        flash("Welcome to our recommendation system")
        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return render_template("recommend.html")
    return render_template("login.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        flash("You are successfully registered!")
        register = user(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")





@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))





@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/contact', methods=['POST'])
def contact_submit():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    contact = Contact(name=name, email=email, message=message)
    db.session.add(contact)
    db.session.commit()
    # do something with the form data, such as send an email or store in a database
    flash('Thank You! For Contacting Us')
    return render_template('contact.html')



@app.route('/top')
def top():
    return render_template('top.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                            )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0]

    if len(index) == 0:
        flash("Book not found in the list.")
        return render_template('recommend.html') # Redirect to the desired page

    index = index[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)


@app.route('/list')
def listt():
    # name = []
    # for i in book_list:
    #     temp_df1 = book_list[book_list['Book-Title'] == book_list.index[i[0]]]
    #     name.extend(list(temp_df1.drop_duplicates('Book-Title')['Book-Title'].values))

    # return render_template('list.html')
    return render_template('list.html', name=list(famous_books[1:700]))
    # return render_template('recommend.html', name = name)

#to run app and debug=true to see changes in page itself


if __name__ == '__main__':
    app.run(debug=True)