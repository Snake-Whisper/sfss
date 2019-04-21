var me;
var socket = io.connect('https://' + document.domain + ':' + location.port + "/chat");
socket.on('connect', function() {
	//init with clear of all?
    });
socket.on("response", function(msg) {
	alert(msg);
});
socket.on("setup", function(msg) {
	me = msg;
});
var inputField = document.getElementById("postField");
inputField.value = "hallo";

function submitChat () {
	if (typeof activeChat !== 'undefined') {
		socket.emit("sendChat", {data: inputField.value, chat: activeChat});
		inputField.value = '';
		alert("send");
	} else {
		alert("Please select a chat!")
	};
}

var chats = document.getElementById("chats");
var chatEntries = document.getElementById("chat");

async function newChatEntry(username, message, ctime) {
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

function addchat2List(name, id) {
	var chat = document.createElement("DIV");
	chat.className = "chats";
	chat.innerHTML = name;
	chats.appendChild(chat);
}

function clearChatList() {
	while (chats.firstChild) {
		chats.removeChild(chats.firstChild);
	}
}
