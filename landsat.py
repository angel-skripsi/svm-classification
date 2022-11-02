from PIL import Image as im
from mysql.connector import Error
import mysql.connector
import numpy as np
import pandas as pd
import os
import glob
import fnmatch
import rasterio

def ndvi_calc(b4_path, b5_path):
  if b4_path != "" and b5_path != "":
    b4i = rasterio.open(b4_path)
    b5i = rasterio.open(b5_path)
    b5 = b5i.read(1).astype('float64')
    b4 = b4i.read(1).astype('float64')
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = np.where(np.add(b5,b4) == 0., 0, np.divide(np.subtract(b5,b4),np.add(b5,b4)))
    return ndvi
  else:
    return None
  
def savi_calc(b4_path, b5_path):
  if b4_path != "" and b5_path != "":
    b4i = rasterio.open(b4_path)
    b5i = rasterio.open(b5_path)
    b5 = b5i.read(1).astype('float64')
    b4 = b4i.read(1).astype('float64')
    np.seterr(divide='ignore', invalid='ignore')
    savi = np.where((b5+b4+0.5) == 0., 0, ((b5-b4)*1.5)/(b5+b4+0.5))
    return savi
  else:
    return None

def evi_calc(b2_path, b4_path, b5_path):
  if b4_path != "" and b5_path != "" and b2_path != "":
    b2i = rasterio.open(b2_path)
    b4i = rasterio.open(b4_path)
    b5i = rasterio.open(b5_path)
    b2 = b2i.read(1).astype('float64')
    b5 = b5i.read(1).astype('float64')
    b4 = b4i.read(1).astype('float64')
    np.seterr(divide='ignore', invalid='ignore')
    evi = np.where((b5+(6*b4)-(7.5*b2)+0.5) == 0., 0, ((b5-b4)*2.5)/(b5+(6*b4)-(7.5*b2)+0.5))
    return evi
  else:
    return None

#Load and insert TIF and Band data to database
root_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset"
list_Image = []
count_num = 0
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS landsat_8_raw;')
    print('Creating table landsat_8_raw')
    cursor.execute("CREATE TABLE landsat_8_raw (Id int(20) NOT NULL auto_increment, FileName varchar(255), Wilayah varchar(255), Kecamatan varchar(255), Tahun int(4), NDVI varchar(255), SAVI varchar(255), EVI varchar(255), PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    cursor.execute("SET @MAX_QUESTIONS=0;") #This will set unlimited
    cursor.execute("FLUSH PRIVILEGES;")
    print("Table landsat_8_raw is created")
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
              elif fnmatch.fnmatch (filename, '*B4*') or fnmatch.fnmatch (filename, '*TIF4*'):
                B4_PATH = filename
              elif fnmatch.fnmatch (filename, '*B2*') or fnmatch.fnmatch (filename, '*TIF2*'):
                B2_PATH = filename
            #Calculate NDVI, SAVI, EVI and save to database
            ndvi = ndvi_calc(B4_PATH, B5_PATH)
            savi = savi_calc(B4_PATH, B5_PATH)
            evi = evi_calc(B2_PATH, B4_PATH, B5_PATH)
            ndvi_image = im.fromarray(ndvi)
            ndvi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\ndvi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
            ndvi_path = ndvi_image.save(ndvi_image_path, "TIFF")
            savi_image = im.fromarray(savi)
            savi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\savi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
            savi_path = savi_image.save(savi_image_path, "TIFF")
            evi_image = im.fromarray(evi)
            evi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\evi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
            evi_path = evi_image.save(evi_image_path, "TIFF")    
            sql = "INSERT INTO heroku_97dccdc5801db01.landsat_8_raw (FileName, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val = (B2_PATH+";"+B4_PATH+";"+B5_PATH, wilayah, kecamatan, year, ndvi_image_path, savi_image_path, evi_image_path)
            cursor.execute(sql, val)
            conn.commit()
            count_num = count_num + 1
            print(count_num, "Record for landsat_8_raw inserted")
except Error as e:
  print("Failed inserting data into MySQL table {}".format(e))

# #Select all data from labeling_y_raw and mapping it to Id and save it to database
# root_path = "C:\Users\Angellina\Dropbox\My PC (LAPTOP-9GTQMRFV)\Desktop\ALL SKRIPSI\GITHUB\dataset"
# try:
#   conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
#   if conn.is_connected():
#     print("=======================================================================")
#     cursor = conn.cursor()
#     cursor.execute('DROP TABLE IF EXISTS images;')
#     print('Creating table images')
#     cursor.execute("CREATE TABLE images (Id int(20) NOT NULL auto_increment, Wilayah varchar(255), Kecamatan varchar(255), Tahun int(4), Band_2 longtext, Band_4 longtext, Band_5 longtext, PRIMARY KEY(Id))")
#     cursor.execute("SET @@auto_increment_increment=1;")
#     print("Table images is created")
#     for year in os.listdir(root_path):
#       for month in os.listdir(root_path+"\\"+year):
#         bulan = month.split("-")[1]
#         for wilayah in os.listdir(root_path+"\\"+year+"\\"+month):
#           for kecamatan in os.listdir(root_path+"\\"+year+"\\"+month+"\\"+wilayah):
#             B4_PATH = "" 
#             B5_PATH = "" 
#             B2_PATH = ""
#             for filename in glob.iglob(root_path+"\\"+year+"\\"+month+"\\"+wilayah+"\\"+kecamatan + "\\" + '*.tif', recursive=True):
#               if fnmatch.fnmatch (filename, '*B5*') or fnmatch.fnmatch (filename, '*TIF5*'):
#                 B5_PATH = filename
#                 with open(B5_PATH, "rb") as image_file:
#                   b5_image_64_encode = base64.b64encode(image_file.read())
#               elif fnmatch.fnmatch (filename, '*B4*') or fnmatch.fnmatch (filename, '*TIF4*'):
#                 B4_PATH = filename
#                 with open(B4_PATH, "rb") as image_file:
#                   b4_image_64_encode = base64.b64encode(image_file.read())
#               elif fnmatch.fnmatch (filename, '*B2*') or fnmatch.fnmatch (filename, '*TIF2*'):
#                 B2_PATH = filename
#                 with open(B2_PATH, "rb") as image_file:
#                   b2_image_64_encode = base64.b64encode(image_file.read())
#             images_data = wilayah,kecamatan,year,b2_image_64_encode,b4_image_64_encode,b5_image_64_encode
#             sql = "INSERT INTO heroku_97dccdc5801db01.images (Wilayah, Kecamatan, Tahun, Band_2, Band_4, Band_5) VALUES (%s,%s,%s,%s,%s,%s)"
#             cursor.execute(sql,images_data)
#             conn.commit()
#             print("Record for images inserted")
# except Error as e:
#   print("Error while connecting to MySQL", e)