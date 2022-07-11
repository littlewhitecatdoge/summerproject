import json
import pymysql
from flask import Flask,request,render_template
import cv2
import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing import image
from flask_cors import *
#from flask_apscheduler import APScheduler
import os
import time
from tensorflow.keras import backend as K
from matplotlib import pyplot as plt


app = Flask(__name__)


CORS(app, resources=r'/*')
header={
   'Access-Control-Allow-Origin':'http://127.0.0.1:3000',
   'Access-Control-Allow-Methods':'GET, POST, PATCH, PUT, DELETE, OPTIONS',
   'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'
}





IMAGE_SIZE = (128,128)

db="a"#pymysql.connect(host='localhost',user='root',password='12345678',database='spirit',cursorclass=pymysql.cursors.DictCursor)

LOG_PATH = os.path.dirname(os.path.abspath(__file__))

pictures_path=LOG_PATH+'/static/masks'

model_path=LOG_PATH+'/unet-seg-03.h5'

Host_URL='http://127.0.0.1:5000/static'


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')


################  ################  upload part  ################ #############


@app.route('/uploadphoto',methods=['POST'])
def upload_photo():
   log_text=''
   username=request.form.get("userName")
   try:
      PCID=request.form.get("PCID")
      #
      #print(PCID)
      res = request.files.to_dict()
      #print(res)
      #PNAME=res["PNAME"]
      image1 = cv2.imdecode(np.asarray(bytearray(res['filename'].read()),dtype='uint8'), cv2.IMREAD_GRAYSCALE)
      log_text=log_text+log_content(username,"Pictures Received\n")
      #print("1,success")
      #print(image1.shape)
      image2 = cv2.resize(image1,IMAGE_SIZE)
      log_text=log_text+log_content(username,"Pictures Resized\n")
      #print("2,success")
      #print(image2.shape)
      pred=call_model(image2)

      prediction_image = pred.reshape(IMAGE_SIZE)
      file=pictures_path+'/'+PCID+'.png'
      #print(file)
      plt.imsave(file, prediction_image, cmap='gray')
      test_img = cv2.imread(file, cv2.IMREAD_COLOR)
      #print(test_img)
      #encoding = mask_to_rle(pred, 128, 128)
      #print(encoding)
      if (test_img==0).all():
         result="No Pneumothorax"
      else:
         result="Pneumothorax"
      if query_patience(PCID)==None:
         insert_patience(PCID,result)
         log_text=log_text+log_content(username,"insert new patience\n") 
      else:
         update_patience(PCID,result)
         log_text=log_text+log_content(username,"update new patience\n")
      log_text=log_text+log_content(username,"Begin to use the model get result\n")
      write_log(log_text)
      return {"success":1}
   except:
      log_text=log_text+log_content(username,"upload failed\n")
      write_log(log_content(username,log_text))
      return {"success":0}
   

def dice_coef(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + K.epsilon()) / (K.sum(y_true_f) + K.sum(y_pred_f) + K.epsilon())

def dice_coef_loss(y_true, y_pred):
    return -dice_coef(y_true, y_pred)


def call_model(image1):
   model = keras.models.load_model(model_path,custom_objects={'dice_coef_loss': dice_coef_loss,'dice_coef':dice_coef})
   x = image.img_to_array(image1)
   #print("3,success")
   #print(x.shape)
   x = np.array([x])
   #print("4,success")
   #print(x.shape)
   #images=np.vstack(x])
   pred=model.predict(x.reshape(1,128,128,1))
   return pred
   #print(pred)
   
def insert_patience(Pcid,result):
   cursor = db.cursor()
   sql = "INSERT INTO patience (Pcid, Result) VALUES (%s,%s)"
   print(sql)
   result = cursor.execute(sql,(Pcid,result))
   if result:
      db.commit()
      cursor.close()
      #db.close()
      return True
   else:
      print("wrong in insert into Patience!")
      return result

