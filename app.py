######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

#for image uploading
from werkzeug import secure_filename
import os, base64

#for date
import datetime

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'floraazhang' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user


def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, pid, caption, aname, aid FROM Photo WHERE uid = '{0}'ORDER BY pid DESC".format(uid))
	return cursor.fetchall()


def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT P.data,P.pid,P.caption,P.likes,U.first,U.last,U.email,U.uid FROM Photo P,Users U WHERE U.uid=P.uid ORDER BY pid DESC") 
	return cursor.fetchall()

def getAllTags():
	cursor = conn.cursor()
	cursor.execute("SELECT *  FROM Tag") 
	return cursor.fetchall()

def getUsersAlbums(uid):
	cursor = conn.cursor() 
	cursor.execute("SELECT aid, aname, cover FROM Album WHERE uid = '{0}'".format(uid))
	return cursor.fetchall()

def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT aid, aname, cover FROM Album ORDER BY aid DESC")
	return cursor.fetchall()

def getAllComments():
	cursor = conn.cursor()
	cursor.execute("SELECT authorName, content, cdate, pid FROM Comment")
	comments = cursor.fetchall()
	return comments

def getAllLikes():
	cursor = conn.cursor()
	cursor.execute("SELECT L.pid, U.first, U.last, U.email FROM Likes L, Users U WHERE U.uid=L.uid")
	alllikes = cursor.fetchall()
	return alllikes

def getAllStrangers():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE uid!='{0}' AND uid NOT IN (SELECT F.f_uid FROM Friends F WHERE F.uid = '{0}')".format(uid))
	return cursor.fetchall()

