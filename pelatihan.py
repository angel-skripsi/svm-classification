from skimage.io import imread
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from mysql.connector import Error
from sshtunnel import SSHTunnelForwarder
import pymysql
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib
import warnings
import itertools
import os
import base64

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

#Select all data from landsat_8_pelatihan and do training process and generate model
root_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\calculation"
data_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\"
ndvi_flat_data_arr = []
savi_flat_data_arr = []
evi_flat_data_arr = []
target_arr = []
warnings.filterwarnings('ignore')
try:
  tunnel = SSHTunnelForwarder(("vicenza.id.domainesia.com", 64000), ssh_password="6yqW[d9bYR;S87", ssh_username="svmclass", remote_bind_address=("localhost", 3306)) 
  tunnel.start()
  conn = pymysql.connect(host="127.0.0.1", user="svmclass_root", passwd="angeljelek6gt!", db = "svmclass_classification", port=tunnel.local_bind_port)
  print("=======================================================================")
  cursor = conn.cursor()
  cursor.execute("SELECT NDVI, SAVI, EVI, Id_label FROM landsat_8_all_pelatihan WHERE (Kecamatan = 'kec_Jasinga' OR Kecamatan = 'kec_Parung' OR Kecamatan = 'kec_Caringin') AND Tahun = '2016' AND Filename LIKE ('%09%') AND Filename NOT LIKE ('%(2)%');")
  # cursor.execute("SELECT NDVI, SAVI, EVI, Id_label FROM landsat_8_all_pelatihan;")
  record = cursor.fetchall() 
  for x in record:
    ndvi_data_input = x[0]
    ndvi_data_input = ndvi_data_input.replace('/', '\\')
    ndvi_data_input = data_path+ndvi_data_input
    ndvi_img_array = imread(ndvi_data_input)
    ndvi_img_resized = resize(ndvi_img_array, (100,100))
    ndvi_img_flatten = ndvi_img_resized.flatten()
    ndvi_img_tolist = ndvi_img_flatten.tolist()
    ndvi_flat_data_arr.extend(ndvi_img_tolist)
    savi_data_input = x[1]
    savi_data_input = savi_data_input.replace('/', '\\')
    savi_data_input = data_path+savi_data_input
    savi_img_array = imread(savi_data_input)
    savi_img_resized = resize(savi_img_array, (100,100))
    savi_img_flatten = savi_img_resized.flatten()
    savi_img_tolist = savi_img_flatten.tolist()
    savi_flat_data_arr.extend(savi_img_tolist)
    evi_data_input = x[2]
    evi_data_input = evi_data_input.replace('/', '\\')
    evi_data_input = data_path+evi_data_input
    evi_img_array = imread(evi_data_input)
    evi_img_resized = resize(evi_img_array, (100,100))
    evi_img_flatten = evi_img_resized.flatten()
    evi_img_tolist = evi_img_flatten.tolist()
    evi_flat_data_arr.extend(evi_img_tolist)
    label = x[3]
    for i in range(10000):
      target_arr.append(label)
  ndvi_flat_data = np.array(ndvi_flat_data_arr)
  savi_flat_data = np.array(savi_flat_data_arr)
  evi_flat_data = np.array(evi_flat_data_arr)
  target = np.array(target_arr)
  df = pd.DataFrame(ndvi_flat_data)
  df['SAVI'] = savi_flat_data
  df['EVI'] = evi_flat_data
  df['target'] = target
  df.columns =['NDVI', 'SAVI', 'EVI', 'Label']
  #Split training and testing data
  X = df.iloc[:,:-1]
  y = df.iloc[:,-1]
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 104)
  print('X_train:', X_train.shape)
  print('X_test:', X_test.shape)
  print('y_train:', y_train.shape)
  print('y_test:', y_test.shape)
  #Training kernel SVM model
  cursor.execute("SELECT Svm_type FROM svm_kernel;")
  svm_record = cursor.fetchall()
  for y in svm_record:
    svm_type = y[0]
  svm_name = svm_type
  classifier = SVC(kernel=svm_name).fit(X_train, y_train)
  #Predicting the testing data
  y_predict = classifier.predict(X_test)
  print('y_predict:', y_predict)
  #Evaluating model performance
  con_matrx = confusion_matrix(y_test, y_predict)
  np.set_printoptions(precision=2)
  print('confusion_matrix:', con_matrx)
  # # Plot confusion matrix without normalization
  # plt.figure()
  # confusion_matrix_1 = plot_confusion_matrix(con_matrx, classes=["Hijau","Kering","Setengah Hijau"])
  # plt.savefig('C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\svm-classification\\output\\confusion_matrix\\confusion_matrix_without_normalization.png')
  # Plot confusion matrix with normalization
  plt.figure()
  confusion_matrix_2 = plot_confusion_matrix(con_matrx, classes=["Hijau","Kering","Setengah Hijau"], normalize=True)
  plt.savefig('C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\svm-classification\\output\\confusion_matrix\\confusion_matrix_with_normalization.png')
  accuracy = accuracy_score(y_test, y_predict) 
  accuracy = accuracy * 100
  print('accuracy:', round(accuracy,2), '%')
  classification = classification_report(y_test,y_predict,output_dict=True)
  prec_1 = str("%.4f" % (classification['1']['precision']))
  rec_1 = str("%.4f" % (classification['1']['recall']))
  score_1 = str("%.2f" % (classification['1']['f1-score']*100))
  prec_2 = str("%.4f" % (classification['2']['precision']))
  rec_2 = str("%.4f" % (classification['2']['recall']))
  score_2 = str("%.2f" % (classification['2']['f1-score']*100))
  prec_3 = str("%.4f" % (classification['3']['precision']))
  rec_3 = str("%.4f" % (classification['3']['recall']))
  score_3 = str("%.2f" % (classification['3']['f1-score']*100))
  prec_4 = str("%.4f" % (classification['macro avg']['precision']))
  rec_4 = str("%.4f" % (classification['macro avg']['recall']))
  score_4 = str("%.2f" % (classification['macro avg']['f1-score']*100))
  print('classification:', classification)
  print("=======================================================================")
  sql = "INSERT INTO svmclass_classification.evaluation (Svm_type, Hijau_precision, Hijau_recall, Hijau_f1_score, Kering_precision, Kering_recall, Kering_f1_score, Setengah_hijau_precision, Setengah_hijau_recall, Setengah_hijau_f1_score, macro_avg_precision, macro_avg_recall, macro_avg_f1_score, accuracy) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
  x = svm_name, prec_1, rec_1, score_1, prec_2, rec_2, score_2, prec_3, rec_3, score_3, prec_4, rec_4, score_4, round(accuracy,2)
  cursor.execute(sql, x)
  conn.commit()
  print("Record for evaluation inserted")
  #Save model
  print("=======================================================================")
  joblib.dump(classifier, "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\dataset\\output\\data_model\\svm_data_model.pkl")
  print("Model saved")
