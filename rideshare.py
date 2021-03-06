from flask import Flask, request, jsonify,redirect,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import json
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER  
from sqlalchemy.orm import sessionmaker
import re
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



 

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'RS.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

#CREATE A CLASS USER 
class User(db.Model):
    username = db.Column(db.String(30), unique=True,primary_key=True)
    password=db.Column(db.String(40),nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password' )

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#CREATE A CLASS RIDE
class Ride(db.Model):    
    rideId=db.Column(db.Integer,primary_key=True)
    created_by = db.Column(db.String(80),db.ForeignKey('user.username'))
    timestamp = db.Column(db.String(30))
    source=db.Column(db.String(20))
    destination=db.Column(db.String(80))
   
	
    def __init__(self, rideId,created_by,timestamp,source,destination):
        self.rideId=rideId
        self.created_by = created_by
        self.timestamp = timestamp
        self.source = source
        self.destination =destination
       
class RideSchema(ma.Schema):
    class Meta:
        fields = ('rideId','created_by','timestamp','source','destination' )

ride_schema = RideSchema()
rides_schema = RideSchema(many=True)



##################create new table User_Ride people 
#CREATE A CLASS User_Ride
class User_Ride(db.Model):
    username = db.Column(db.String(30),db.ForeignKey('user.username'),primary_key=True)
    rideId=db.Column(INTEGER(unsigned=True),db.ForeignKey('ride.rideId'), primary_key=True)



    def __init__(self, username, rideId):
        self.username = username
        self.rideId = rideId

class URSchema(ma.Schema):
    class Meta:
        fields = ('username', 'rideId' )

ur_schema = URSchema()
urs_schema = URSchema(many=True)


#------------------(1)
#1 (ADD USER)
@app.route("/api/v1/users",methods=["PUT"])    
def add_user():
    username = request.json['username']
    password = request.json['password']
    if not(re.match(r'^[A-Fa-f0-9]{40}$', password)):
        return jsonify({}),400
    new_user = User(username,password) 
    user=User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify({}),400

    else:
         db.session.add(new_user)
         db.session.commit()
         return jsonify({}),201
         
         #return user_schema.jsonify(new_user),200
   

#-------------------(2)
# 2.(DELETE USER)
@app.route("/api/v1/users/<username>", methods=["DELETE"])
def user_delete(username):
    user = User.query.get(username)
    if user is None:
        return jsonify({}),400
    else:    
        db.session.delete(user)
        db.session.commit()
    return jsonify({}),200



#---------------------(3)
#3.(CREATE A NEW RIDE)
@app.route("/api/v1/rides",methods=["POST","GET"])    
def add_ride():
    if(request.method=="POST"):
        rideId=request.json['rideId']
        created_by = request.json['created_by']
        timestamp = request.json['timestamp']
        source = request.json['source']
        destination = request.json['destination']
        user=User.query.filter_by(username=created_by).first()
        if user is None:
             return jsonify({}),400
        else:
             try:
                 new_ride = Ride(rideId,created_by,timestamp,source,destination)
                 db.session.add(new_ride)
                 db.session.commit()
                 #return rides_schema.jsonify(new_ride),200
                 return jsonify({}),201
             except Exception as e:
                 print(e)
                 return jsonify({}),400
    elif(request.method=="GET"):
        try:
            source=request.args.get("source")
            destination=request.args.get("destination")
            #user=User.query.filter_by(username=username).first()
            ride=Ride.query.filter_by(source=source,destination=destination).all()
            json_result=[]
            for result in ride:
                 d={}
                 d["rideId"]=result.rideId
                 d["username"]=result.created_by  #Ride object has no attribute called username
                 d["timestamp"]=result.timestamp
                 json_result.append(d)
                 return jsonify(json_result),200
                 #result = rides_schema.dump(new_ride)
                 return jsonify(result)
        except Exception as e:
                 print("hello")
                 print(e)
                 return jsonify({}),400
                 #abort(400)
    else:
          pass

### join ride
@app.route("/api/v1/rides/<rideId>",methods=["POST","GET"])  
def join_ride(rideId):
    if(request.method=="POST"):
       username=request.json["username"]
       new_join=User_Ride(rideId=rideId,username=username)
      
       ride=Ride.query.filter_by(rideId=rideId).first()
       if ride is None:
          return jsonify({}),200
       user=User.query.filter_by(username=username).first()
       if user is None:
          return jsonify({}),400
       if (user and ride):
          db.session.add(new_join)
          db.session.commit()
          return jsonify({}),200


    elif(request.method=="GET"):
       ride=Ride.query.filter_by(rideId=rideId).first()
       users=User_Ride.query.filter_by(rideId=rideId).all()
       print("hhhhhhhhh")
       d={}
       d['rideId']=ride.rideId  
       d['created_by']=ride.created_by
       d['timestamp']=ride.timestamp
       d['source']=ride.source
       d['destination']=ride.destination
       for i in users:
           d["users"].append(i.username)
       return jsonify(d)
       return jsonify({}),200
    else:
         
        


'''#5.try.list all the details of a given rides             ========?????
@app.route('/api/v1/rides',methods=['GET'])
def get_all_rides():
    if request.method =='GET':
        results = Ride.query.filter_by().all()
        json_results = []
        for result in results:
            d = {
                'rideId':result.rideId,
                'created_by':result.created_by,
                'timestamp':result.timestamp,
                'source':result.source,
                'destination':result.destination
            }
            json_results.append(d)
        return jsonify(json_results)
'''


#---------------------------(7)
# 7.ENDPOINT TO DELETE RIDE
@app.route("/api/v1/rides/<rideId>", methods=["DELETE"])
def ride_delete(rideId):
    ride = Ride.query.get(rideId)
    if ride is None:
       return jsonify({}),400
    else:
        db.session.delete(ride)
        db.session.commit()

    #return user_schema.jsonify(ride),200 
    return jsonify({}),200


#8.write to db 
@app.route("/api/v1/db/write", methods=["POST"])
def writeDD():

  data=request.json['insert']
  table=request.json['table']
  column=request.json['column']
  lis=[]
  for i in  data:
      if type(i) is str:
         print(type(i))
         lis.append("\'"+i+"\'")
      else:
         lis.append(str(i))
  #print(lis)
  res=""
  for i in column:
     res=res+i+','
  
  res=res.strip(',')
  print(res)
  # res is the comma separated string of column names
  t2=""
  for i in lis:
     t2=t2+i+','
  t2=t2.strip(',')
  print(t2)
  var1=db.session.execute("insert into " + table+ "("+res+ ")  values("+ t2+")")
  return jsonify({}),200

   


#9.read from table
@app.route("/api/v1/db/read",methods=['POST'])
def readdb():

   table=request.json['table']
   column=request.json['columns']
   where_val=request.json['where']
   #var=db.session.execute("select * from User where username Like '"+username+"' and password Like '"+password+"'")
   var=db.session.execute("select "+ column + " from " + table + " where " + where_val)
   for i in var:
       print(i)
   return jsonify({}),200


 

if __name__ == '__main__':
    app.run(debug=True)





        

