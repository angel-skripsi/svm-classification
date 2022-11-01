from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'us-cdbr-east-06.cleardb.net'
app.config['MYSQL_USER'] = 'b539dadf046091'
app.config['MYSQL_PASSWORD'] = '5b842ab0'
app.config['MYSQL_DB'] = 'heroku_97dccdc5801db01'

mysql = MySQL(app)

@app.route("/select_labeling_y/")
def select_labeling_y():
  cursor = mysql.connection.cursor()
  cursor.execute("SELECT Wilayah, Kecamatan, Tahun, Label FROM labeling_y")
  rv = cursor.fetchall()
  cursor.close()
  payload = []
  content = {}
  for result in rv:
    content = {'Wilayah': result[0], 'Kecamatan': result[1], 'Tahun': result[2], 'Label': result[3]}
    payload.append(content)
    content = {}
  return jsonify(payload)