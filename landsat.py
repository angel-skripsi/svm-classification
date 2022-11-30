from PIL import Image as im
from sshtunnel import SSHTunnelForwarder
from mysql.connector import Error
import numpy as np
import pymysql
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
root_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\resources"
list_Image = []
count_num = 0
try:
  tunnel = SSHTunnelForwarder(("vicenza.id.domainesia.com", 64000), ssh_password="6yqW[d9bYR;S87", ssh_username="svmclass", remote_bind_address=("localhost", 3306)) 
  tunnel.start()
  conn = pymysql.connect(host="127.0.0.1", user="svmclass_root", passwd="angeljelek6gt!", db = "svmclass_classification", port=tunnel.local_bind_port)
  print("=======================================================================")
  cursor = conn.cursor()
  cursor.execute('DROP TABLE IF EXISTS landsat_8_all_pelatihan;')
  print('Creating table landsat_8_all_pelatihan')
  cursor.execute("CREATE TABLE landsat_8_all_pelatihan (Id int(20) NOT NULL auto_increment, FileName text, Wilayah varchar(255), Kecamatan varchar(255), Tahun int(4), NDVI varchar(255), SAVI varchar(255), EVI varchar(255), Id_label int(20), Label varchar(255), PRIMARY KEY(Id))")
  cursor.execute("SET @@auto_increment_increment=1;")
  print("Table landsat_8_all_pelatihan is created")
  for year in os.listdir(root_path):
    for month in os.listdir(root_path+"/"+year):
      bulan = month.split("-")[1]
      for wilayah in os.listdir(root_path+"/"+year+"/"+month):
        for kecamatan in os.listdir(root_path+"/"+year+"/"+month+"/"+wilayah):
          B4_PATH = "" 
          B5_PATH = "" 
          B2_PATH = ""
          for filename in glob.iglob(root_path+"/"+year+"/"+month+"/"+wilayah+"/"+kecamatan + "/" + '*.tif', recursive=True):
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
          ndvi = np.uint8(ndvi*255)
          savi = np.uint8(savi*255)
          evi = np.uint8(evi*255)
          ndvi_image = im.fromarray(ndvi)
          ndvi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\output\\calculation\\pelatihan\\ndvi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
          ndvi_path = ndvi_image.save(ndvi_image_path, "TIFF")
          ndvi_image_path_save = "output/calculation/pelatihan/ndvi/"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
          savi_image = im.fromarray(savi)
          savi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\output\\calculation\\pelatihan\\savi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
          savi_path = savi_image.save(savi_image_path, "TIFF")
          savi_image_path_save = "output/calculation/pelatihan/savi/"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
          evi_image = im.fromarray(evi)
          evi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\output\\calculation\\pelatihan\\evi\\"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
          evi_path = evi_image.save(evi_image_path, "TIFF")
          evi_image_path_save = "output/calculation/pelatihan/evi/"+year+"_"+month+"_"+wilayah+"_"+kecamatan+".tif"
          sql = "INSERT INTO svmclass_classification.landsat_8_all_pelatihan (FileName, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI) VALUES (%s,%s,%s,%s,%s,%s,%s)"
          val = (B2_PATH+";"+B4_PATH+";"+B5_PATH, wilayah, kecamatan, year, ndvi_image_path_save, savi_image_path_save, evi_image_path_save)
          cursor.execute(sql, val)
          conn.commit()
          count_num = count_num + 1
          print(count_num, "Record for landsat_8_all_pelatihan inserted")
except Error as e:
  print("Failed inserting data into MySQL table {}".format(e))

#Select all data from landsat_8_all_pelatihan and mapping it to Label and save it to database
count_num_3 = 0
try:
  tunnel = SSHTunnelForwarder(("vicenza.id.domainesia.com", 64000), ssh_password="6yqW[d9bYR;S87", ssh_username="svmclass", remote_bind_address=("localhost", 3306)) 
  tunnel.start()
  conn = pymysql.connect(host="127.0.0.1", user="svmclass_root", passwd="angeljelek6gt!", db = "svmclass_classification", port=tunnel.local_bind_port)
  print("=======================================================================")
  cursor = conn.cursor()
  cursor.execute("UPDATE svmclass_classification.landsat_8_all_pelatihan SET Id_Label = (SELECT Id_label FROM labeling_y WHERE landsat_8_all_pelatihan.Wilayah = labeling_y.Wilayah AND landsat_8_all_pelatihan.Kecamatan = labeling_y.Kecamatan AND landsat_8_all_pelatihan.Tahun = labeling_y.Tahun), Label = (SELECT Label FROM labeling_y WHERE landsat_8_all_pelatihan.Wilayah = labeling_y.Wilayah AND landsat_8_all_pelatihan.Kecamatan = labeling_y.Kecamatan AND landsat_8_all_pelatihan.Tahun = labeling_y.Tahun) WHERE Id > 0")
  conn.commit()
  print("Record for landsat_8_all_pelatihan updated")
except Error as e:
  print("Error while connecting to MySQL", e)