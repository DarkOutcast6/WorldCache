# Setup for main.py
from flask import Flask, redirect, render_template, request
from replit import db
import pycaching, os, folium, base64, re

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

# Functions
def svg_to_dataurl(path_to_svg):
  with open(path_to_svg, 'r') as f:
    svg = f.read()
  return "data:image/svg+xml;base64," + base64.b64encode(svg.encode('utf-8')).decode('utf-8')
  
def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd;

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3])
    lng = dms2dd(parts[4], parts[5], parts[6], parts[7])

    return (lat, lng)

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
  # Get logs
  def to_dict(log):
    return {
      name: str(getattr(log, name, 'null'))
      for name in 'author text type uuid visited'.split()
    }

  logs = [to_dict(log) for log in cache.load_logbook()]

  # Coordinate Fixing
  cache_loc = str(cache.location)
  negatives = {"S":False, "W":False}
  cache_loc = cache_loc.replace("N","")
  if "S" in cache_loc:
    negatives["S"] = True
    cache_loc = cache_loc.replace("S","")
  cache_loc = cache_loc.replace("E","")
  if "W" in cache_loc:
    negatives["W"] = True
    cache_loc = cache_loc.replace("S","")

  cache_loc = cache_loc.replace("d","")
  cache_loc = cache_loc.replace("s","")
  cache_loc = cache_loc.replace("m","")
  cache_loc = [str(parse_dms(cache_loc)[0]),str(parse_dms(cache_loc)[1])]

  if negatives.get("S"):
    cache_loc = ["-" + cache_loc[0],cache_loc[1]]

  if negatives.get("W"):
    cache_loc = [cache_loc[0],"-" + cache_loc[1]]

  del negatives
  m = folium.Map(location=cache_loc, zoom_start=12, tiles=folium.TileLayer("OpenStreetMap", show=False, name="OpenStreet Map"))

  # Layer Control
  # folium.TileLayer().add_to(m)
  folium.TileLayer("Stamen Terrain", show=False, name="Stamen Terrain").add_to(m)
  folium.TileLayer("Cartodb Positron", show=False, name="Cartodb Positron", attr='contributors &copy; <a href="https://carto.com/attributions">CARTO</a>').add_to(m)
  folium.TileLayer("Esri.WorldImagery", show=False, name="Sattelite", attr='contributors &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community').add_to(m)
  folium.LayerControl(position = "bottomright").add_to(m)
  
  popup_content = """
    <div id="custom-popup" style="display: none;">
        <h2>Custom Popup</h2>
        <p>This is a custom div element that shows up when you click the marker.</p>
    </div>
  """

  try:
    custom_icon = folium.CustomIcon(icon_image=svg_to_dataurl(f'static/imgs/type_{str(cache.type).split(".")[1]}.svg'), icon_size=(30,30))
    marker = folium.Marker(location=cache_loc, icon=custom_icon)
    marker.add_to(m)
  except:
    folium.Marker(location=cache_loc, icon=folium.Icon(color="green")).add_to(m)

  js_code = """
    <script>
    var marker = L.DomUtil.get("custom-popup");

    marker.addEventListener("click", function() {
        var popup = L.DomUtil.get("custom-popup");
        if (popup.style.display === "none") {
            popup.style.display = "block";
        } else {
            popup.style.display = "none";
        }
    });
    </script>
  """

  m.get_root().html.add_child(folium.Element(js_code))

  popup_content = """
    <div id="custom-popup" style="display: none;">
        <h2>{}</h2>
        <p>{}</p>
    </div>
  """.format(cache.name, cache.description)

  map_html = m._repr_html_()
  return render_template("cache.html", cacheName = cache.name, cacheWP = cache.wp, cacheAuthor = cache.author, cacheDescription = cache.description_html, cacheTerrain = cache.terrain, cacheDifficulty = cache.difficulty, cacheHint = cache.hint, cacheType = str(cache.type).split(".")[1], cacheSize = str(cache.size).split(".")[1].replace("_"," ").capitalize(), logs = logs, logCount = len(logs), map_html = map_html, popup_content = popup_content)

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
@app.route("/home", methods=["POST"])
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