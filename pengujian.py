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

def appendDictToDF(df,dictToAppend):
  df = pd.concat([df, pd.DataFrame.from_records([dictToAppend])])
  return df

def plot_confusion_matrix(cm,classes,normalize=False,title='Confusion Matrix',cmap=plt.cm.Blues):
  if normalize:
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print("Normalized confusion matrix")
  else:
    print('Confusion matrix, without normalization')
  print(cm)
  plt.figure(figsize=(10,7))
  plt.imshow(cm, interpolation='nearest', cmap=cmap)
  plt.title(title)
  plt.colorbar()
  tick_marks = np.arange(len(classes))
  plt.xticks(tick_marks, classes, rotation=0)
  plt.yticks(tick_marks, classes)
  fmt = '.2f' if normalize else 'd'
  thresh = cm.max() / 2.
  for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
    plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")
  plt.tight_layout()
  plt.ylabel('true_label')
  plt.xlabel('predict_label')
  
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