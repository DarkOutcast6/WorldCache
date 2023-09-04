# Setup for main.py
from flask import Flask, redirect, render_template, request
import pycaching

app = Flask(__name__)

# Predefined vars
geocaching = None
cacheWP = None

# logged in?
if geocaching == None:
  loggedIn = False
else:
  loggedIn = True

# Error Function
def error(type):
  if type == "loginNotFound":
    return render_template('login.html', error="Incorrect username or password!")

# Logged In Var
@app.context_processor
def contextProcessor():
  return dict(loggedIn=loggedIn)

# App Routes
@app.route("/")
def index():
  return render_template("index.html")

@app.route("/home")
def hello():
  return render_template("home.html")
  
@app.route("/about")
def about():
  return render_template("about.html")
  
@app.route("/search")
def search():
  return render_template("search.html")

@app.route("/cache/<cacheWP>")
def cache(cacheWP):
  cache = geocaching.get_cache(wp=cacheWP)
  return render_template("cache.html", cacheName = cache.name, cacheAuthor = cache.author, cacheDescription = cache.description, cacheTerrain = cache.terrain, cacheDifficulty = cache.difficulty, cacheType = str(cache.type).split(".")[1])

@app.route("/login")
def login():
  return render_template("login.html")

# Login Form
@app.route('/login', methods=["POST"])
def loginForm():
  global geocaching
  global loggedIn
  form = request.form
  try:
    geocaching = pycaching.login(form["username"], form["password"])
    loggedIn = True
    return redirect("/home")
  except:
    return error("loginNotFound")

# Search
@app.route("/search", methods=["POST"])
def searchForm():
  global cacheWP
  form = request.form
  if True:#form["search-caches"][1] == "G" and form["search-caches"][2] == "C":
    # try:
    cacheWP = form["search-caches"]
    return redirect(f"/cache/{cacheWP}")
    # except:
    #   raise ValueError('Invalid GUID')
    #   return render_template("search.html")
  else:
    raise ValueError('No results')
    return render_template("search.html")
    
# Run Program
if __name__ == '__main__':
    app.run('0.0.0.0', 81)