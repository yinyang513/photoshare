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
import flask_login
from datetime import date
import config

#for image uploading
import os, base64


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!


#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = config.password
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

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()

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

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
    return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a>
               '''
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

def getFriendsUID(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id2 FROM Friends WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall() 

# def getFriendsPhotos(uid):
# 	friends_ids = getFriendsUID(uid)
# 	cursor = conn.cursor()
# 	for friend in friends_ids: 
# 		cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(friend))
# 		return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

# @app.route('/')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('home.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        #this means there are greater than zero entries with that email
        return False
    else:
        return True

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    # email = request.form.get('email')
    return render_template('register.html', supress = True)

@app.route("/registerf", methods=['GET', 'POST'])
def registerf():
    return render_template('register.html')

@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        birthday = request.form.get('birthday')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        password=request.form.get('password')
        
    except:
        print("couldn't find all tokens1") #this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test =  isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, firstname, lastname, birthday, hometown, gender, password) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')"
            .format(email, firstname, lastname, birthday, hometown, gender, password)))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('home.html', name=firstname, message='Account Created!')
    else:
        print("Email in use")
        return flask.redirect(flask.url_for('registerf'))

def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption, albumID, user_id FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('profile.html', name=flask_login.current_user.id, likes = displayLikes(), tags = displayTags(), photos=getUsersPhotos(uid), comments = displayComments(), base64=base64)


# @app.route('/profile', methods = ['POST'])
# def my_photos():
# 	uid = getUserIdFromEmail(flask_login.current_user.id)
# 	return render_template('home.html', name=flask_login.current_user.id, message="Here's your profile", photos=getUsersPhotos(uid), base64=base64)

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# def getPhotoIDFromData(photo_data):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT picture_id FROM Pictures WHERE imgdata = '{0}'".format(photo_data))
# 	return cursor.fetchone()[0]

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        album_name = request.form.get('albumname')
        if albumExists(album_name, uid) != 0:
            albumID = getAlbumId(album_name, uid)
            photo_data =imgfile.read()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, albumID) VALUES (%s, %s, %s, %s )''' ,(photo_data, uid, caption, albumID))
            conn.commit()
            return render_template('home.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
        else:
            return render_template('home.html', message='Album does not exist! Please create!')
        
    #The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')
#end photo uploading code

def displayTags():
    cursor = conn.cursor()
    cursor.execute("SELECT T.name FROM Tags T, Tagged TG WHERE T.tag_id = TG.tag_id")
    tags = cursor.fetchall()
    return tags

@app.route('/add-tag', methods=['GET', 'POST'])
@flask_login.login_required
def addTag():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        tag = request.form.get('tag')
        photo_id = request.form.get('photo_id')

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Tags WHERE name = '{0}'".format(tag))
        tagExists = cursor.fetchone()
        if not tagExists:
            cursor.execute("INSERT INTO Tags (name) VALUES (%s)", (tag))

        cursor.execute("SELECT tag_id FROM Tags WHERE name = '{0}'".format(tag))
        tag_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT photo_id,tag_id FROM Tagged WHERE photo_id = '{0}' AND tag_id = '{1}'".format(photo_id,tag_id))
        taggedExist = cursor.fetchall()
        if not taggedExist:
            cursor.execute('''INSERT INTO Tagged (photo_id, tag_id) VALUES (%s, %s)''', (photo_id, tag_id))
        conn.commit()

        # print(displayTags())

        return render_template ('displayUpload.html', name=flask_login.current_user.id, message='Add Tags!', 
        tags = (tag,photo_id), photos=getUsersPhotos(uid), base64=base64)
    else: 
        return render_template ('displayUpload.html', name=flask_login.current_user.id, 
        message='Add Tags!', photos=getUsersPhotos(uid), base64=base64)

@app.route('/profile/tags')
@flask_login.login_required
def displayUserTags():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT T.tag_id, P.picture_id, P.imgdata FROM Pictures P, Tags T, Tagged TG WHERE P.picture_id = TG.photo_id AND TG.tag_id = T.tag_id AND user_id = '{0}' ORDER BY T.tag_id ASC".format(uid))
    userPhotosByTag = cursor.fetchall()
    cursor.execute("SELECT T.tag_id, T.name FROM Pictures P, Tags T, Tagged TG WHERE P.picture_id = TG.photo_id AND TG.tag_id = T.tag_id AND user_id = '{0}' ORDER BY T.tag_id ASC".format(uid))
    userTags = cursor.fetchall()
    # print(userTags)
    return render_template('userTags.html', name=flask_login.current_user.id, photos = userPhotosByTag, tags = userTags, base64 = base64)

@app.route('/tags')
def displayTags():
    cursor = conn.cursor()
    cursor.execute("SELECT T.tag_id, P.picture_id, P.imgdata FROM Pictures P, Tags T, Tagged TG WHERE P.picture_id = TG.photo_id AND TG.tag_id = T.tag_id ORDER BY T.tag_id ASC")
    userPhotosByTag = cursor.fetchall()
    cursor.execute("SELECT tag_id, name FROM Tags")
    userTags = cursor.fetchall()
    return render_template('allTags.html', name = 'Tags', photos = userPhotosByTag, tags = userTags, base64 = base64)

@app.route('/popular-tags')
def popularTags():
    cursor = conn.cursor()
    cursor.execute("SELECT T.tag_id, P.picture_id, P.imgdata FROM Pictures P, Tags T, Tagged TG WHERE P.picture_id = TG.photo_id AND TG.tag_id = T.tag_id ORDER BY T.tag_id ASC")
    userPhotosByTag = cursor.fetchall()
    cursor.execute("SELECT TG.tag_id, T.name, COUNT(TG.tag_id), T.name FROM Tagged TG, Tags T WHERE TG.tag_id = T.tag_id GROUP BY tag_id ORDER BY COUNT(tag_id) DESC")
    mostPopular = cursor.fetchall()
    return render_template('allTags.html', name='Popular', photos = userPhotosByTag, tags = mostPopular, base64 = base64)

@app.route('/you-may-also-like-tags')
@flask_login.login_required
def tagRecommendations():
    topFive = [0]*5
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    #gets the top 5 tags used
    cursor.execute('''SELECT COUNT(TG.tag_id),T.tag_id FROM Tagged TG, Tags T, Pictures P 
                    WHERE TG.tag_id = T.tag_id AND TG.photo_id = P.picture_id AND P.user_id = '{0}' 
                    GROUP BY tag_id ORDER BY COUNT(tag_id) DESC LIMIT 5'''.format(uid))
    tags = cursor.fetchall()
    # topFive = [tag[1] for tag in tags]
    for i in range(len(tags)): topFive[i] = tags[i][1]
    # print(topFive)
    #get the number of tags each photo has
    cursor.execute("SELECT photo_id, COUNT(photo_id) FROM Tagged GROUP BY photo_id")
    numOfTags = cursor.fetchall()
    #get the photos that are in the top 5 tags as well as how many tags they have for the top 5 tags
    cursor.execute('''SELECT P.picture_id, COUNT(P.picture_id), P.imgdata FROM Tagged TG, Pictures P 
                        WHERE P.picture_id = TG.photo_id AND (TG.tag_id = '{0}' OR TG.tag_id = '{1}' OR TG.tag_id = '{2}' OR TG.tag_id = '{3}' OR TG.tag_id = '{4}') 
                        GROUP BY P.picture_id ORDER BY COUNT(P.picture_id) DESC'''.format(topFive[0], topFive[1], topFive[2], topFive[3], topFive[4]))
    topFivePics0 = cursor.fetchall()

    #merge the two
    topFivePics = []
    for noTag in numOfTags:
        # print("no", noTag[0])
        for pic1 in topFivePics0:
            # print("pic", pic1[0])
            pic = ()
            if noTag[0] == pic1[0]:
                # print()
                
                pic = (pic1[0],pic1[1],pic1[2],noTag[1]) #change to add pic1[2]
                break
        # print(pic)
        if pic != ():
            topFivePics.append(pic)
    # print(topFivePics)
    topFivePics1 = sorted(topFivePics,key=lambda x:x[3])
    # print(topFivePics1)
    topFivePics2 = sorted(topFivePics1,key=lambda x:x[1], reverse = True)
    # print(topFivePics2)
    return render_template('allTags.html', name='You may also like:', photos = topFivePics2, base64 = base64)

@app.route('/tag-photos', methods = ['GET','POST'])
def tagPhotos():
    tag_id = request.args.get('tag_id')
    cursor = conn.cursor()
    cursor.execute("SELECT P.picture_id, P.imgdata, P.caption FROM Tags T, Tagged TG, Pictures P WHERE T.tag_id = TG.tag_id AND TG.photo_id = P.picture_id AND T.tag_id = '{0}'".format(tag_id))
    allPhotos = cursor.fetchall()
    return render_template('displayTags.html',photos = allPhotos, base64=base64)

@app.route('/tag-user-photos', methods = ['GET','POST'])
@flask_login.login_required
def tagUserPhotos():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    tag_id = request.args.get('tag_id')
    cursor = conn.cursor()
    cursor.execute("SELECT P.picture_id, P.imgdata, P.caption FROM Tags T, Tagged TG, Pictures P WHERE T.tag_id = TG.tag_id AND TG.photo_id = P.picture_id AND T.tag_id = '{0}' AND P.user_id = '{1}'".format(tag_id,uid))
    allPhotos = cursor.fetchall()
    return render_template('displayTags.html',photos = allPhotos, base64=base64)
#default page
# @app.route("/")
# def home():
# 	if hasattr(str(flask_login.current_user), "email"):
# 		uid = getUserIdFromEmail(flask_login.current_user.id)
# 		return render_template('home.html', message='Welcome to Photoshare', photos = getUsersPhotos(uid), base64 = base64)
# 	else:
# 		return render_template('home.html', message='Welcome to Photoshare')

def getComments(uid,photo_id):
    comment = request.form.get('comment')
    cursor = conn.cursor()
    if not photo_id or not comment:
        return
    else: 
        today = date.today().strftime("%y/%m/%d")
        cursor.execute('''INSERT INTO Comments (user_id, photo_id, text, date) VALUES (%s, %s, %s, %s)''', (uid, photo_id, comment, today))
        conn.commit()

def displayComments():
    cursor = conn.cursor()
    cursor.execute("SELECT text, photo_id FROM Comments")
    return cursor.fetchall()

def getLikes(uid,photo_id):
    like = request.form.get('like')
    cursor = conn.cursor()
    if not like:
        return
    else:
        cursor.execute('''INSERT INTO Likes (photo_id, user_id) VALUES (%s, %s)''', (photo_id, uid))
        conn.commit()

def displayLikes():
    cursor = conn.cursor()
    cursor.execute("SELECT photo_id, COUNT(photo_id) FROM Likes GROUP BY photo_id") # this is the number of likes
    numOfLikes = cursor.fetchall()
    cursor.execute("SELECT L.photo_id, U.firstname, U.lastname FROM Likes L, Users U WHERE U.user_id = L.user_id ORDER BY photo_id DESC") # (photo_id,user_id)
    likedBy = cursor.fetchall()
    return numOfLikes, likedBy

def getAllPhotos():
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures")
    return cursor.fetchall() 

@app.route('/', methods = ['GET', 'POST'])
def home():
    uid = -1
    if flask_login.current_user.is_authenticated:
        uid = getUserIdFromEmail(flask_login.current_user.id)

    if request.method == 'POST':
        photo_id = request.form.get('photo_id')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
        oid = cursor.fetchone()[0]
        # cannot comment or like own photos
        if uid != oid: 
            getLikes(uid,photo_id)
            getComments(uid,photo_id)
            return render_template('home.html', message='Welcome to Photoshare', likes = displayLikes(), 
            comments = displayComments(), tags = displayTags(), photos = getAllPhotos(), base64 = base64)
        else:
            return render_template('home.html', message='You cannot like or comment on your own posts. Please try again', 
            likes = displayLikes(), comments = displayComments(), tags = displayTags(), photos = getAllPhotos(), base64 = base64)
    else:
        return render_template('home.html', message='Welcome to Photoshare', likes = displayLikes(), 
        comments = displayComments(), tags = displayTags(), photos = getAllPhotos(), base64 = base64)


@app.route('/search-photo', methods = ['GET','POST'])
def searchTag():
    if request.method == 'POST':
        tag = request.form.get('findTag')
        cursor = conn.cursor()
        cursor.execute("SELECT P.imgdata FROM Pictures P, Tags T, Tagged TG WHERE T.name = '{0}' AND T.tag_id = TG.tag_id AND TG.photo_id = P.picture_id".format(tag))
        photos = cursor.fetchall()
        return render_template('searchPhoto.html', photos = photos, base64 = base64)
    else:
        return render_template('searchPhoto.html')

@app.route('/search-comment', methods = ['GET','POST'])
def searchComment():
    if request.method == 'POST':
        word = request.form.get('findWord')
        cursor = conn.cursor()
        cursor.execute('''SELECT U.firstname, U.lastname, COUNT(U.user_id) FROM Comments C, Users U WHERE C.text = '{0}' 
                        AND C.user_id = U.user_id GROUP BY U.user_id ORDER BY COUNT(U.user_id) DESC'''.format(word))
        users = cursor.fetchall()
        return render_template('searchComments.html', users = users)
    else:
        return render_template('searchComments.html')

def getEmailfromUserId(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]


@app.route('/findfriends', methods=['GET', 'POST'])
@flask_login.login_required
def findfriends():
    if request.method == "POST":
        uid = getUserIdFromEmail(flask_login.current_user.id)
        f_email = request.form.get('f_email')
        f_email_unique = isEmailUnique(f_email)
        if f_email_unique == False:
            email = f_email
            cursor.execute("SELECT email, firstname, lastname, user_id from Users WHERE email LIKE %s", (email))
            conn.commit()
            data = cursor.fetchall()
            return render_template('findfriends.html', data=data)
        else:
            return render_template('home.html', message="User not found!")
    return render_template('findfriends.html')

@app.route('/addfriend', methods=['GET', 'POST'])
@flask_login.login_required
def addfriend():
    if request.method == "GET":
        uid = getUserIdFromEmail(flask_login.current_user.id)
        friend_id = int(request.args.get('friend_id'))
        cursor = conn.cursor()
        cursor.execute("SELECT friend_id FROM Friends WHERE user_id = '{0}'".format(uid))
        friends = [item[0] for item in cursor.fetchall()]
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Friends WHERE friend_id = '{0}'".format(uid))
        data = cursor.fetchall()
        d2 = [item[0] for item in data]
        if friend_id in friends:
            return render_template('home.html', message="Friend already added!")
        elif friend_id in d2:
            return render_template('home.html', message="Friend already added!")
        elif friend_id == uid:
            return render_template('home.html', message="You can't friend yourself!")
        else:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Friends(user_id, friend_id) VALUES ('{0}', '{1}')".format(uid, friend_id))
            conn.commit()
            return render_template('home.html', message="Added friend!")
    else:
        return flask.redirect(flask.url_for('findfriends'))

@app.route('/listfriends', methods=['GET', 'POST'])
@flask_login.login_required
def listfriends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT friend_id FROM Friends WHERE user_id = '{0}'".format(uid))
    friends = [item[0] for item in cursor.fetchall()]
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Friends WHERE friend_id = '{0}'".format(uid))
    friends2 = [item[0] for item in cursor.fetchall()]
    all_friends = friends + friends2
    data = []
    for fr in all_friends:
        data.append((fr, getEmailfromUserId(fr)))
    return render_template('listfriends.html', data=data)

    #for friend id in friends, find email, fn/ln. etc.

@app.route('/recFriends', methods=['GET', 'POST'])
@flask_login.login_required
def recFriends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT friend_id FROM Friends WHERE user_id = '{0}'".format(uid))
    friends = [item[0] for item in cursor.fetchall()]
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Friends WHERE friend_id = '{0}'".format(uid))
    friends2 = [item[0] for item in cursor.fetchall()]
    user_friends = friends + friends2
    f_friends = []
    for friend in user_friends:
        cursor = conn.cursor()
        cursor.execute("SELECT friend_id FROM Friends WHERE user_id = '{0}'".format(friend))
        friends1 = [item[0] for item in cursor.fetchall()]
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Friends WHERE friend_id = '{0}'".format(friend))
        friends2 = [item[0] for item in cursor.fetchall()]
        f_friends = friends1 + friends2 + f_friends
    f_1 = sorted(f_friends, key = f_friends.count, reverse = True)
    ff = []
    for f in f_1:
        if f not in ff:
            ff.append(f)
    if uid not in ff:
        return render_template('home.html', message = "No friends added. Please add a friend first!")
    else:
        ff.remove(uid)
        for f in user_friends:
            if f in ff:
                ff.remove(f)
        data = []
        for rf in ff:
            data.append((rf, getEmailfromUserId(rf)))
        return render_template('recFriends.html', data=data)

#user contribution
def userCon():
    
    cursor = conn.cursor()
    cursor.execute("SELECT count(user_id) FROM Users")
    num_users = cursor.fetchall()
    
    
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, COUNT(user_id) FROM Comments GROUP BY user_id")
    comment_con = cursor.fetchall()
    cursor.execute("SELECT user_id, count(picture_id) FROM Pictures AS P GROUP BY P.user_id")
    photo_con = cursor.fetchall()

    #userCon = [0]*(num_users[0][0]-1)
    # for i in range(1, num_users[0][0]):
    #     comment = 0
    #     photo = 0
    #     if photo_con[i][0] == i:
    #         photo = photo_con[i][1]
    #     elif comment_con[i][0] == i:
    #         comment = comment_con[i][1]
    #     userCon[i] = (i,photo+comment)     
        # userCon.append([i, 0])
    userCon = []

    for i in range(1, num_users[0][0]):
        userCon.append([i,0])

    # print(userCon)
    for i in range(len(photo_con)):
        user = photo_con[0][0]
        # print('user', user, photo_con[i][1])
    for i in range(len(photo_con)):
        user = photo_con[i][0]
        # print(user)
        userCon[user-1][1] += photo_con[i][1]
    # print("cc", comment_con)   
    for i in range(len(comment_con)):
        user = comment_con[i][0]
        # print(i)
        # print(comment_con[i][1])
        if user != -1:
            userCon[user-1][1] += comment_con[i][1]
        
    # print('User contribution:', userCon)
    return userCon

def key(count):
    return count[1]

#top10users
def topUsers():
    user_Con = userCon()
    # print('top users user con is', user_Con)
    sortedUserCon = sorted(user_Con, key = key, reverse = True)
    top10 = []
    if len(sortedUserCon)<=10:
        for u in sortedUserCon:
            top10.append(u[0])
    else:
        top10sorted = sortedUserCon[:10]
        for u in top10sorted:
            top10.append(u[0])
    return top10

@app.route('/topUser', methods = ['GET', 'POST'])
def topUser():
    top10Users = topUsers()
    # print(top10Users)
    result = []
    if top10Users != None:
        for u in top10Users:
            # print('U is', u)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM Users WHERE user_id='{0}'".format(u))
            # print('idl')
            result.append(cursor.fetchall())
        # print(result)
        return render_template('topUser.html', topUsers = result)
    else: 
        return render_template('home.html', message = 'No users found!')

#new
def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT albumID, album_name, user_id FROM Albums WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]
#end login code