def getAllFriends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT U.first, U.last, U.birth, U.hometown, U.gender FROM Friends F, Users U WHERE F.uid='{0}' AND F.f_uid=U.uid".format(uid))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserNameFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT first  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserInfo():
	email = flask_login.current_user.id
	cursor = conn.cursor()
	cursor.execute("SELECT *  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()

def getAidFromAname(aname):
	cursor = conn.cursor()
	cursor.execute("SELECT aid  FROM Album WHERE aname = '{0}'".format(aname))
	return cursor.fetchone()[0]

def getTopTenUsers():
	cursor = conn.cursor()
	cursor.execute("SELECT *  FROM Users ORDER BY contribution DESC LIMIT 10")
	return cursor.fetchall()

def getTopTenTags():
	cursor = conn.cursor()
	cursor.execute("SELECT word, COUNT(*) FROM Tag GROUP BY word ORDER BY COUNT(*) DESC LIMIT 10")
	return cursor.fetchall()

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def checkCommentValid(pid, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT uid  FROM Photo WHERE pid = '{0}'".format(pid))
	owner_uid = cursor.fetchone()[0]
	return owner_uid != uid


@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 


def createAlbum(aname, uid):
	now = datetime.datetime.now()
	adate = now.strftime("%Y-%m-%d")
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Album (uid, aname, adate) VALUES ('{0}', '{1}', '{2}' )".format(uid, aname, adate))
	conn.commit()

def deleteAlbum(aname):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Album WHERE aname='{0}'".format(aname))
	conn.commit()

def uploadPhoto(uid, imgfile, caption, aname, tags):
	data = base64.standard_b64encode(imgfile.read())
	aid = getAidFromAname(aname)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Photo (aid, data, uid, caption, aname) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(aid, data, uid, caption, aname))
	cursor.execute("UPDATE Album SET cover='{0}' WHERE aname='{1}' AND uid='{2}'".format(data, aname, uid))
	cursor.execute("UPDATE Users SET contribution=contribution+1 WHERE uid='{0}'".format(uid))
	conn.commit()
	handleTags(tags)

def deletePhoto(pid):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photo WHERE pid='{0}'".format(pid))
	conn.commit()

def handleTags(tags):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT MAX(pid) FROM Photo")
	pid = cursor.fetchone()[0]
	for tag in tags.split(', '):
		cursor.execute("INSERT INTO Tag (word, pid, uid) VALUES ('{0}','{1}','{2}')".format(tag, pid, uid))
	conn.commit()

def handleClickedTag(clickedTag):
	cursor.execute("SELECT P.data FROM Photo P, Tag T WHERE P.pid=T.pid AND T.word='{0}'".format(clickedTag))
	return cursor.fetchall()

def handleClickedMyTag(clickedMyTag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT P.data FROM Photo P, Tag T WHERE P.pid=T.pid AND T.word='{0}' AND P.uid='{1}'".format(clickedMyTag,uid))
	return cursor.fetchall()

def handleSearchTags(searchTags):
	photo=()
	for tag in searchTags.split(' '):
		photo = photo + handleClickedTag(tag)
	return photo

def handleClickedAlbum(aid):
	cursor.execute("SELECT data FROM Photo WHERE aid='{0}'".format(aid))
	photos = cursor.fetchall()
	return photos

def handleComments(content, pid):
	now = datetime.datetime.now()
	cdate = now.strftime("%Y-%m-%d")
	cursor = conn.cursor()
	if flask_login.current_user.is_authenticated:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		authorName = getUserNameFromEmail(flask_login.current_user.id)
		if checkCommentValid(pid, uid):
			cursor.execute("INSERT INTO Comment (uid, authorName, content, cdate, pid) VALUES ('{0}', '{1}', '{2}','{3}', '{4}' )".format(uid, authorName, content, cdate, pid))
			cursor.execute("UPDATE Users SET contribution=contribution+1 WHERE uid='{0}'".format(uid))
	else:
		authorName = "Anonymous"
		cursor.execute("INSERT INTO Comment (authorName, content, cdate, pid) VALUES ('{0}', '{1}', '{2}','{3}')".format(authorName, content, cdate, pid))
	conn.commit()

def handleLikes(pid):
	if flask_login.current_user.is_authenticated:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT uid FROM Likes WHERE pid='{0}' AND uid='{1}'".format(pid,uid))
		liked = cursor.fetchone()
		print(liked)
		if liked is None:
			cursor.execute("UPDATE Photo SET likes=likes + 1 WHERE pid='{0}'".format(pid))
			cursor.execute("INSERT INTO Likes (uid, pid) VALUES ('{0}','{1}')".format(uid,pid))
			conn.commit()

def mayLikePhotos():
	cursor = conn.cursor()
	if flask_login.current_user.is_authenticated:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor.execute("SELECT P.data, P.caption,P.likes,P.pid FROM Tag T, Photo P, (SELECT word AS word2 FROM Tag WHERE uid='{0}' GROUP BY word ORDER BY COUNT(*) DESC limit 5)  AS userTags ,(SELECT pid AS pid2, COUNT(*) AS numberofTag FROM Tag GROUP BY pid ORDER BY COUNT(*))  AS numTag WHERE T.word=word2 AND T.pid=P.pid AND T.pid=pid2 AND P.uid<>'{0}' GROUP BY T.pid ORDER BY COUNT(*) DESC, numberofTag".format(uid))
		mayLikePhotos = cursor.fetchall()
		if not mayLikePhotos:
			cursor.execute("SELECT P.data, P.caption,P.likes,P.pid FROM Photo P WHERE P.uid <> '{0}' ORDER BY P.likes DESC limit 10".format(uid))
			mayLikePhotos = cursor.fetchall()
	else:
		cursor.execute("SELECT P.data, P.caption,P.likes,P.pid FROM Photo P ORDER BY P.likes DESC limit 10")
		mayLikePhotos = cursor.fetchall()
	return mayLikePhotos








#default page  
@app.route("/", methods=['GET', 'POST'])
def hello():
	if request.method == 'POST':
		if request.form.get('comment') is not None:
			content = request.form.get('comment')
			pid = request.form.get('clickedPost')
			handleComments(content, pid)
		else:
			pid = request.form.get('likes')
			handleLikes(pid)

	return render_template('hello.html', allphotos=getAllPhotos(), mayLikePhotos=mayLikePhotos(), tags=getAllTags(), allalbums=getAllAlbums(), allcomments=getAllComments(), alllikes=getAllLikes(),topTenUsers=getTopTenUsers(), topTenTags=getTopTenTags())


@app.route('/photo', methods=['GET', 'POST'])
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		# create album
		if request.form.get('albumName') is not None:
			aname = request.form.get('albumName')
			createAlbum(aname, uid)
		# delete photo
		elif request.form.get('delete') is not None:
			pid = request.form.get('delete')
			deletePhoto(pid)
		# delete album
		elif request.form.get('deleteAlbum') is not None:
			aname = request.form.get('deleteAlbum')
			deleteAlbum(aname)
		# upload photo
		else:
			imgfile = request.files['photo']
			caption = request.form.get('caption')
			aname = request.form.get('aname')
			tags = request.form.get('tags')
			uploadPhoto(uid, imgfile, caption, aname, tags)

	return render_template('photo.html',photos=getUsersPhotos(uid), tags=getAllTags(), albums=getUsersAlbums(uid))
	


@app.route("/album", methods=['POST'])
def album():
	if request.method == 'POST':
		cursor = conn.cursor()
		# clicked album
		if request.form.get('clickedAlbum') is not None:
			aid = request.form.get('clickedAlbum')
			cursor.execute("SELECT aname FROM Album WHERE aid='{0}'".format(aid))
			return render_template('album.html', photos=handleClickedAlbum(aid), title=cursor.fetchone()[0]) 
		# clicked my tag
		elif request.form.get('clickedMyTag') is not None:
			clickedMyTag = request.form.get('clickedMyTag')
			return render_template('album.html', photos=handleClickedMyTag(clickedMyTag), title="#"+clickedMyTag) 
		# search tags
		elif request.form.get('searchTags') is not None:
			searchTags = request.form.get('searchTags')
			print(searchTags)
			return render_template('album.html', photos=handleSearchTags(searchTags), title="#"+searchTags)
		# clicked home page tag
		else:
			clickedTag = request.form.get('clickedTag')
			return render_template('album.html', photos=handleClickedTag(clickedTag), title="#"+clickedTag) 

 

@app.route("/friend", methods=['GET', 'POST'])
@flask_login.login_required
def friend():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		f_uid = request.form.get('addFriend')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Friends (uid, f_uid) VALUES ('{0}', '{1}')".format(uid, f_uid))
		conn.commit()
	return render_template('friend.html', strangers=getAllStrangers(), friends=getAllFriends()) 



@app.route('/account')
@flask_login.login_required
def account():
	userInfo = getUserInfo()
	return render_template('account.html', userInfo=userInfo)

















@app.route("/register", methods=['GET'])
def register():
	return render_template('improved_register.html', supress='True') 

@app.route("/register/", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first=request.form.get('first')
		last=request.form.get('last')
		birth=request.form.get('birth')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print cursor.execute("INSERT INTO Users (email, password, first, last, birth, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, first, last, birth, hometown, gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('account.html', name=email)
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return render_template('login.html')

	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('unauth.html', message='Logged out') 

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Photo (data, uid, caption) VALUES ('{0}', '{1}', '{2}' )".format(data, uid, caption))
		conn.commit()
		return render_template('photo.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid) )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code 

if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)











@app.route('/template')
def template():
	return render_template('template.html')
