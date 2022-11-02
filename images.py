from mysql.connector import Error
import mysql.connector
import os
import glob
import fnmatch
import base64

#Select all data from labeling_y_raw and mapping it to Id and save it to database
root_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\DATASET"
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS images;')
    print('Creating table images')
    cursor.execute("CREATE TABLE images (Id int(20) NOT NULL auto_increment, Wilayah varchar(255), Kecamatan varchar(255), Tahun int(4), Band_2 longtext, Band_4 longtext, Band_5 longtext, PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table images is created")
    for year in os.listdir(root_path):
      for month in os.listdir(root_path+"\\"+year):
        bulan = month.split("-")[1]
        for wilayah in os.listdir(root_path+"\\"+year+"\\"+month):
          for kecamatan in os.listdir(root_path+"\\"+year+"\\"+month+"\\"+wilayah):
            B4_PATH = "" 
            B5_PATH = "" 
            B2_PATH = ""
            for filename in glob.iglob(root_path+"\\"+year+"\\"+month+"\\"+wilayah+"\\"+kecamatan + "\\" + '*.tif', recursive=True):
              if fnmatch.fnmatch (filename, '*B5*') or fnmatch.fnmatch (filename, '*TIF5*'):
                B5_PATH = filename
                with open(B5_PATH, "rb") as image_file:
                  b5_image_64_encode = base64.b64encode(image_file.read())
              elif fnmatch.fnmatch (filename, '*B4*') or fnmatch.fnmatch (filename, '*TIF4*'):
                B4_PATH = filename
                with open(B4_PATH, "rb") as image_file:
                  b4_image_64_encode = base64.b64encode(image_file.read())
              elif fnmatch.fnmatch (filename, '*B2*') or fnmatch.fnmatch (filename, '*TIF2*'):
                B2_PATH = filename
                with open(B2_PATH, "rb") as image_file:
                  b2_image_64_encode = base64.b64encode(image_file.read())
            images_data = wilayah,kecamatan,year,b2_image_64_encode,b4_image_64_encode,b5_image_64_encode
            sql = "INSERT INTO heroku_97dccdc5801db01.images (Wilayah, Kecamatan, Tahun, Band_2, Band_4, Band_5) VALUES (%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,images_data)
            conn.commit()
            print("Record for images inserted")
except Error as e:
  print("Error while connecting to MySQL", e)