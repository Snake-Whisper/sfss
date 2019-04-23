var me;
var socket = io.connect('https://' + document.domain + ':' + location.port + "/chat");
socket.on('connect', function() {
	//init with clear of all?
	console.log("connected");
    });


socket.on("setupMe", function(msg) {
	me = msg;
});

socket.on("loadChat", function(msg) {
	clearChat();
	var chatEnriesJson = JSON.parse(msg);	
	for (var i = 0; i<chatEnriesJson.length; i++) {
		addChatEntry(chatEnriesJson[i]["username"],
					 chatEnriesJson[i]["content"],
					 chatEnriesJson[i]["ctime"]);
	}
	
});

socket.on("loadChatList", function (msg) {
	var chatList = JSON.parse(msg)
	for (var i = 0; i<chatList.length; i++) {
		addchat2List(chatList[i]["name"],
					chatList[i]["id"]);
	}
});

socket.on("recvPost", function(msg) {
	var chatEnriesJson = JSON.parse(msg);
	for (var i = 0; i<chatEnriesJson.length; i++) { //I'm not lazy. Prob. there're coming multiple posts at same time XD
		if (typeof(activeChat) !== "undefined"
			&& chatEnriesJson[i]["chatId"] == activeChat) {			
			addChatEntry(chatEnriesJson[i]["username"],
						 chatEnriesJson[i]["content"],
						 chatEnriesJson[i]["ctime"]);
			document.getElementById(activeChat)
		} else {
			var chat = document.getElementById(chatEnriesJson[i]["chatId"]);
			chat.classList.add("noticeMe")
			chat.addEventListener("mouseover", terminateNoticeMe);
		}
	}
});

var inputField = document.getElementById("postField");
inputField.value = "hallo";

function sendPost () {
	if (typeof activeChat !== 'undefined') {
		socket.emit("sendPost", {content: inputField.value, chatId: activeChat});
		inputField.value = '';
	} else {
		alert("Please select a chat!")
	};
}

function terminateNoticeMe() {
	event.target.classList.remove("noticeMe");
	event.target.removeEventListener("mouseover", terminateNoticeMe);
	event.target.classList.add("notRead");
	event.target.addEventListener("click", terminateNotRead);
}

function terminateNotRead() {
	event.target.classList.remove("notRead");
	event.target.removeEventListener("click", terminateNotRead);
	
}

function getChat(chatId) {
	socket.emit("cdChat", {"chatId" : chatId});
}

var chats = document.getElementById("chats");
var chatEntries = document.getElementById("chat");
var objectsBar = document.getElementById("objectsBar");

async function addChatEntry(username, message, ctime) {
	while (typeof(me) === "undefined") {
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
	chatEntries.scrollTop = chatEntries.scrollHeight;
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
	chat.setAttribute("id", chatId);
	chat.addEventListener("click", changeChat);
	chat.innerHTML = name;
	chats.appendChild(chat);
}

function clearChatList() {
	while (chats.firstChild) {
		chats.removeChild(chats.firstChild);
	}
}

function changeChat() {
	getChat(event.target.id);
	activeChat = event.target.id;
}

function clearObjectsBar() {
	while (objectsBar.firstChild) {
		objectsBar.removeChild(objectsBar.firstChild);
	}
	
	addObjects2ObjectsBar("+", false);
}

function addObjects2ObjectsBar(content, active) {
	var obj = document.createElement("DIV");
	obj.className = "object";
	obj.innerHTML = content;
	
	var objTab = document.createElement("DIV");
	objTab.className = active ? "objectTab active" : "objectTab";
	
	objTab.appendChild(obj);
	objectsBar.insertBefore(objTab, objectsBar.lastElementChild);
}