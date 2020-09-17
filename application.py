import os
import csv, requests
from passlib.hash import sha256_crypt
from flask import Flask, session, render_template, url_for, request, redirect, g, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import login_required, logout_user, login_user, login_manager

app = Flask(__name__)
app.secret_key = 'hello'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = session['user_id']

@app.route("/", methods=["POST", "GET"])
def index():
	userName = request.form.get('userName')
	userPassword = request.form.get('userPassword')
	userData = db.execute("SELECT * FROM value WHERE email=:userMail", {"userMail":userName}).fetchone()
	if request.method == "POST":
		if userData != None:
			session.pop('user_id', None)
			session.clear()
			if userData.email == userName and sha256_crypt.verify(userPassword, userData.password):
				session['user_id'] = userName
				return redirect(url_for('login'))
			else:
				return render_template('index.html', message="PASSWORD DIDN'T MATCH")
		else:
			return render_template('index.html', message="USER DOES NOT EXITS")
	else:
		return render_template('index.html')

@app.route("/signup", methods=['POST', 'GET'])
def signup():
	if request.method == "POST":
		userFirstName = request.form.get('firstN')
		userLastName = request.form.get('lastN')
		userEamil = request.form.get('email')
		userPassword = request.form.get('password')
		userConPassword = request.form.get('confirmPassword')
		if userPassword == userConPassword:
			encrypPass = sha256_crypt.hash(userPassword)
			db.execute("INSERT INTO value (firstname, lastname, email, password) VALUES (:fName, :lName, :email, :ePass)",
			{"fName":userFirstName, "lName":userLastName, "email":userEamil, "ePass":encrypPass})
			db.commit()
			message = "Password Matches"
			return redirect(url_for('login'))
		else:
			message = "Password don't Match"
			return render_template('singup.html', message=message)
	else:
		return render_template("singup.html")

@app.route("/userPass", methods=['POST', 'GET'])
def userPass():
	userName = request.form.get('userName')
	userPassword = request.form.get('userPassword')
	if request.method == "POST":
		return render_template('index.html', userName=userName)
	else:
		return render_template('index.html')

@app.route("/success")
def success():
	return render_template('success.html')

@app.route("/login")
def login():
	if not g.user:
		return redirect(url_for('index'))
	return render_template('success.html')

@app.route("/logout")
def logout():
	if session == None:
		return render_template('index.html')
	session.pop('user_id', None)
	session.clear()
	return render_template('index.html')

@app.route("/book", methods=["POST", "GET"])
def book():
	if request.method == 'POST':
		categore = request.form.get('userSelect')
		userSeach = request.form.get('search')
		if categore == "isbn":
			data = db.execute("SELECT * FROM data WHERE isbn=:eisbn", {"eisbn":userSeach}).fetchall()
			if data:
				return render_template('success.html', data=data)
			else:
				newS1 = "%" + userSeach + "%"
				val1 = userSeach[0]
				totalLen = len(userSeach)
				val2 = userSeach[totalLen-1]
				newS2 = val1 + "%" + val2
				dataPosition = db.execute("SELECT * FROM data WHERE isbn LIKE :eisbn1 OR isbn LIKE :eisbn2",
				 {"eisbn1":newS1, "eisbn2":newS2}).fetchall()
				message = "Did You mean"
				return render_template('success.html', message=message, dataPosition=dataPosition)
		elif categore == "title":
			data = db.execute("SELECT * FROM data WHERE title=:etitle", {"etitle":userSeach}).fetchall()
			if data:
				return render_template('success.html', data=data)
			else:
				newS1 = "%" + userSeach + "%"
				val1 = userSeach[0]
				totalLen = len(userSeach)
				val2 = userSeach[totalLen-1]
				newS2 = val1 + "%" + val2
				dataPosition = db.execute("SELECT * FROM data WHERE title LIKE :title1 OR title LIKE :title2",
				 {"title1":newS1, "title2":newS2}).fetchall()
				message = "Did You mean"
				return render_template('success.html', message=message, dataPosition=dataPosition)
		elif categore == "author":
			data = db.execute("SELECT * FROM data WHERE author=:eauthor", {"eauthor":userSeach}).fetchall()
			if data:
				return render_template('success.html', data=data)
			else:
				newS1 = "%" + userSeach + "%"
				val1 = userSeach[0]
				totalLen = len(userSeach)
				val2 = userSeach[totalLen-1]
				newS2 = val1 + "%" + val2
				dataPosition = db.execute("SELECT * FROM data WHERE author LIKE :eauthor1 OR author LIKE :eauthor2",
				 {"eauthor1":newS1, "eauthor2":newS2}).fetchall()
				message = "Did You mean"
				return render_template('success.html', message=message, dataPosition=dataPosition)
		elif categore == "year":
			data = db.execute("SELECT * FROM data WHERE year=:eyear", {"eyear":userSeach}).fetchall()
			if data:
				return render_template('success.html', data=data)
			else:
				newS1 = "%" + userSeach + "%"
				val1 = userSeach[0]
				totalLen = len(userSeach)
				val2 = userSeach[totalLen-1]
				newS2 = val1 + "%" + val2
				dataPosition = db.execute("SELECT * FROM data WHERE year LIKE :eyear1 OR year LIKE :eyear2",
				 {"eyear1":newS1, "eyear2":newS2}).fetchall()
				message = "Did You mean"
				return render_template('success.html', message=message, dataPosition=dataPosition)
		
	else:
		return redirect(url_for('index'))

