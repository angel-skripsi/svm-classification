from mysql.connector import Error
import mysql.connector
import pandas as pd

#Load and insert CSV data that contains manual classification for Label for each Wilayah, Kecamatan, and Tahun to database
labeldata = pd.read_csv('resources/full_labeling.csv', index_col=False, delimiter = ';')
labeldata.head()
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT database();")
    record = cursor.fetchone()
    print("You're connected to database:", record)
    cursor.execute('DROP TABLE IF EXISTS labeling_y_raw;')
    print('Creating table labeling_y_raw')
    cursor.execute("CREATE TABLE labeling_y_raw (Id int(20) NOT NULL auto_increment,Wilayah varchar(255),Kecamatan varchar(255),Tahun int(4),Label varchar(255),PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table labeling_y_raw is created")
    for i,row in labeldata.iterrows():
      sql = "INSERT INTO heroku_97dccdc5801db01.labeling_y_raw (Wilayah, Kecamatan, Tahun, Label) VALUES (%s,%s,%s,%s)"
      cursor.execute(sql, tuple(row))
      conn.commit()
    print("Record for labeling_y_raw inserted")
except Error as e:
  print("Error while connecting to MySQL", e)

#Select Wilayah data from labeling_y_raw and mapping it to Id and save it to database
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS mapping_wilayah;')
    print('Creating table mapping_wilayah')
    cursor.execute("CREATE TABLE mapping_wilayah (Id int(20) NOT NULL auto_increment,Wilayah varchar(255),PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table mapping_wilayah is created")
    cursor.execute("SELECT DISTINCT Wilayah FROM labeling_y_raw ORDER BY 1")
    record = cursor.fetchall()
    for x in record:
      sql = "INSERT INTO heroku_97dccdc5801db01.mapping_wilayah (Wilayah) VALUES (%s)"
      cursor.execute(sql, x)
      conn.commit()
    print("Record for mapping_wilayah inserted")
except Error as e:
  print("Error while connecting to MySQL", e)

#Select Kecamatan data from labeling_y_raw and mapping it to Id and save it to database
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS mapping_kecamatan;')
    print('Creating table mapping_kecamatan')
    cursor.execute("CREATE TABLE mapping_kecamatan (Id int(20) NOT NULL auto_increment,Kecamatan varchar(255),PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table mapping_kecamatan is created")
    cursor.execute("SELECT DISTINCT Kecamatan FROM labeling_y_raw ORDER BY 1")
    record = cursor.fetchall()
    for x in record:
      sql = "INSERT INTO heroku_97dccdc5801db01.mapping_kecamatan (Kecamatan) VALUES (%s)"
      cursor.execute(sql, x)
      conn.commit()
    print("Record for mapping_kecamatan inserted")
except Error as e:
  print("Error while connecting to MySQL", e)
  
#Select Label data from labeling_y_raw and mapping it to Id and save it to database
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS mapping_label;')
    print('Creating table mapping_label')
    cursor.execute("CREATE TABLE mapping_label (Id int(20) NOT NULL auto_increment,Label varchar(255),PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table mapping_label is created")
    cursor.execute("SELECT DISTINCT Label FROM labeling_y_raw ORDER BY 1")
    record = cursor.fetchall()
    for x in record:
      sql = "INSERT INTO heroku_97dccdc5801db01.mapping_label (Label) VALUES (%s)"
      cursor.execute(sql, x)
      conn.commit()
    print("Record for mapping_label inserted")
except Error as e:
  print("Error while connecting to MySQL", e)

#Select all data from labeling_y_raw and mapping it to Id and save it to database
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS labeling_y;')
    print('Creating table labeling_y')
    cursor.execute("CREATE TABLE labeling_y (Id int(20), Id_wilayah int(20), Wilayah varchar(255), Id_kecamatan int(20), Kecamatan varchar(255), Tahun int(4), Id_label int(20), Label varchar(255), PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table labeling_y is created")
    cursor.execute("SELECT a.Id, b.Id AS Id_wilayah, a.Wilayah, c.id AS Id_kecamatan, a.Kecamatan, a.Tahun, d.Id AS Id_label, a.Label FROM `labeling_y_raw` AS a LEFT JOIN `mapping_wilayah` AS b ON a.Wilayah = b.Wilayah LEFT JOIN `mapping_kecamatan` AS c ON a.Kecamatan = c.Kecamatan LEFT JOIN `mapping_label` AS d ON a.Label = d.Label ORDER BY 1")
    record = cursor.fetchall()
    for x in record:
      sql = "INSERT INTO heroku_97dccdc5801db01.labeling_y (Id, Id_wilayah, Wilayah, Id_kecamatan, Kecamatan, Tahun, Id_label, Label) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
      cursor.execute(sql, x)
      conn.commit()
    print("Record for labeling_y inserted")
except Error as e:
  print("Error while connecting to MySQL", e)