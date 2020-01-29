# -*- coding: utf-8 -*-
"""flask_app.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qPGW6LfSGV3tPop23IrqnvM9VgqRGKOj
"""

#from google.colab import drive
#drive.mount('/content/drive')

#!pip install flask-ngrok

#web app libraries
from flask import Flask,request,render_template,flash,url_for,redirect
#from flask_ngrok import run_with_ngrok

#OS and Measure Time
import os
from time import perf_counter

#preprocessing libraries
from tensorflow.keras.preprocessing.image import load_img,img_to_array,array_to_img,save_img
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# Model Loading Library
from tensorflow.keras.models import load_model,model_from_json

#path=os.getcwd()
#print(path)

"""#Delete Uploaded Images from server"""

def delete_img_folder():
  path_to_static=os.path.join(os.getcwd(),'static')
  if 'images'not in os.listdir(path_to_static):
    return None
  path_to_img_folder=os.path.join(os.getcwd(),'static','images')
  print(path_to_img_folder)
  imgs=os.listdir(path_to_img_folder)
  for i in imgs:
    rpath=os.path.join(path_to_img_folder,i)
    print(rpath)
    os.remove(rpath)
  os.rmdir(path_to_img_folder)
  print("\n\nImage dir deleted\n\n")

"""#Create Image Folder to store uploaded image"""

def make_img_folder():
  path_change=os.path.join(os.getcwd(),'static','images')
  #print(path_change)
  if not os.path.isdir(path_change):        
    os.mkdir(path_change)
    print(f'\n\n{path_change} dir created\n\n')
    return path_change

"""#Load Model"""

def load_PMD_model():
  #H5
  """
  path_to_model=os.path.join(os.getcwd(),'final_model_v1.h5')
  model=load_model(path_to_model)
  """
  #JSON
  # load json and create model
  model_dir=os.path.join(os.getcwd(),"Final_model_v1.json")
  json_file = open(model_dir, 'r')
  loaded_model_json = json_file.read()
  json_file.close()
  loaded_model = model_from_json(loaded_model_json)
  # load weights into new model
  loaded_model.load_weights(os.path.join(os.getcwd(),"weights_for_jsonModel.h5"))
  loaded_model.compile(loss="categorical_crossentropy",metrics=['accuracy'],optimizer="adam")
  #model.summary()
  return loaded_model

"""#Get the Processed Image"""

def get_image(imageName):
  path_to_img=os.path.join(os.getcwd(),f'static/images/{imageName}')
  img=load_img(path_to_img)
  #display(img)
  img_arr=np.resize(img_to_array(img),[128,128,3])
  img_arr=img_arr.reshape(1,128,128,3).astype("Int32")
  return img_arr

"""#Decoder Function"""

def pmdDecoder(class_names):
  LE=LabelEncoder()
  #label encoding
  L_encd=LE.fit_transform(class_names)
  #print(L_encd)
  no_of_cls=len(L_encd)
  #onehot encoding on label encoded 
  ohEnc=to_categorical(L_encd,no_of_cls)
  pmdEnc={}
  for i,j in zip(class_names,ohEnc):
    pmdEnc[str(j)]=i
  print(pmdEnc)
  return pmdEnc

"""#Prediction Making Function"""

def predict_the_class(model,image):
  class_names=class_names=['forest','snow_covered_land','grass_land','buildings','water','barren_land']
  predicted_result_encoded=model.predict_proba(image)
  predicted_result=[int(i) for i in predicted_result_encoded[0]]
  pred_np_arr=np.array(predicted_result,dtype="float32")
  decoder=pmdDecoder(class_names)
  return decoder[str(pred_np_arr)]

"""#The PMD Flask App"""

#!cp /content/drive/My\ Drive/GUI_Test/PMD_GUI_2020/final_model_v1.h5 -r /content/
#!cp /content/drive/My\ Drive/PMD_Models/Final_model_v1.json -r /content/
#!cp /content/drive/My\ Drive/PMD_Models/weights_for_jsonModel.h5 -r /content/
#!cp /content/drive/My\ Drive/GUI_Test/PMD_GUI_2020/static -r /content/
#!cp /content/drive/My\ Drive/GUI_Test/PMD_GUI_2020/templates -r /content/

app=Flask(__name__)
#run_with_ngrok(app)
FileName="none.png"
app.config['SECRET_KEY']="LoL 13 NoOne Can Guess This Key XD"
#app.config['DEBUG']=True
delete_img_folder()
app.config['IMAGE_UPLOAD']=make_img_folder()#os.path.join(os.getcwd(),'static','images')

@app.route('/')
def home_page():
  #path_to_images=make_img_folder()
  #delete_img_folder()
  return render_template('index.html',val=False,msg="Upload an Image")

@app.route('/upload',methods=["POST","GET"])
def upload_img():
  #delete_img_folder()
  if request.method=="POST":
    #app.config['IMAGE_UPLOAD']=make_img_folder()#os.path.join(os.getcwd(),'static','images')
    k=False
    if request.files and request.files['myImage'].filename != '' :
      filename=request.files['myImage']
      print(filename)
      filename.save(os.path.join(app.config['IMAGE_UPLOAD'],filename.filename))
      k=True
      global FileName
      FileName=filename.filename
      path='../static/images'
      path=os.path.join(path,FileName)
      print(f"\npath of the image  to show: {path}")
      print("\nIn uploading route\n")
      #path="../static/uploaded_images/"
      return render_template("img.html",fileName=path)
      #return render_template("index.html",val=k,msg="Plz Upload Again",sz=fSize(pathJoin(app.config['IMAGE_UPLOAD'],filename.filename))//(1024*1024))
    else:
      k=False
      return render_template("index.html",val=k,msg="Plz Upload Again" )
      #return render_template("img.html",fileName=path)
  else:
    return render_template('index.html',msg="Upload The Image")

@app.route('/predict')
def predict_my_image():
  global FileName
  print("\nIn Predicting route\n\n")
  #image_name=os.listdir(app.config['IMAGE_UPLOAD'])        #This is a change
  print(f"\nuploaded image name {FileName}\n")
  #path_to_img=os.path.join(app.config['IMAGE_UPLOAD'],image_name)
  ans=predict_the_class(load_PMD_model(),get_image(FileName))  #this is a change
  #delete_img_folder()       #New change
  return render_template('result.html',Ans=ans)

if __name__=="__main__":
  app.run()

