#FLASK_DEBUG=1
#export FLASK_APP=application
#export FLASK_ENV=development
import os
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from key import key

UPLOAD_FOLDER = "static/profilepics/uploads"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = key()

db = SQL("sqlite:///yarn.db")

# session object contains "user" (the username) and "user_id" (the id)

# global variables



# non-route functions

def getId(user):
    currentuser = user
    profile = db.execute("SELECT * FROM users WHERE name = :name",
    name=currentuser)
    currentuser_id=profile[0]["id"]
    return currentuser_id


def getUsername(id):
        profile = db.execute("SELECT * FROM users WHERE id = :id",
        id=id)
        name = profile[0]["name"]
        return name

def getProjectId(project, user):
    user_id=getId(user)
    project = db.execute("SELECT id FROM projects WHERE name = :name AND user_id=:user_id", name=project, user_id=user_id)
    project_id = project[0]["id"]
    return project_id


def is_allowed(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# routes

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html")

@app.errorhandler(500)
def not_found(error):
    return render_template("500.html")

@app.route("/welcome")
def welcome():
    return render_template("coverpage.html")

@app.route("/")
def index():
    if session.get('user') is None:
        return redirect("/welcome")
    else:
        return render_template("index.html")


@app.route("/projects/<user>", methods=["GET", "POST"])
def projects(user):
    user_id = getId(user)
    c_userid = session["user_id"]
    if request.method == "GET":
        rows = db.execute("SELECT * FROM projects WHERE user_id = :id", id = user_id)
        return render_template("projects.html", rows=rows, user=user)
    if request.method == "POST":
        name = request.form.get("name")
        yarn = request.form.get("yarn")
        yardage = request.form.get("yardage")
        notes = request.form.get("notes")
        db.execute("INSERT INTO projects(name, yarn, yardage, notes, user_id) VALUES (:name, :yarn, :yardage, :notes, :user_id)", name=name, yarn=yarn, yardage=yardage, notes=notes, user_id=user_id)
        rows = db.execute("SELECT name, yarn, yardage, notes, user_id FROM projects WHERE user_id = :id", id=c_userid)
        return redirect(url_for('projects', user=session["user"]))

@app.route("/projects/<user>/<project>", methods=["GET", "POST"])
def projectspages(user, project):
    if request.method == "GET":
        user_id = getId(user)
        rows = db.execute("SELECT * FROM projects WHERE user_id = :user_id AND name = :project", user_id=user_id, project=project)
        return render_template("projectpage.html", rows=rows, user=user)
    if request.method == "POST":
        return redirect(url_for('individualprojectedit', user=user, project=project))

@app.route("/projects/<user>/<project>/like", methods=["POST"])
def likeproject(user, project):
    if request.method == "POST":
        project_id=getProjectId(project, user)
        liker_id=getId(user)
        db.execute("INSERT INTO project_likes(project_id, liker_id) VALUES (:project_id, :liker_id)", project_id=project_id, liker_id=liker_id)
        return redirect(url_for('projectspages', user=user, project=project))

@app.route("/projects/<user>/<project>/edit", methods=["GET", "POST"])
def individualprojectedit(user, project):
    pid = getProjectId(user, project)
    if request.method == "GET":
        user_id = getId(user)
        rows = db.execute("SELECT name, yarn, yardage, notes, user_id FROM projects WHERE user_id = :user_id AND name = :project", user_id=user_id, project=project)
        return render_template("projectpageedit.html", rows=rows, user=user)
    if request.method == "POST":
        name = request.form.get("name")
        yarn = request.form.get("yarn")
        yardage = request.form.get("yardage")
        notes = request.form.get("notes")
        db.execute("UPDATE projects SET name=:name, yarn=:yarn, yardage=:yardage, notes=:notes WHERE id=:pid;", name=name, pid=pid, yarn=yarn, yardage=yardage, notes=notes)
        return redirect(url_for('projectspages', user=user, project=name))

@app.route("/yarn/<user>", methods=["GET", "POST"])
def yarn(user):
    user_id = getId(user)
    if request.method == "GET":
        rows = db.execute("SELECT name, yardage, fiber, weight FROM yarn WHERE user_id = :id GROUP BY name", id = user_id)
        return render_template("yarn.html", rows=rows, user=user)
    if request.method == "POST":
        name = request.form.get("name")
        yardage = request.form.get("yardage")
        fiber = request.form.get("fiber")
        weight = request.form.get("weight")
        db.execute("INSERT INTO yarn(name, yardage, fiber, weight, user_id) VALUES (:name, :yardage, :fiber, :weight, :user_id)", name=name, yardage=yardage, fiber=fiber, weight=weight, user_id=user_id)
        rows = db.execute("SELECT name, yardage, fiber, weight FROM yarn WHERE user_id = :id GROUP BY name", id = user_id)
        return render_template("yarn.html")

@app.route("/yarn/<user>/<yarn>", methods=["GET"])
def yarnpages(user, yarn):
    user_id = getId(user)
    rows = db.execute("SELECT name, yardage, fiber, weight, user_id FROM yarn WHERE user_id = :user_id AND name = :yarn", user_id=user_id, yarn=yarn)
    return render_template("yarnpage.html", rows=rows, user=user)

@app.route("/patterns", methods=["GET", "POST"])
def patterns():
    if request.method == "GET":
        print("trying")
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
            pwhash = db.execute("SELECT hash FROM users WHERE name = :name",
            name=request.form.get("name"))
            checker = check_password_hash(pwhash[0]["hash"], password)
            print(pwhash)
            print(password)
            print(checker)
        if checker == False:
            flash("Incorrect password")
            return redirect("/login")
        else:
            session["user"] = rows[0]["name"]
            session["user_id"] = rows[0]["id"]
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
        if len(password) < 10:
            flash("Password must be at least 10 characters long")
            return redirect("/register")
        has_digit = False
        for character in password:
            if character.isdigit():
                has_digit = True
        if has_digit==False:
            flash("Password must contain number")
            return redirect("/register")
        if str.isalnum(password)==True:
            flash("Password must contain non-alphanumeric character")
            return redirect("/register")
        if password != passwordconfirm:
            flash("Make sure passwords match")
            return redirect("/register")
        else:
            hash=generate_password_hash(password)
            db.execute("INSERT INTO users(name, hash) VALUES (:name, :hash)", name=name, hash=hash)
            row = db.execute("SELECT name FROM users WHERE name = :name", name=name)
            session["user"] = row[0]["name"]
            print(session)
            flash("Registered! Welcome to Knittery. Go to your profile to add more information about you.")
            return redirect("/")

    return render_template("public/sign_in.html")

@app.route("/profile/<user>")
def profileget(user):
    profile = db.execute("SELECT * FROM users WHERE name = :name",
    name=user)
    currentuser_id=session["user_id"]
    profile_id=getId(user)
    #get friends
    friends_id = db.execute("SELECT friendee FROM friends WHERE friender = :profile_id",
    profile_id=profile_id)
    friends=[]
    fn = 0
    for entry in friends_id:
        friendo = db.execute("SELECT name FROM users WHERE users.id = :friends_id",
        friends_id=friends_id[fn]["friendee"])
        frien = friendo[0]["name"]
        friends.append(frien)
        fn += 1
    print(friends)

    #get number of projects and stashed items
    projects = db.execute("SELECT * FROM projects WHERE user_id = :user_id", user_id=profile_id)
    stashed = db.execute("SELECT * FROM yarn WHERE user_id = :user_id GROUP BY name", user_id=profile_id)
    nprojects = len(projects)
    nstashed = len(stashed)

    #if not viewing own profile, see if current profile owner is one of your friends
    isfriend = False
    if user != session["user"]:
        loggedinUser = db.execute("SELECT * FROM users WHERE name = :name",
        name=session["user"])
        loggedinUser_id = loggedinUser[0]["id"]
        friendquery = db.execute("SELECT * FROM friends WHERE friender = :loggedinUser_id AND friendee = :profile_id",
        loggedinUser_id = loggedinUser_id, profile_id=profile_id)
        print(friendquery)
        if len(friendquery) == 0:
            print("not friends")
        else:
            isfriend = True
            print(friendquery)
    return render_template("profile.html", profile=profile, friends=friends, isfriend=isfriend, nprojects=nprojects, nstashed=nstashed)

@app.route("/profile", methods=["GET", "POST"])
def userprofile():
    if request.method == "GET":
        username=session["user"]
        return redirect(url_for('profileget', user=username))
    if request.method == "POST":
        print(' why are we poast')
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
        return render_template("logout.html")
    if request.method == "POST":
        session.pop("user", None)
        session.pop("user_id", None)
        return redirect("/")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        tosearch = request.form.get("tosearch")
        search = request.form.get("search")
        print(tosearch)
        print(search)
        searchwild = "%" + search + "%"
        print(searchwild)
        results = db.execute("SELECT * FROM :tosearch WHERE name LIKE :search",
        tosearch=tosearch, search=searchwild)
        if len(results) == 0:
            flash("No results found with that query!")
            return redirect("/search")
        print(results)
        # if (tosearch == "patterns"):
        #     return render_template("patterns.html", rows=results)
        if (tosearch == "projects" or tosearch == "yarn"):
            for result in results:
                print(getUsername(result["user_id"]))
                # need to add the username to result
                result["uname"] = getUsername(result["user_id"])
            puser = db.execute("SELECT name FROM :tosearch WHERE id=:user_id", user_id=int(results[0]["user_id"]), tosearch=tosearch)
            return render_template("search.html", results=results, puser=puser, tosearch=tosearch)
        if (tosearch == "users"):
            return render_template("search.html", results=results, tosearch=tosearch)
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
