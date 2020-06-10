from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, url_for


app = Flask(__name__)

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
        
@app.route("/profile")
def profile():

    if not session.get("USERNAME") is None:
        username = session.get("USERNAME")
        user = users[username]
        return render_template("public/profile.html", user=user)
    else:
        print("No username found in session")
        return redirect(url_for("sign_in"))
