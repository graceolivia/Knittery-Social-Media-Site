from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, url_for, flash
from key import key

app = Flask(__name__)
app.config["SECRET_KEY"] = key()


db = SQL("sqlite:///yarn.db")

@app.route("/")
def index():
       return render_template("index.html")


@app.route("/projects", methods=["GET", "POST"])
def projects():
    user_id = 1
    if request.method == "GET":
        rows = db.execute("SELECT pattern, yarn, yardage, notes, user_id FROM projects WHERE user_id = :id", id = user_id)
        return render_template("projects.html", rows=rows)
    if request.method == "POST":
        pattern = request.form.get("pattern")
        yarn = request.form.get("yarn")
        yardage = request.form.get("yardage")
        notes = request.form.get("notes")
        user_id = 1
        db.execute("INSERT INTO projects(pattern, yarn, yardage, notes, user_id) VALUES (:pattern, :yarn, :yardage, :notes, :user_id)", pattern=pattern, yarn=yarn, yardage=yardage, notes=notes, user_id=user_id)
        rows = db.execute("SELECT pattern, yarn, yardage, notes, user_id FROM projects WHERE user_id = :id", id = user_id)
        return render_template("projects.html", rows=rows)

@app.route("/yarn", methods=["GET", "POST"])
def yarn():
    user_id = 1
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
    user_id = 1
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
            print("Incorrect password")
            return redirect("/login")
        else:
            session["user"] = rows[0]["name"]
            print(session)
            print("session username set")
            return redirect("/")

    return render_template("public/sign_in.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM users WHERE name = :name",
                name=request.form.get("name"))
        if len(rows) == 1:
            flash("Username In Use Already")
            return redirect("/register")
            #else add it to the table
        else:
            session["user"] = rows[0]["name"]
            print(session)
            print("session username set")
            return redirect("/")

    return render_template("public/sign_in.html")

@app.route("/profile")
def profile():
    if not session.get("user") is None:
        currentuser = session["user"]
        profile = db.execute("SELECT * FROM users WHERE name = :name",
        name=currentuser)
        print(profile)
        return render_template("profile.html", profile=profile)
    else:
        print("No user logged in.")
        flash("No user logged in. Please log in.")
        return redirect("/login")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "GET":
        session.pop("user", None)
        return redirect("/")
    if request.method == "POST":
        session.pop("user", None)
        return redirect("/")

