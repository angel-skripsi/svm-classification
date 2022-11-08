from PIL import Image as im
from mysql.connector import Error
import mysql.connector
import numpy as np
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
root = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\pengujian"
Tahun = "2020"
Month = "2020-07-bogor"
Wilayah = "Bogor"
Kecamatan = "kec_Babakan_Madang"
B2_Filename = root+"\\"+Tahun+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF2_crop.tif"
B4_Filename = root+"\\"+Tahun+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF4_crop.tif"
B5_Filename = root+"\\"+Tahun+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF5_crop.tif"
B2_PATH = root+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF2_crop.tif"
B4_PATH = root+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF4_crop.tif"
B5_PATH = root+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF5_crop.tif"
count_num = 0
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    #Calculate NDVI, SAVI, EVI and save to database
    ndvi = ndvi_calc(B4_PATH, B5_PATH)
    savi = savi_calc(B4_PATH, B5_PATH)
    evi = evi_calc(B2_PATH, B4_PATH, B5_PATH)
    ndvi_image = im.fromarray(ndvi)
    ndvi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\pelatihan\\ndvi\\"+Tahun+"_"+Month+"_"+Wilayah+"_"+Kecamatan+".tif"
    ndvi_path = ndvi_image.save(ndvi_image_path, "TIFF")
    savi_image = im.fromarray(savi)
    savi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\pelatihan\\savi\\"+Tahun+"_"+Month+"_"+Wilayah+"_"+Kecamatan+".tif"
    savi_path = savi_image.save(savi_image_path, "TIFF")
    evi_image = im.fromarray(evi)
    evi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\pelatihan\\evi\\"+Tahun+"_"+Month+"_"+Wilayah+"_"+Kecamatan+".tif"
    evi_path = evi_image.save(evi_image_path, "TIFF")    
    sql = "INSERT INTO smt_7_skripsi.landsat_8_raw (FileName, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val = (B2_Filename+";"+B4_Filename+";"+B5_Filename, Wilayah, Kecamatan, Tahun, ndvi_image_path, savi_image_path, evi_image_path)
    cursor.execute(sql, val)
    conn.commit()
    count_num = count_num + 1
    print(count_num, "Record for landsat_8_raw inserted")
except Error as e:
  print("Failed inserting data into MySQL table {}".format(e))

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
    cursor.execute("SELECT a.Id, a.FileName, b.Id AS Id_wilayah, a.Wilayah, c.id AS Id_kecamatan, a.Kecamatan, a.Tahun, a.NDVI, a.SAVI, a.EVI, e.Id_label, e.Label FROM `landsat_8_raw` AS a LEFT JOIN `mapping_wilayah` AS b ON a.Wilayah = b.Wilayah LEFT JOIN `mapping_kecamatan` AS c ON a.Kecamatan = c.Kecamatan LEFT JOIN `labeling_y` AS e ON a.Wilayah = e.Wilayah AND a.Kecamatan = e.Kecamatan AND a.Tahun = e.Tahun ORDER BY 1")
    record = cursor.fetchall()
    for x in record:
      sql = "INSERT INTO smt_7_skripsi.landsat_8 (Id, Filename, Id_wilayah, Wilayah, Id_kecamatan, Kecamatan, Tahun, NDVI, SAVI, EVI, Id_label, Label) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
      cursor.execute(sql, x)
      conn.commit()
      count_num_3 = count_num_3 + 1
      print(count_num_3, "Record for landsat_8 inserted")
except Error as e:
  print("Error while connecting to MySQL", e)