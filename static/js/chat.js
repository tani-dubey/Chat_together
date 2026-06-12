
//initialize socketio
var socketio=io();

//Listen to messages coming from main.py
const messageList=document.getElementById("messages-list")
const members_count = document.getElementById("members_count")

socketio.on("members_count", (data) => {
    members_count.innerHTML = 
                `Joined as ${data.name} | Total Members: ${data.count}`;
});

//message is coming from main.py and messageList is the section where
//messages will be displayed
const createMessage= (name,message)=> {
    console.log(message)
    let content;

    if (message === "has joined the room" || message ==="has left the room"){
        content= `
        <div class="log-message">
            <span class="time">${new Date().toLocaleTimeString()}</span>
            <span class="event">${name} ${message}</span>
        </div>
        `;
    }
    else{
        content= `
        <div>
        <span> <strong>${name}</strong>: ${message} </span> <!--strong tag makes it bold -->
            <span class="time"> ${new Date().toLocaleTimeString()} </span>
        </div>
        `;
    }
    messageList.innerHTML += content;
    messageList.scrollTop = messageList.scrollHeight;
}
socketio.on("message",(data) => {
    createMessage(data.name,data.message);
});

const sendMessage= () => {
    const said=document.getElementById("message-input");
    if(said.value==""){
        return;
    }
    socketio.emit("message",{
        data:said.value
    });
    said.value="";
}

document.getElementById("message-input").addEventListener("keypress",function(event){
    if(event.key==="Enter"){
        event.preventDefault(); //prevent default behaviour of enter key
        sendMessage();
    }
});