def query_patience(Pcid):
   cursor = db.cursor()
   sql = "SELECT Result FROM patience WHERE Pcid=%s"
   result = cursor.execute(sql, (Pcid,))
   if result:
      result = cursor.fetchone()
      cursor.close()
      #db.close()
      return result
   else:
      print("wrong with the patience query")
      return None

def update_patience(PCID,newresult):
   cursor = db.cursor()
   sql = "UPDATE patience SET Result = %s WHERE PCID = %s"
   try:
      cursor.execute(sql, (newresult,PCID))
   except:
      print("failed in update patience")
   db.commit()
   cursor.close()
   #db.close()
   





################  ################  detect part  ################ #############
@app.route('/get_photo',methods=['POST'])
def get_photo():
   res = request.get_json()
   username=res["username"]
   PCID=res["PCID"]
   picture_url=Host_URL+"/masks/"+PCID+'.png'
   result=query_patience(PCID)
   result=result['Result']
   res={"PCID":PCID,"result":result,"url":picture_url}
   log_text=log_content(username,"get result of detect\n")
   write_log(log_text)
   return res












#######################  model setting part ##################

@app.route('/settime',methods=['POST'])
def settime():
   text=request.get_data(as_text=True)
   #print(text)
   username=text.split(" ")[0]
   #print(username)
   text=" ".join(text.split(" ")[1:])
   #print(text)
   try:
      DBsettime(username,text)
      OSsettime(text)
      return "success"
   except:
      return "failed"


def OSsettime(text):
   os.system("crontab -l | grep -v 'run.py' | crontab -")
   cmd="(crontab -l ; echo '"+ text +" python3 run.py') | crontab -"
   os.system(cmd)
   log_text=log_content("The update time is set\n")
   write_log(log_text)
   

# @app.route('/settime',methods=['POST'])
# def work():
#    text=request.get_data(as_text=True)
#    date=text.split()

#    if date[4]=="*":
#       scheduler.add_job(func=run, id="1",trigger='cron',month=int(date[3]), day=int(date[2]), hour=int(date[1]), minute=int(date[0]),second=0, replace_existing=True)
#    else:
#       scheduler.add_job(func=run, id="1",trigger='cron',day_of_week=int(date[4])-1, hour=int(date[1]), minute=int(date[0]),second=0, replace_existing=True)

def DBsettime(username,text):
   if querytime(username) == 0:
      date=text.split()
      print(date)
      user=queryuser(username)
      print(user)
      UID=user['UID']
      print(UID)
      cursor = db.cursor()
      sql = "INSERT INTO setting (min,hour,day,month,week,UID) VALUES (%s,%s,%s,%s,%s,%s)"
      try:
         cursor.execute(sql, (date[0],date[1],date[2],date[3],date[4],UID))
      except:
         print("failed in inserting time")
      
      db.commit()
      cursor.close()
         #db.close()
   else:
      updatetime(username,text)

def updatetime(username,text):
   date=text.split()
   cursor = db.cursor()
   user=queryuser(username)
   UID=user['UID']
   sql = "UPDATE setting SET min = %s, hour=%s, day=%s, month=%s,week=%s WHERE UID = %d"
   try:
      cursor.execute(sql, (date[0],date[1],date[2],date[3],date[4],UID))
   except:
      print("failed in update time")
   cursor.close()
         #db.close()
   

def querytime(username):
   cursor = db.cursor()
   user=queryuser(username)
   UID=user['UID']
   sql = "SELECT * FROM setting WHERE UID=%s"
   try:
      result = cursor.execute(sql, (UID,))
   except:
      print("failed in query time")
   cursor.close()
   print(result)
   #db.close()
   return result
   

@app.route('/manual_run',methods=['POST'])
def manual_run():
   run()
   log_text=log_content("Model is manual updated\n")
   write_log(log_text)
   return ""

def run():
   cmd="jupyter nbconvert --to notebook --execute /Users/lucas/Documents/postgraduate/summerproject/LFX/spirit/flask-server/middlemodel.ipynb"
   os.system(cmd)










###############      mysql + usersystem       ############################

