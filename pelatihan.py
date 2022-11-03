from PIL import Image as im
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from statistics import mean
# from io import BytesIO
from mysql.connector import Error
import mysql.connector
import pandas as pd
import seaborn as sns
import base64
import warnings
# import joblib
import numpy as np

def appendDictToDF(df,dictToAppend):
  df = pd.concat([df, pd.DataFrame.from_records([dictToAppend])])
  return df

#Select all data from landsat_8 and do training process and generate model
data_citra = []
data_training = pd.DataFrame(columns=['NDVI','SAVI','EVI','Id_label'])
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT NDVI, SAVI, EVI, Id_label FROM `landsat_8` LIMIT 1")
    record = cursor.fetchall()
    for x in record:
      data_citra.append(x)
    for i in range(len(data_citra)):
      print ("Read training data" ,i+1)
      NDVI = data_citra[i][0]
      with open(NDVI, "rb") as image_file:
        x = im.open(image_file)
        w, h = x.size
        print('width: ', w/2)
        print('height:', h/2)
        # b5_image_64_encode = base64.b64encode(image_file.read())
      # # im = im.open(BytesIO(base64.b64decode(b5_image_64_encode)))
      # # im.save('image1.tif', 'TIFF')
      # SAVI = data_citra[i][1]
      # with open(SAVI, "rb") as image_file2:
      #   b4_image_64_encode = base64.b64encode(image_file2.read())
      # EVI = data_citra[i][2]
      # with open(EVI, "rb") as image_file3:
      #   b2_image_64_encode = base64.b64encode(image_file3.read())
      # b5_image_64_decode = base64.b64decode(b5_image_64_encode)
      # b5_image = "".join(["{:08b}".format(x) for x in b5_image_64_decode])
      # b4_image_64_decode = base64.b64decode(b4_image_64_encode)
      # b4_image = "".join(["{:08b}".format(x) for x in b4_image_64_decode])
      # b2_image_64_decode = base64.b64decode(b2_image_64_encode)
      # b2_image = "".join(["{:08b}".format(x) for x in b2_image_64_decode])
      # print(b2_image)
      # data_training = appendDictToDF(data_training,{'NDVI':b5_image,'SAVI':b4_image,'EVI':b2_image,'Id_label':data_citra[i][3]})
    # print(data_training)
    # print("Data training size:" + str(data_training.shape))  
    # #Create data training diagram
    # colours = ["green", "orange", "yellow"]
    # plot_data_train = sns.countplot(x='Id_label', data=data_training, palette=colours)
    # plot_data_train.bar_label(plot_data_train.containers[0])
    # plot_data_train.set(xlabel='label_tanah', ylabel='data_count', title='Plot Data Pelatihan')
    # figure_data_train = plot_data_train.get_figure()
    # figure_data_train.savefig("output/plot_pelatihan/plot_data_pelatihan.png")
    # #Split training and testing data
    # data_training = data_training.infer_objects()
    # X = data_training.drop({"Id_label"}, axis=1)
    # y = data_training["Id_label"]
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 104)
    # print('X_train:', X_train.shape)
    # print('X_test:', X_test.shape)
    # print('y_train:', y_train.shape)
    # print('y_test:', y_test.shape)
    # #Training kernel SVM model
    # # classifier = SVC(kernel = 'rbf', C=1, gamma ='auto', tol=0.001, decision_function_shape='ovo').fit(X_train, y_train)
    # classifier = SVC(kernel='linear').fit(X_train, y_train)
    # # classifier = SVC(kernel = 'poly', degree=5, C=3).fit(X_train, y_train) 
    # #Predicting the testing data
    # y_predict = classifier.predict(X_test)
    # print("=======================================================================")
    # print('y_predict:', y_predict)
    # #Evaluating model performance
    # con_matrx = confusion_matrix(y_test, y_predict)
    # print('confusion_matrix:', con_matrx)
    # accuracy = accuracy_score(y_test, y_predict) 
    # accuracy = accuracy * 100
    # print('accuracy:', round(accuracy,2), '%')
    # classification = classification_report(y_test,y_predict)
    # print('classification:', classification)
    # #Save model
    # print("=======================================================================")
    # joblib.dump(classifier, "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\svm\\svm_model.pkl")
    # print("Model saved")
except Error as e:
  print("Error while connecting to MySQL", e)

