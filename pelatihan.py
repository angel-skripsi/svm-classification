from skimage.io import imread
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from mysql.connector import Error
import mysql.connector
import seaborn as sns
import numpy as np
import pandas as pd
import joblib
import warnings

def appendDictToDF(df,dictToAppend):
  df = pd.concat([df, pd.DataFrame.from_records([dictToAppend])])
  return df

#Select all data from landsat_8 and create plot for training data
data_citra = []
data_training = pd.DataFrame(columns=['NDVI','SAVI','EVI','Label'])
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT NDVI, SAVI, EVI, Label FROM `landsat_8`")
    record = cursor.fetchall()
    for x in record:
      data_citra.append(x)
    for i in range(len(data_citra)):
      print ("Read training data" ,i+1)
      NDVI = data_citra[i][0]
      SAVI = data_citra[i][1]
      EVI = data_citra[i][2]
      data_training = appendDictToDF(data_training,{'NDVI':NDVI,'SAVI':SAVI,'EVI':EVI,'Label':data_citra[i][3]})
    print("Data training size:" + str(data_training.shape))  
    #Create data training diagram
    colours = ["green", "orange", "yellow"]
    plot_data_train = sns.countplot(x='Label', data=data_training, palette=colours)
    plot_data_train.bar_label(plot_data_train.containers[0])
    plot_data_train.set(xlabel='label_tanah', ylabel='data_count', title='Plot Data Pelatihan')
    figure_data_train = plot_data_train.get_figure()
    figure_data_train.savefig("output/plot_pelatihan/plot_data_pelatihan.png")
    print("Plot data training is created")
except Error as e:
  print("Error while connecting to MySQL", e)

#Select all data from landsat_8 and do training process and generate model
flat_data_arr = []
target_arr = []
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT NDVI AS data_input, Id_label FROM landsat_8 UNION ALL SELECT SAVI AS data_input, Id_label FROM landsat_8 UNION ALL SELECT EVI AS data_input, Id_label FROM landsat_8;")
    record = cursor.fetchall()
    for x in record:
      data_input = x[0]
      label = x[1]
      img_array = imread(data_input)
      img_resized = resize(img_array, (100,100))
      flat_data_arr.append(img_resized.flatten())
      target_arr.append(label)
    flat_data = np.array(flat_data_arr)
    target = np.array(target_arr)
    df = pd.DataFrame(flat_data)
    df['Target'] = target
    #Split training and testing data
    X = df.iloc[:,:-1]
    y = df.iloc[:,-1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 104)
    print('X_train:', X_train.shape)
    print('X_test:', X_test.shape)
    print('y_train:', y_train.shape)
    print('y_test:', y_test.shape)
    #Training kernel SVM model
    classifier = SVC(kernel='linear').fit(X_train, y_train)
    # classifier = SVC(kernel = 'poly').fit(X_train, y_train) 
    #Predicting the testing data
    y_predict = classifier.predict(X_test)
    print("=======================================================================")
    print('y_predict:', y_predict)
    #Evaluating model performance
    con_matrx = confusion_matrix(y_test, y_predict)
    print('confusion_matrix:', con_matrx)
    accuracy = accuracy_score(y_test, y_predict) 
    accuracy = accuracy * 100
    print('accuracy:', round(accuracy,2), '%')
    classification = classification_report(y_test,y_predict)
    print('classification:', classification)
    #Save model
    print("=======================================================================")
    joblib.dump(classifier, "output/data_model/svm_data_model.pkl")
    print("Model saved")
except Error as e:
  print("Error while connecting to MySQL", e)