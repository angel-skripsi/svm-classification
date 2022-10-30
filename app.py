from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask_mysqldb import MySQL
from TestHello import my_function

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'us-cdbr-east-06.cleardb.net'
app.config['MYSQL_USER'] = 'b539dadf046091'
app.config['MYSQL_PASSWORD'] = '5b842ab0'
app.config['MYSQL_DB'] = 'heroku_97dccdc5801db01'

mysql = MySQL(app)

@app.route('/login')
def index():
   return render_template("index.html")

@app.route("/hello/")
def home():
    return "Hello, Flask!"

@app.route('/<int:number>/')
def incrementer(number):
    return "Incremented number is " + str(number+1)

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
def test_json():
    content = request.json
    return (content['param1'] + content['param2'])

@app.route("/selectdb/")
def selectdb():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM test")
    rv = cursor.fetchall()
    cursor.close()
    payload = []
    content = {}
    for result in rv:
       content = {'id': result[0], 'name': result[1], 'email': result[2], 'phone': result[3], 'birthdate': result[4]}
       payload.append(content)
       content = {}
    return jsonify(payload)
