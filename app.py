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