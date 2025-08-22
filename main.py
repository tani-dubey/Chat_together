from flask import Flask,render_template,request,redirect,session,url_for
from flask_socketio import SocketIO,join_room,leave_room,send
import random
from string import ascii_lowercase,ascii_uppercase, digits

app=Flask(__name__)
app.config["SECRET_KEY"]= "dvcyidsvtlu"
socketio=SocketIO(app)

rooms={}
#rooms_map={}
def generate_unique_code(length):
    characters=ascii_uppercase+ascii_lowercase+digits
    return ''.join(random.choices(characters,k=length))

@app.route("/",methods=["GET","POST"])
def home():
    session.clear()
    if request.method=="POST":
        name=request.form.get("name")
        code=request.form.get("code")
        join=request.form.get("join",False) 
        create=request.form.get("create",False)
        
        
        if join!=False and not code:
            return render_template("home.html",error="Please enter a room code")
        room=code.strip()
        if create!=False:
            room=generate_unique_code(4)
            rooms[room]=room
            creator_name=name 
            rooms[room] = {"creator_name":creator_name,"members":1,"messages":[]}
            create=False
            
        if join!=False and room not in rooms:
            return render_template("home.html",error="Please enter a valid room code!",name=name,code=code)
        # else:
        #     rooms[room]["members"]+=1  no hardcode😊
        
        print(rooms)
        
        session["room"]=room
        session["name"]=name
        
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
        leave_room(room)
        return 
    
    join_room(room)
    rooms[room]["members"]+=1
    send({"name":name,"message":"has joined the room"},to=room)
    
    print(f"{name} joined the chat\nMembers - {rooms[room]["members"]}")

## when someone lefts
@socketio.on("disconnect")
def disconnect():
    room=session.get("room")
    name=session.get("name")
    leave_room(room)
    
    if room in rooms:
        rooms[room]["members"]-=1

        
        if rooms[room]["members"]<=0:
          del rooms[room]
          
        send({"name":name ,"message":"has left the room"},to=room)
        print(f"{name} left the chat\nMembers - {rooms[room]["members"]}")   

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
    socketio.run(app,debug=True)