def insert_user(username,password,access):
   cursor = db.cursor()
   sql = "INSERT INTO hosuser (user_name, Password, access) VALUES (%s,%s,%s)"
   print(sql)
   result = cursor.execute(sql,(username,password,access))
   if result:
      db.commit()
      cursor.close()
      #db.close()
      return True
   else:
      print("wrong in insert!")
      return False


def queryuser(username):
   cursor = db.cursor()
   sql = "SELECT UID, password, access FROM hosuser WHERE user_name=%s"
   result = cursor.execute(sql, (username,))
   if result:
      result = cursor.fetchone()
      cursor.close()
      #db.close()
      return result
   else:
      print("wrong with the user query")

def updateuser(username:str,newpassword:str):
   cursor = db.cursor()
   sql = "UPDATE hosuser SET Password = %s WHERE user_name = %s"
   try:
      result=cursor.execute(sql, (newpassword,username))
   except:
      print("wrong in update user")
   #print(result)
   if result:
      db.commit()
      cursor.close()
      #db.close()
      return True
   else:
      print("do not set the same password")
      return False


@app.route('/login',methods=['POST'])
def login():
   recv=request.get_data()
   recv_json=json.loads(recv)
   username=recv_json["username"]
   password=recv_json["password"]
   query=queryuser(username)
   if password==query['password']:
      write_log(log_content(username,"Login success\n"))
      return {"username":username,"access":query["access"]}
   else:
      write_log(log_content(username,"Login fail\n"))
      return {"username":username,"access":0}

@app.route('/register',methods=['POST'])
def register():
   recv=request.get_data()
   recv_json=json.loads(recv)
   username=recv_json["username"]
   password=recv_json["password"]
   identity=recv_json["identity"]
   if identity=="Doctor":
      access="1"
   elif identity=="Detector":
      access="2"

   judge=insert_user(username,password,access)
   if judge:
      write_log(log_content(username,"Register success\n"))
      return {"success":1}
   else:
      write_log(log_content(username,"Register fail\n"))
      return {"success":0}


@app.route('/updatepassword',methods=['POST'])
def updatepassword():
   recv=request.get_data()
   recv_json=json.loads(recv)
   username=recv_json["username"]
   password=recv_json["password"]
   #print(username,password)
   #print(type(username),type(password))
   judge=updateuser(username,password)
   if judge:
      write_log(log_content(username,"Password changed success\n"))
      return {"success":1}
   else:
      write_log(log_content(username,"Password changed fail\n"))
      return {"success":0}












##########################    Log System    ###############

@app.route('/receiveLog',methods=['GET'])
def log():
   log=''
   with open(LOG_PATH+'/log.txt', 'r') as f:
      for line in f:
         log=log+line
   return log
   #return send_from_directory(LOG_PATH,'log.txt')

#####  depending on frontend
@app.route('/receivepic',methods=['GET'])
def receivepic():
   result=""
   for name in os.walk(LOG_PATH+'/model/'):
      for n in name[2]:
         result=result+Host_URL+"/model/"+n+"\n"
   return result

@app.route('/receivepic1',methods=['GET'])
def receivepic1():
   picture_url=Host_URL+'/model/seg-loss.png'
   return picture_url

@app.route('/receivepic2',methods=['GET'])
def receivepic2():
   picture_url=Host_URL+'/model/seg-accuracy.png'
   return  picture_url

@app.route('/receivepic3',methods=['GET'])
def receivepic3():
   ##############  add image name 
   picture_url=Host_URL+'/model'
   return picture_url

@app.route('/receivepic4',methods=['GET'])
def receivepic4():
   ##############  add image name 
   picture_url=Host_URL+'/model'
   return  picture_url


def log_content(name,text):
   return time.ctime()+"               "+name+"               "+text

def write_log(text):
   log=''
   try:
      with open(LOG_PATH+'/log.txt', 'r') as f:
         for line in f:
            log=log+line
   except:
      pass
   with open(LOG_PATH+'/log.txt', 'w+') as txt:
      txt.write(text) 
      txt.write(log)



if __name__ == '__main__':
   write_log(log_content("","Server start\n"))
   app.run(debug=True,port=5000)


