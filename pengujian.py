from PIL import Image as im
from skimage.io import imread
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from mysql.connector import Error
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import joblib
import warnings
import itertools
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
B2_PATH = root+"\\"+Tahun+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF2_crop.tif"
B4_PATH = root+"\\"+Tahun+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF4_crop.tif"
B5_PATH = root+"\\"+Tahun+"\\"+Month+"\\"+Wilayah+"\\"+Kecamatan+"\\"+"TIF5_crop.tif"
count_num = 0
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    ndvi = ndvi_calc(B4_PATH, B5_PATH)
    savi = savi_calc(B4_PATH, B5_PATH)
    evi = evi_calc(B2_PATH, B4_PATH, B5_PATH)
    ndvi_image = im.fromarray(ndvi)
    ndvi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\pengujian\\ndvi\\"+Tahun+"_"+Month+"_"+Wilayah+"_"+Kecamatan+".tif"
    ndvi_path = ndvi_image.save(ndvi_image_path, "TIFF")
    savi_image = im.fromarray(savi)
    savi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\pengujian\\savi\\"+Tahun+"_"+Month+"_"+Wilayah+"_"+Kecamatan+".tif"
    savi_path = savi_image.save(savi_image_path, "TIFF")
    evi_image = im.fromarray(evi)
    evi_image_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\calculation\\pengujian\\evi\\"+Tahun+"_"+Month+"_"+Wilayah+"_"+Kecamatan+".tif"
    evi_path = evi_image.save(evi_image_path, "TIFF")
    sql = "INSERT INTO smt_7_skripsi.landsat_8_pengujian (FileName, Wilayah, Kecamatan, Tahun, NDVI, SAVI, EVI) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    val = (B2_PATH+";"+B4_PATH+";"+B5_PATH, Wilayah, Kecamatan, Tahun, ndvi_image_path, savi_image_path, evi_image_path)
    cursor.execute(sql, val)
    conn.commit()
    count_num = count_num + 1
    print(count_num, "Record for landsat_8_pengujian inserted")
except Error as e:
  print("Failed inserting data into MySQL table {}".format(e))
  
#Select all data from landsat_8_pelatihan and do training process and generate model
flat_data_arr = []
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT NDVI AS data_input FROM landsat_8_pelatihan WHERE Id = (SELECT MAX(Id) FROM landsat_8_pengujian) UNION ALL SELECT SAVI AS data_input FROM landsat_8_pelatihan WHERE Id = (SELECT MAX(Id) FROM landsat_8_pengujian) UNION ALL SELECT EVI AS data_input FROM landsat_8_pengujian WHERE Id = (SELECT MAX(Id) FROM landsat_8_pengujian);")
    record = cursor.fetchall()
    for x in record:
      data_input = x[0]
      img_array = imread(data_input)
      img_resized = resize(img_array, (100,100))
      flat_data_arr.append(img_resized.flatten())
    flat_data = np.array(flat_data_arr)
    df = pd.DataFrame(flat_data)
    print("Data testing size:" + str(df.shape))  
    svm_model = joblib.load("output/data_model/svm_data_model.pkl")
    y_test = svm_model.predict(df)
    print(y_test)
except Error as e:
  print("Error while connecting to MySQL", e)