except Error as e:
  print("Error while connecting to MySQL", e)

#Select plot data training from local repository and save base64 value to database
count_num_2 = 0
root_path = "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\ALL SKRIPSI\\GITHUB\\svm-classification\\output\\confusion_matrix"
try:
  tunnel = SSHTunnelForwarder(("vicenza.id.domainesia.com", 64000), ssh_password="6yqW[d9bYR;S87", ssh_username="svmclass", remote_bind_address=("localhost", 3306)) 
  tunnel.start()
  conn = pymysql.connect(host="127.0.0.1", user="svmclass_root", passwd="angeljelek6gt!", db = "svmclass_classification", port=tunnel.local_bind_port)
  print("=======================================================================")
  cursor = conn.cursor()
  cursor.execute('DELETE FROM svmclass_classification.image_encode WHERE entity_name = "confusion_matrix";')
  for row in os.listdir(root_path):
    with open(root_path+"/"+row, "rb") as image_file:
      cm_encode = base64.b64encode(image_file.read())
    sql = "INSERT INTO svmclass_classification.image_encode (entity_name, encode_value) VALUES (%s, %s)"
    val = ("confusion_matrix", cm_encode)
    cursor.execute(sql, val)
    conn.commit()
    count_num_2 = count_num_2 + 1
    print(count_num_2, "Record for image_encode inserted")
except Error as e:
  print("Error while connecting to MySQL", e)