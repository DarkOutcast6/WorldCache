from flask import Flask, redirect, render_template, request
import pycaching

# geocaching = pycaching.login("user", "pass")

app = Flask(__name__)


# @app.route('/login', methods=["GET"])
# def loginForm():
#  return render_template("login.html")

# @app.route('/', methods=["POST"])
# def processForm():
#   form = request.form
#   print(form)

# if __name__ == '__main__':
#     app.run('0.0.0.0', 81)

def error(type):
  if type == "loginNotFound":
    return render_template('login.html', error="Login Error")
    return redirect('/login')