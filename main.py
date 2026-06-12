from flask import Flask,render_template,request,redirect,session,url_for
from flask_socketio import SocketIO,join_room,leave_room,send
import random
import os
from string import ascii_lowercase,ascii_uppercase, digits
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# from dotenv import load_dotenv
# load_dotenv()
# print("mongo url: ",os.getenv("MONGO_URI"))
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chat_app"]
users_collection = db["users"]

app=Flask(__name__)
app.config["SECRET_KEY"]= os.getenv("SECRET_KEY")
socketio=SocketIO(app)

rooms={}

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = users_collection.find_one(
            {"username": username}
        )

        if existing_user:
            return render_template(
                "register.html",
                error="Username already exists"
            )

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one(
            {"username": username}
        )

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["username"] = username

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



def generate_unique_code(length):
    characters=ascii_uppercase+ascii_lowercase+digits
    return ''.join(random.choices(characters,k=length))

@app.route("/",methods=["GET","POST"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    
    if request.method=="POST":
        code=request.form.get("code")
        join=request.form.get("join",False) 
        create=request.form.get("create",False)
        
        
        if join!=False and not code:
            return render_template("home.html",error="Please enter a room code")
        room=code.strip()
        if create!=False:
            room=generate_unique_code(4)
            rooms[room]=room
            creator_name=session["username"]
            rooms[room] = {"creator_name":creator_name,
                           "members":0,
                           "messages":[]
                           }
            
        if join!=False and room not in rooms:
            return render_template("home.html",error="Please enter a valid room code!",name=name,code=code)
        # else:
        #     rooms[room]["members"]+=1  no hardcode😊
        
        print(rooms)
        
        session["room"]=room
        session["name"]=session["username"]
        
        # return render_template("room.html",creator_name=rooms[room]["creator_name"],name=name,room=room,members=rooms[room]["members"])
        return redirect(url_for('room'))
        #join and create are buttons so they are not going to return anything or they just say yes.. this button is pressed which is gonna 
        # return None to avoid we use default value=False 
    return render_template("home.html")

@app.route('/room')
def room():
    name=session.get("name")
    room=session.get("room")
    
    #print(f"rooms[room]={rooms[room]}")
    if room not in rooms:
       return redirect("/")
   
    return render_template("room.html",creator_name=rooms[room]["creator_name"],name=name,room=room,messages=rooms[room]["messages"],members=rooms[room]["members"])
    
## Socket -- listen to socketio's request

##When someone joins 
@socketio.on("connect")
def connect(auth): ##use that connect
    room=session.get("room")
    name=session.get("name")
    
    if not room or not name:
        return
    if room not in rooms:
        return 
    
    join_room(room)
    rooms[room]["members"]+=1
    send(
        {"name":name,"message":"has joined the room"},
        to=room
        )
    socketio.emit(
        "members_count",
        {"name": name,
         "count": rooms[room]["members"]},
        to=room
    )
    
    print(f"{name} joined the chat\nMembers - {rooms[room]["members"]}")


## when someone lefts
@socketio.on("disconnect")
def disconnect():
    room=session.get("room")
    name=session.get("name")
    
    if not room or room not in rooms:
        return

    leave_room(room)
    
    rooms[room]["members"]-=1

    send(
        {"name":name ,"message":"has left the room"},
        to=room
        )
    socketio.emit(
        "members_count",
        {"name": name,
         "count": rooms[room]["members"]},
        to=room
    )
    
    print(f"{name} left the chat\nMembers - {rooms[room]["members"]}")  
   
    if rooms[room]["members"]<=0:
          del rooms[room]
           

@socketio.on("message")
def message(data):
    room=session.get("room")
    content={
        "name":session.get("name"),
        "message":data["data"]
    }
    send(content,to=room)
    rooms[room]["messages"].append(content)

if __name__=="__main__":
    socketio.run(app,host="0.0.0.0",port=5000,debug=False)