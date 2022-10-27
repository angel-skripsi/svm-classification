from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from TestHello import my_function
app = Flask(__name__)

@app.route('/login')
def index():
   return render_template("index.html")

@app.route("/hello/")
def home():
    return "Hello, Flask!"

@app.route('/<int:number>/')
def incrementer(number):
    return "Incremented number is " + str(number+1)

# @app.route('/<string:name>/')
# def hello(name):
#     return "Hello " + name;

@app.route('/person/')
def person():
    return jsonify({'name':'Jimit',
                    'address':'India'})

@app.route('/calculate')
def calculate():
  x = request.args.get('x', type = int)
  y = request.args.get('y', type = int)
  return str(my_function(x,y))

@app.route('/login_test',methods = ['POST'])
def login():
    user = request.form['nm'];
    return user

@app.route('/test_json',methods = ['POST'])
def login():
    content = request.json
    return (content['param1'] + content['param2'])