#new
def albumExists(album_name, user_id):
    #use this to check if an album with albumID has already been created
    cursor = conn.cursor()
    cursor.execute("SELECT albumID FROM Albums WHERE album_name = '{0}' AND user_id = '{1}'".format(album_name, user_id))    
    res = cursor.fetchall()
    return(len(res))

#new 
def getAlbumId(album_name, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT albumID FROM Albums WHERE album_name = '{0}' AND user_id = '{1}'".format(album_name, user_id))  
    albumID = cursor.fetchall()
    return albumID

#new
@app.route('/createAlbum', methods = ['GET', 'POST'])
@flask_login.login_required
def createAlbum():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        album_name = request.form.get('album_name')
        today = date.today().strftime("%y/%m/%d")
        cursor = conn.cursor()
        cursor.execute("SELECT album_name from Albums WHERE user_id = '{0}'".format(uid))
        albums = cursor.fetchall()
        albums = [a[0] for a in albums]
        # print('Album name is', album_name)
        if album_name in albums:
            return render_template('home.html', name=flask_login.current_user.id, message='Album with this name has already been created!', base64=base64)
        # print(album_name in albums)
        # print(albums)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO Albums(user_id, album_name, creation_date) VALUES ('{0}', '{1}', '{2}')".format(uid, album_name, today))
        conn.commit()
        return render_template('home.html', name=flask_login.current_user.id, message='Album created!', base64=base64)
    else: 
        return render_template('createAlbum.html')

#new
def getEmailfromUserId(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]

#new
@app.route('/viewAlbums', methods=['GET', 'POST'])
@flask_login.login_required
def viewAlbums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT albumID, album_name FROM Albums WHERE user_id = '{0}'".format(uid))
    albums = cursor.fetchall()
    return render_template('viewAlbums.html', data=albums)

#new
#Looks at all albums on Photoshare. Login not required
@app.route('/viewAllAlbums', methods=['GET', 'POST'])
def viewAllAlbums():
    cursor = conn.cursor()
    cursor.execute("SELECT albumID, album_name FROM Albums")
    albums = cursor.fetchall()
    return render_template('viewAllAlbums.html', data=albums)

#new
#Looks at all the photos in a album Photoshare. Login not requried
@app.route('/albumPhotos', methods=['GET', 'POST'])
def albumPhotos():
    albumID = request.args.get('albumID')
    cursor = conn.cursor()
    cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE albumID = '{0}'".format(albumID))
    allPhotos = cursor.fetchall()
    return render_template('albumPhotos.html', photos = allPhotos, base64=base64)

#new
#Looks at all the photos on Photoshare. Login not required
@app.route('/allPhotos', methods=['GET', 'POST'])
def allPhotos():
    cursor = conn.cursor()
    cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures")
    allPhotos = cursor.fetchall()
    return render_template('allPhotos.html', photos = allPhotos, base64=base64)

#new
#Looks at all the photos uploaded by the logged in user
@app.route('/yourPhotos', methods=['GET', 'POST'])
@flask_login.login_required
def yourPhotos():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('yourPhotos.html', photos=getUsersPhotos(uid),base64=base64)

#new
#delete photo
@app.route('/deletePhoto', methods=['GET', 'POST'])
@flask_login.login_required
def deletePhoto():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    pid = request.args.get('photo_id')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(pid))
    oid = cursor.fetchone()[0]
    # print(oid)
    if oid == uid:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(pid))
        conn.commit()
        # print(oid, uid)
        return render_template('home.html', name=flask_login.current_user.id, message='Photo deleted!', photos=getUsersPhotos(uid),base64=base64)
    else:
        return render_template('home.html', message='Unable to delete. Not your photo!')

    
@app.route('/deleteAlbum', methods=['GET'])
@flask_login.login_required
def deleteAlbum():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    aid = request.args.get('albumID')
    # print(aid)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Albums WHERE albumID = '{0}'".format(aid))
    conn.commit()
    return render_template('viewAlbums.html', name=flask_login.current_user.id)
        

if __name__ == "__main__":
    #this is invoked when in the shell  you run
    #$ python app.py
    app.run(port=5000, debug=True)
