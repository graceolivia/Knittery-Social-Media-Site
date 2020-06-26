#FLASK_DEBUG=1
import os
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from key import key

UPLOAD_FOLDER = "static/profilepics/uploads"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = key()


db = SQL("sqlite:///yarn.db")

# non-route functions

def getId(user):
    currentuser = session["user"]
    profile = db.execute("SELECT * FROM users WHERE name = :name",
    name=currentuser)
    currentuser_id=profile[0]["id"]
    return currentuser_id

def is_allowed(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# routes

@app.route("/welcome")
def welcome():
    return render_template("coverpage.html")

@app.route("/")
def index():
    if session.get('user') is None:
        return redirect("/welcome")
    else:
        return render_template("index.html")


@app.route("/projects", methods=["GET", "POST"])
def projects():
    user_id = getId(session["user"])
    if request.method == "GET":
        rows = db.execute("SELECT name, yarn, yardage, notes, user_id FROM projects WHERE user_id = :id", id = user_id)
        return render_template("projects.html", rows=rows)
    if request.method == "POST":
        name = request.form.get("name")
        yarn = request.form.get("yarn")
        yardage = request.form.get("yardage")
        notes = request.form.get("notes")
        db.execute("INSERT INTO projects(name, yarn, yardage, notes, user_id) VALUES (:name, :yarn, :yardage, :notes, :user_id)", name=name, yarn=yarn, yardage=yardage, notes=notes, user_id=user_id)
        rows = db.execute("SELECT name, yarn, yardage, notes, user_id FROM projects WHERE user_id = :id", id = user_id)
        return render_template("projects.html", rows=rows)

@app.route("/yarn", methods=["GET", "POST"])
def yarn():
    user_id = getId(session["user"])
    if request.method == "GET":
        rows = db.execute("SELECT name, yardage, fiber, weight FROM yarn WHERE user_id = :id GROUP BY name", id = user_id)
        return render_template("yarn.html", rows=rows)
    if request.method == "POST":
        name = request.form.get("name")
        yardage = request.form.get("yardage")
        fiber = request.form.get("fiber")
        weight = request.form.get("weight")
        db.execute("INSERT INTO yarn(name, yardage, fiber, weight, user_id) VALUES (:name, :yardage, :fiber, :weight, :user_id)", name=name, yardage=yardage, fiber=fiber, weight=weight, user_id=user_id)
        rows = db.execute("SELECT name, yardage, fiber, weight FROM yarn WHERE user_id = :id GROUP BY name", id = user_id)
        return render_template("yarn.html")

@app.route("/patterns", methods=["GET", "POST"])
def patterns():
    user_id = getId(session["user"])
    if request.method == "GET":
        rows = db.execute("SELECT name, author, weight, sizes_available, needle_size, published FROM patterns")
        return render_template("patterns.html", rows=rows)
    if request.method == "POST":
        name = request.form.get("name")
        author = request.form.get("author")
        weight = request.form.get("weight")
        sizes_available = request.form.get("sizes_available")
        needle_size = request.form.get("needle_size")
        published = request.form.get("published")
        db.execute("INSERT INTO patterns (name, author, weight, sizes_available, needle_size, published) VALUES (:name, :author, :weight, :sizes_available, :needle_size, :published)", name=name, author=author, weight=weight, sizes_available=sizes_available, needle_size=needle_size, published=published)
        rows = db.execute("SELECT name, author, weight, sizes_available, needle_size, published FROM patterns")
        return render_template("patterns.html", rows=rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM users WHERE name = :name",
                name=request.form.get("name"))
        if len(rows) != 1:
            flash("Username Not Found")
            print("Username not found!")
            return redirect("/login")
        else:
            passw0rd = db.execute("SELECT password FROM users WHERE name = :name",
            name=request.form.get("name"))
            passcode = passw0rd[0]['password']
        if passcode != password:
            flash("Incorrect password")
            return redirect("/login")
        else:
            session["user"] = rows[0]["name"]
            print(session)
            flash("Logged in!")
            return redirect("/")

    return render_template("public/sign_in.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        passwordconfirm = request.form.get("passwordconfirm")
        rows = db.execute("SELECT * FROM users WHERE name = :name",
                name=request.form.get("name"))
        if len(rows) == 1:
            flash("Username In Use Already")
            return redirect("/register")
        if password != passwordconfirm:
            flash("Make sure passwords match")
            return redirect("/register")
        else:
            db.execute("INSERT INTO users(name, password) VALUES (:name, :password)", name=name, password=password)
            row = db.execute("SELECT name FROM users WHERE name = :name", name=name)
            session["user"] = row[0]["name"]
            print(session)
            flash("Registered! Welcome to Knittery. Go to your profile to add more information about you.")
            return redirect("/")

    return render_template("public/sign_in.html")

@app.route("/profile/<user>")
def profileget(user):
    currentuser = user
    profile = db.execute("SELECT * FROM users WHERE name = :name",
    name=currentuser)
    currentuser_id=getId(session["user"])
    friends_id = db.execute("SELECT friendee FROM friends WHERE friender = :currentuser_id",
    currentuser_id=currentuser_id)
    print(friends_id)
    friends=[]
    fn = 0
    for entry in friends_id:
        friendo = db.execute("SELECT name FROM users WHERE users.id = :friends_id",
        friends_id=friends_id[fn]["friendee"])
        frien = friendo[0]["name"]
        friends.append(frien)
        fn += 1
    print(friends)

    #if not viewing own profile, see if current profile owner is one of your friends
    isfriend = False
    if currentuser != session["user"]:
        loggedinUser = db.execute("SELECT * FROM users WHERE name = :name",
        name=session["user"])
        loggedinUser_id = loggedinUser[0]["id"]
        print("Accessing the profile that is not your own Profile.")
        friendquery = db.execute("SELECT * FROM friends WHERE friender = :loggedinUser_id AND friendee = :currentuser_id",
        loggedinUser_id = loggedinUser_id, currentuser_id=currentuser_id)
        if len(friendquery) == 0:
            print("not friends")
        else:
            isfriend = True
            print(friendquery)
    return render_template("profile.html", profile=profile, friends=friends, isfriend=isfriend)

@app.route("/profile", methods=["GET", "POST"])
def userprofile():
    if request.method == "GET":
        username=session["user"]
        return redirect(url_for('profileget', user=username))
    if request.method == "POST":
        return redirect("/profile/edit")

@app.route("/profile/edit", methods=["GET", "POST"])
def profileedit():
    currentuser = session["user"]
    if request.method == "GET":
        profile = db.execute("SELECT * FROM users WHERE name = :name",
        name=currentuser)
        return render_template("profileedit.html", profile=profile)
    if request.method == "POST":
        years_knitting = request.form.get("years_knitting")
        favorite_color = request.form.get("favorite_color")
        about_me = request.form.get("about_me")
        print(years_knitting)
        print(favorite_color)
        print(about_me)
        db.execute("UPDATE users SET years_knitting = :years_knitting, favorite_color = :favorite_color, about_me = :about_me WHERE name = :name;",
        years_knitting=years_knitting, favorite_color=favorite_color, about_me=about_me, name=currentuser)
        return redirect("/profile")

@app.route("/profile/upload", methods=["GET", "POST"])
def profileupload():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Please upload a file')
            print('Please upload a file')
            return redirect(request.url)
        if file and is_allowed(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filename)
            location = "/static/profilepics/uploads/"
            newpiclocation = location + filename
            print(newpiclocation)
            db.execute("UPDATE users SET pic = :newpiclocation WHERE name = :name",
            newpiclocation=newpiclocation, name=session["user"])
            flash('Profile pic uploaded!')
            print('Profile pic uploaded!')
            return redirect("/profile")
        return("done")
    if request.method == "GET":
        return redirect("/profile/edit")



@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        session.pop("user", None)
        return redirect("/")
    if request.method == "POST":
        session.pop("user", None)
        return redirect("/")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        tosearch = request.form.get("tosearch")
        search = request.form.get("search")
        print(tosearch)
        print(search)
        results = db.execute("SELECT * FROM :tosearch WHERE name = :search",
        tosearch=tosearch, search=search)
        if len(results) == 0:
            flash("No results found with that query!")
            return redirect("/search")
        print(results)
        if (tosearch == "patterns"):
            return render_template("patterns.html", rows=results)
        if (tosearch == "projects"):
            return render_template("projects.html", rows=results)
        if (tosearch == "users"):
            return render_template("profile.html", profile=results)
        if (tosearch == "yarn"):
            return render_template("yarn.html", rows=results)
        return redirect("/search")
    if request.method == "GET":
        return render_template("search.html")

@app.route("/addfriend", methods=["POST"])
def addfriend():
    af = request.form.get("addfriend")
    currentuser = session["user"]
    currentuser_id = db.execute("SELECT id FROM users WHERE name = :currentuser", currentuser=currentuser)
    af_id = db.execute("SELECT id FROM users WHERE name = :af", af=af)
    db.execute("INSERT INTO friends(friender, friendee) VALUES (:currentuser_id, :af_id)", currentuser_id=currentuser_id[0]["id"], af_id=af_id[0]["id"])
    flash(af + " added to friends!")
    return redirect(request.referrer)

@app.route("/removefriend", methods=["POST"])
def removefriend():
    af = request.form.get("removefriend")
    currentuser = session["user"]
    currentuser_id = db.execute("SELECT id FROM users WHERE name = :currentuser", currentuser=currentuser)
    af_id = db.execute("SELECT id FROM users WHERE name = :af", af=af)
    db.execute("DELETE FROM friends WHERE friender = :currentuser_id AND friendee = :af_id", currentuser_id=currentuser_id[0]["id"], af_id=af_id[0]["id"])
    flash(af + " removed from friends!")
    return redirect(request.referrer)