# #Select all data from landsat_8 and do training process and generate model
# data_citra = []
# data_training = pd.DataFrame(columns=['NDVI','SAVI','EVI','Id_label','Label'])
# warnings.filterwarnings('ignore')
# try:
#   conn = mysql.connector.connect(host="us-cdbr-east-06.cleardb.net", user="b539dadf046091", password="5b842ab0", database="heroku_97dccdc5801db01", port = "3306")
#   if conn.is_connected():
#     print("=======================================================================")
#     cursor = conn.cursor()
#     cursor.execute("SELECT NDVI, SAVI, EVI, Id_label, Label FROM `landsat_8` LIMIT 10")
#     record = cursor.fetchall()
#     for x in record:
#       data_citra.append(x)
#     for i in range(len(data_citra)):
#       print ("Read training data" ,i+1)
#       NDVI = data_citra[i][0]
#       with open(NDVI, "rb") as image_file:
#         b5_image_64_encode = base64.b64encode(image_file.read())
#       # im = im.open(BytesIO(base64.b64decode(b5_image_64_encode)))
#       # im.save('image1.tif', 'TIFF')
#       SAVI = data_citra[i][1]
#       with open(SAVI, "rb") as image_file2:
#         b4_image_64_encode = base64.b64encode(image_file2.read())
#       EVI = data_citra[i][2]
#       with open(EVI, "rb") as image_file3:
#         b2_image_64_encode = base64.b64encode(image_file3.read())
#       b5_image_64_decode = base64.b64decode(b5_image_64_encode)
#       b5_image = "".join(["{:08b}".format(x) for x in b5_image_64_decode])
#       b4_image_64_decode = base64.b64decode(b4_image_64_encode)
#       b4_image = "".join(["{:08b}".format(x) for x in b4_image_64_decode])
#       b2_image_64_decode = base64.b64decode(b2_image_64_encode)
#       b2_image = "".join(["{:08b}".format(x) for x in b2_image_64_decode])
#       data_training = appendDictToDF(data_training,{'NDVI':b5_image,'SAVI':b4_image,'EVI':b2_image,'Id_label':data_citra[i][3],'Label':data_citra[i][4]})
#     print("Data training size:" + str(data_training.shape))  
#     #Create data training diagram
#     colours = ["green", "orange", "yellow"]
#     plot_data_train = sns.countplot(x='Label', data=data_training, palette=colours)
#     plot_data_train.bar_label(plot_data_train.containers[0])
#     plot_data_train.set(xlabel='label_tanah', ylabel='data_count', title='Plot Data Pelatihan')
#     figure_data_train = plot_data_train.get_figure()
#     figure_data_train.savefig("output/plot_pelatihan/plot_data_pelatihan.png")
#     #Split training and testing data
#     data_training = data_training.infer_objects()
#     X = data_training.drop({"Id_label", "Label"}, axis=1)
#     y = data_training["Id_label"]
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 104)
#     print('X_train:', X_train.shape)
#     print('X_test:', X_test.shape)
#     print('y_train:', y_train.shape)
#     print('y_test:', y_test.shape)
#     #Training kernel SVM model
#     # classifier = SVC(kernel = 'rbf', C=1, gamma ='auto', tol=0.001, decision_function_shape='ovo').fit(X_train, y_train)
#     classifier = SVC(kernel='linear', C=1, gamma ='auto', tol=0.001, decision_function_shape='ovo').fit(X_train, y_train)
#     # classifier = SVC(kernel = 'poly', degree=5, C=3).fit(X_train, y_train) 
#     #Predicting the testing data
#     y_predict = classifier.predict(X_test)
#     print("=======================================================================")
#     print('y_predict:', y_predict)
#     #Evaluating model performance
#     con_matrx = confusion_matrix(y_test, y_predict)
#     print('confusion_matrix:', con_matrx)
#     accuracy = accuracy_score(y_test, y_predict) 
#     accuracy = accuracy * 100
#     print('accuracy:', round(accuracy,2), '%')
#     classification = classification_report(y_test,y_predict)
#     print('classification:', classification)
#     # #Save model
#     # print("=======================================================================")
#     # joblib.dump(classifier, "C:\\Users\\Angellina\\Dropbox\\My PC (LAPTOP-9GTQMRFV)\\Desktop\\svm\\svm_model.pkl")
#     # print("Model saved")
# except Error as e:
#   print("Error while connecting to MySQL", e)