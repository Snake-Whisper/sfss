var me;
var socket = io.connect('https://' + document.domain + ':' + location.port + "/chat");
socket.on('connect', function() {
	//init with clear of all?
	console.log("connected");
    });

socket.on("response", function(msg) {
	alert(msg);
});

socket.on("setup", function(msg) {
	console.log("recv me");
	me = msg;
});



socket.on("loadChat", function(msg) {
	console.log(msg);
	clearChat();
	var chatEnriesJson = JSON.parse(msg);	
	for (var i = 0; i<chatEnriesJson.length; i++) {
		addChatEntry(chatEnriesJson[i]["username"],
					 chatEnriesJson["content"],
					 chatEnriesJson[i]["ctime"]);
	}
	
});

var inputField = document.getElementById("postField");
inputField.value = "hallo";

function submitChat () {
	if (typeof activeChat !== 'undefined') {
		socket.emit("sendChatEntry", {data: inputField.value, chat: activeChat});
		inputField.value = '';
		alert("send");
	} else {
		alert("Please select a chat!")
	};
}

function getChat(chatId) {
	socket.emit("getChat", {"chatId" : chatId});
}

var chats = document.getElementById("chats");
var chatEntries = document.getElementById("chat");

async function addChatEntry(username, message, ctime) {
	while (typeof(me) === undefined) {
		sleep(200);
	}
	var bubble = document.createElement("DIV");
	var head = document.createElement("DIV");
	var content = document.createElement("DIV");
	var foot = document.createElement("DIV");
	bubble.className = username == me ? "selfPost speech-bubble-right": "foreignPost speech-bubble-left";
	head.className = "head";
	content.className = "content";
	foot.className = "foot";
	
	head.innerHTML = username;
	content.innerHTML = message;
	foot.innerHTML = ctime;
	
	bubble.appendChild(head);
	bubble.appendChild(content);
	bubble.appendChild(foot);
	
	chatEntries.appendChild(bubble);
}

function clearChat() {
	while (chatEntries.firstChild) {
		chatEntries.removeChild(chatEntries.firstChild);
	}
}

function Sleep(milliseconds) {
 return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function addchat2List(name, chatId) {
	var chat = document.createElement("DIV");
	chat.className = "chats";
	chat.setAttribute("onclick", "getChat("+chatId+")"); //eventlistener?
	chat.innerHTML = name;
	chats.appendChild(chat);
}

function clearChatList() {
	while (chats.firstChild) {
		chats.removeChild(chats.firstChild);
	}
}