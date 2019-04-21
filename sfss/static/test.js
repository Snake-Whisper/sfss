var socket = io.connect('https://' + document.domain + ':' + location.port + "/chat");
socket.on('connect', function() {
	//socket.emit('sendChat', {data: 'I\'m connected!'});
	alert("connected");
    });
socket.on("response", function(msg) {
	alert(msg);
});
var inputField = document.getElementById("postField");
inputField.value = "hallo";

function submitChat () {
	//alert("try to send");
	if (typeof activeChat !== 'undefined') {
		socket.emit("sendChat", {data: inputField.value, chat: activeChat});
		inputField.value = '';
		alert("send");
	} else {
		alert("Please select a chat!")
	};
}

var frame = document.getElementById("chatFrame");

function newEntry(username, content, ctime) {
	var bubble = document.createElement("DIV");
	bubble.innerHTML="hamsdvflkmsavklmdfklsvmdf"
	var con = document.createTextNode(content);
	bubble.appendChild(con);
	frame.html.body.appendChild(bubble);
}

newEntry("hallo", "Inhalt", 515631);