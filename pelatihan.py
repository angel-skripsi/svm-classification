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

#Select all data from landsat_8_pelatihan and create plot for training data
data_citra = []
data_training = pd.DataFrame(columns=['NDVI','SAVI','EVI','Label'])
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT NDVI, SAVI, EVI, Label FROM `landsat_8_pelatihan`")
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

#Select all data from landsat_8_pelatihan and do training process and generate model
flat_data_arr = []
target_arr = []
warnings.filterwarnings('ignore')
try:
  conn = mysql.connector.connect(host="localhost", user="root", password="", database="smt_7_skripsi", port = "3310")
  if conn.is_connected():
    print("=======================================================================")
    cursor = conn.cursor()
    cursor.execute("SELECT NDVI AS data_input, Id_label FROM landsat_8_pelatihan UNION ALL SELECT SAVI AS data_input, Id_label FROM landsat_8_pelatihan UNION ALL SELECT EVI AS data_input, Id_label FROM landsat_8_pelatihan;")
    record = cursor.fetchall()
    record_count = int(len(record)/3)
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
    svm_name = 'linear'
    classifier = SVC(kernel=svm_name).fit(X_train, y_train)
    #Predicting the testing data
    y_predict = classifier.predict(X_test)
    print('y_predict:', y_predict)
    #Evaluating model performance
    con_matrx = confusion_matrix(y_test, y_predict)
    np.set_printoptions(precision=2)
    print('confusion_matrix:', con_matrx)
    # Plot confusion matrix without normalization
    plt.figure()
    confusion_matrix_1 = plot_confusion_matrix(con_matrx, classes=["Hijau","Kering","Setengah Hijau"])
    plt.savefig('output/confusion_matrix/confusion_matrix_without_normalization.png')
    # Plot confusion matrix with normalization
    plt.figure()
    confusion_matrix_2 = plot_confusion_matrix(con_matrx, classes=["Hijau","Kering","Setengah Hijau"], normalize=True)
    plt.savefig('output/confusion_matrix/confusion_matrix_with_normalization.png')
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
    sql = "INSERT INTO smt_7_skripsi.evaluation (Svm_type, Data_count, Hijau_precision, Hijau_recall, Hijau_f1_score, Kering_precision, Kering_recall, Kering_f1_score, Setengah_hijau_precision, Setengah_hijau_recall, Setengah_hijau_f1_score, macro_avg_precision, macro_avg_recall, macro_avg_f1_score) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    x = svm_name, record_count, prec_1, rec_1, score_1, prec_2, rec_2, score_2, prec_3, rec_3, score_3, prec_4, rec_4, score_4
    cursor.execute(sql, x)
    conn.commit()
    print("Record for evaluation inserted")
    #Save model
    print("=======================================================================")
    joblib.dump(classifier, "output/data_model/svm_data_model.pkl")
    print("Model saved")
except Error as e:
  print("Error while connecting to MySQL", e)