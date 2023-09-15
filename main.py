# Setup for main.py
from flask import Flask, redirect, render_template, request
from replit import db
import pycaching, os

app = Flask(__name__)

# Predefined vars
geocaching = None

geocaching = pycaching.login(os.environ['username'], os.environ['pw'])

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

# Errors
@app.errorhandler(400)
def _400(e):
  return render_template('400.html', error=e)

@app.errorhandler(404)
def _404(e):
  return render_template('404.html', error=e)

@app.errorhandler(405)
def _405(e):
  return render_template('405.html', error=e)

@app.errorhandler(500)
def _500(e):
  return render_template('500.html', error=e)
  
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

@app.route("/search/<user_input>")
def searching(user_input):
  try:
    results = list(geocaching.search(pycaching.Point.from_string(user_input),20))
    return render_template("searching.html", results = results)
  except:
    try:
      results = list(geocaching.advanced_search({"st": "some cache","sort": "distance"},20))
      return render_template("searching.html", results=results)
    except:
      return render_template("searching.html", results="no-results")

@app.route("/cache/<cacheWP>")
def cache(cacheWP):
  cache = geocaching.get_cache(wp=cacheWP)
  
  def to_dict(log):
    return {
      name: str(getattr(log, name, 'null'))
      for name in 'author text type uuid visited'.split()
    }

  logs = [to_dict(log) for log in cache.load_logbook()]
  # logCount = int(cache.log_counts.get("<Type.owner_maintenance: '46'>")) + int(cache.log_counts.get("<Type.found_it: '2'>"))
  
  return render_template("cache.html", cacheName = cache.name, cacheWP = cache.wp, cacheAuthor = cache.author, cacheDescription = cache.description, cacheTerrain = cache.terrain, cacheDifficulty = cache.difficulty, cacheType = str(cache.type).split(".")[1], logs = logs, logCount = len(logs))

@app.route("/cache/<cacheWP>/log")
def logCache(cacheWP):
  
  return render_template("logCache.html", cacheName = cache.name)

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
  user_input = form["search-caches"]
  try:
    geocaching.search(pycaching.Point.from_string(user_input),1)
    return redirect(f"/search/{user_input}")
  except:
    if user_input.startswith("GC"):
      try:
        cacheWP = user_input
        return redirect(f"/cache/{cacheWP}")
      except:
        pass
    else:
      try:
        geocaching.advanced_search({"st": user_input,"sort": "distance"},1)
        return redirect(f"/search/{user_input}")
        # https://www.geocaching.com/play/results/?st=the+cool+cache&oid=-1&ot=query&asc=true&sort=distance
      except:
        user_input = "no-results"
        return redirect(f"/search/{user_input}")

@app.route("/search/<user_input>", methods=["POST"])
def searchingForm(user_input):
  global cacheWP
  form = request.form
  user_input = form["search-caches"]
  try:
    geocaching.search(pycaching.Point.from_string(user_input),1)
    return redirect(f"/search/{user_input}")
  except:
    if user_input.startswith("GC"):
      try:
        cacheWP = user_input
        return redirect(f"/cache/{cacheWP}")
      except:
        pass
    else:
      try:
        geocaching.advanced_search({"st": user_input,"sort": "distance"},20)
        return redirect(f"/search/{user_input}")
      except:
        user_input = "no-results"
        return redirect(f"/search/{user_input}")
# Run Program
if __name__ == '__main__':
    app.run('0.0.0.0', 81)