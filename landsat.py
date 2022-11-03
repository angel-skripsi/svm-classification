from PIL import Image as im
from mysql.connector import Error
import mysql.connector
import numpy as np
import pandas as pd
import warnings
import os
import glob
import fnmatch
import rasterio
import math

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
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS landsat_8_original;')
    print('Creating table landsat_8_original')
    cursor.execute("CREATE TABLE landsat_8_original (Id int(20) NOT NULL auto_increment, FileName text, Wilayah varchar(255), Kecamatan varchar(255), Tahun int(4), NDVI varchar(255), SAVI varchar(255), EVI varchar(255), PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table landsat_8_original is created")
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
            ndvi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\original\\ndvi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
            ndvi_path = ndvi_image.save(ndvi_image_path, "TIFF")
            savi_image = im.fromarray(savi)
            savi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\original\\savi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
            savi_path = savi_image.save(savi_image_path, "TIFF")
            evi_image = im.fromarray(evi)
            evi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\original\\evi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
            evi_path = evi_image.save(evi_image_path, "TIFF")    
            sql = "INSERT INTO smt_7_skripsi.landsat_8_original (FileName, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val = (B2_PATH+";"+B4_PATH+";"+B5_PATH, wilayah, kecamatan, year, ndvi_image_path, savi_image_path, evi_image_path)
            cursor.execute(sql, val)
            conn.commit()
            count_num = count_num + 1
            print(count_num, "Record for landsat_8_original inserted")
except Error as e:
  print("Failed inserting data into MySQL table {}".format(e))

#Select all data from landsat_8_original and do resized
data_citra = []
data_training = pd.DataFrame(columns=['NDVI','SAVI','EVI'])
count_num2 = 0
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS landsat_8_resized;')
    print('Creating table landsat_8_resized')
    cursor.execute("CREATE TABLE landsat_8_resized (Id int(20) NOT NULL, FileName text, Wilayah varchar(255), Kecamatan varchar(255), Tahun int(4), NDVI varchar(255), SAVI varchar(255), EVI varchar(255), PRIMARY KEY(Id))")
    print("Table landsat_8_resized is created")
    cursor.execute("SELECT Id, Filename, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI FROM `landsat_8_original`")
    record = cursor.fetchall()
    for x in record:
      data_citra.append(x)
    for i in range(len(data_citra)):
      NDVI = data_citra[i][5]
      NDVI_name = data_citra[i][5].split("\\")
      SAVI = data_citra[i][6]
      SAVI_name = data_citra[i][6].split("\\")
      EVI = data_citra[i][7]
      EVI_name = data_citra[i][7].split("\\")
      with open(NDVI, "rb") as image_file2:
        x2 = im.open(image_file2)
        w2, h2 = x2.size
        current_w2 = math.ceil(w2/10)
        current_h2 = math.ceil(h2/10)
        new_image2 = x2.resize((current_w2, current_h2))
        new_image2_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\resized\\ndvi\\"+NDVI_name[11]+'.tif'
        new_image2.save(new_image2_path, "TIFF")  
      with open(SAVI, "rb") as image_file3:
        x3 = im.open(image_file3)
        w3, h3 = x3.size
        current_w3 = math.ceil(w3/10)
        current_h3 = math.ceil(h3/10)
        new_image3 = x3.resize((current_w3, current_h3))
        new_image3_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\resized\\savi\\"+SAVI_name[11]+'.tif'
        new_image3.save(new_image3_path, "TIFF")  
      with open(EVI, "rb") as image_file4:
        x4 = im.open(image_file4)
        w4, h4 = x4.size
        current_w4 = math.ceil(w4/10)
        current_h4 = math.ceil(h4/10)
        new_image4 = x4.resize((current_w4, current_h4))
        new_image4_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\resized\\evi\\"+EVI_name[11]+'.tif'
        new_image4.save(new_image4_path, "TIFF")  
      sql = "INSERT INTO smt_7_skripsi.landsat_8_resized (Id, FileName, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
      val = (data_citra[i][0], data_citra[i][1], data_citra[i][2], data_citra[i][3], data_citra[i][4], new_image2_path, new_image3_path, new_image4_path)
      cursor.execute(sql, val)
      conn.commit()
      count_num2 = count_num2 + 1
      print(count_num2, "Record for landsat_8_resized inserted")
except Error as e:
  print("Error while connecting to MySQL", e)

#Select all data from landsat_8_raw and mapping it to Id and save it to database
count_num_3 = 0
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS landsat_8;')
    print('Creating table landsat_8')
    cursor.execute("CREATE TABLE landsat_8 (Id int(20), Filename text, Id_wilayah int(20), Wilayah varchar(255), Id_kecamatan int(20), Kecamatan varchar(255), Tahun int(4), NDVI varchar(255), SAVI varchar(255), EVI varchar(255), Id_label int(20), Label varchar(255), PRIMARY KEY(Id))")
    cursor.execute("SET @@auto_increment_increment=1;")
    print("Table landsat_8 is created")
    cursor.execute("SELECT a.Id, a.FileName, b.Id AS Id_wilayah, a.Wilayah, c.id AS Id_kecamatan, a.Kecamatan, a.Tahun, a.NDVI, a.SAVI, a.EVI, e.Id_label, e.Label FROM `landsat_8_resized` AS a LEFT JOIN `mapping_wilayah` AS b ON a.Wilayah = b.Wilayah LEFT JOIN `mapping_kecamatan` AS c ON a.Kecamatan = c.Kecamatan LEFT JOIN `labeling_y` AS e ON a.Wilayah = e.Wilayah AND a.Kecamatan = e.Kecamatan AND a.Tahun = e.Tahun ORDER BY 1")
    record = cursor.fetchall()
    for x in record:
      sql = "INSERT INTO smt_7_skripsi.landsat_8 (Id, Filename, Id_wilayah, Wilayah, Id_kecamatan, Kecamatan, Tahun, NDVI, SAVI, EVI, Id_label, Label) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
      cursor.execute(sql, x)
      conn.commit()
      count_num_3 = count_num_3 + 1
      print(count_num_3, "Record for landsat_8 inserted")
except Error as e:
  print("Error while connecting to MySQL", e)