@app.route('/booklist/<string:book_isbn>/<string:authorN>')
def booklist(book_isbn, authorN):
	data = db.execute("SELECT * FROM data WHERE isbn=:bookisbn AND author=:auth", {"bookisbn":book_isbn, "auth":authorN}).fetchone()
	if data:
		session['isbn'] = data.isbn
		session['auth'] = data.author
		user = session['user_id']
		reviews = db.execute("SELECT * FROM usercomment WHERE bookisbn=:bookis AND bookauthor=:booka", 
			{"bookis":book_isbn, "useEam":user, "booka":authorN}).fetchall()

		average = db.execute("SELECT AVG(rating)::numeric(10,2) FROM usercomment WHERE bookisbn=:bookis AND bookauthor=:booka", 
			{"bookis":book_isbn, "booka":authorN}).fetchall()

		count = db.execute("SELECT COUNT(useremail) FROM usercomment WHERE useremail=:usedata AND bookisbn=:bookis AND bookauthor=:booka", 
			{"usedata":user, "bookis":book_isbn, "booka":authorN}).fetchall()
		if reviews and average:
			return render_template('books.html', data=data, reviews=reviews, average=average[0], count=count[0])
		else:
			message = "No ratings Yet"
			return render_template('books.html', data=data, message=message, count=count[0])
	else:
		message = "Book Doesn't exits"
		return render_template('books.html', message=message)

@app.route("/comment")
def comment():
	if session:
		value = session['isbn']
		auth = session['auth']
		
		data = db.execute("SELECT * FROM data WHERE isbn=:bookisbn AND author=:auth", {"bookisbn":value, "auth":auth}).fetchone()
		if data:
			return render_template('signin.html',  message="FROM POST", data=data)
		else:
			return render_template('signin.html', message="NO data")
@app.route("/review")
def review():
	statValue = request.args.get('rate')
	messText = request.args.get('usercomment')
	user = session['user_id']
	isbn = session['isbn']
	auth = session['auth']

	db.execute("INSERT INTO usercomment (useremail, bookisbn, bookauthor, comments, rating) VALUES (:uemail, :uboisbn, :uauthor, :ucomment, :urating)",
		{"uemail":user, "uboisbn":isbn, "uauthor":auth, "ucomment":messText, "urating":statValue})
	db.commit()
	return render_template('thankyou.html')

@app.route("/api/<string:isbnapi>")
def api(isbnapi):
	reveiwAndCount = db.execute("SELECT COUNT(rating), AVG(rating) FROM usercomment WHERE bookisbn=:userRequest",
				 {"userRequest":isbnapi})
	bookInfo = db.execute("SELECT * FROM data WHERE isbn=:userrequesisbn", {"userrequesisbn":isbnapi}).fetchone()
	if bookInfo is None:
		return jsonify({"error": "Invalid isbn"}), 422

	return jsonify({
		"Author " : bookInfo.author,
		"Titlle " : bookInfo.title,
		"Published Year " : bookInfo.year,
		"ISBN " : bookInfo.isbn
		})

"""@app.route("/books")
def books():
	f = open('books.csv')
	csv_f = csv.reader(f)
	header = next(csv_f)
	for row in csv_f:
		db.execute("INSERT INTO data (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
								{"isbn":row[0], "title":row[1], "author":row[2], "year":row[3]})
	db.commit()
	return render_template("success.html", message="Done")"""






































