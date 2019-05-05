var me;
var activeChat = 0;
var writePerm = true;
var uploadPerm = true;
var grantPerm = true;
var chats = document.getElementById("chats");
var chatEntries = document.getElementById("chat");
var objectsBar = document.getElementById("objectsBar");
var progressBar = document.getElementById("UploadBar");
var fileDropZone = document.getElementById("dropFile");
var postBar = document.getElementById("post");
var fileDropZoneObject = document.getElementById("dropFileObject");
var previewFrame = document.getElementById("previewFrame");
var uploadQueue = [];
var uploadSizes = [];
var uploadTotalProceeds = [];
var inputField = document.getElementById("postField");
var socket = io.connect('https://' + document.domain + ':' + location.port + "/chat");


inputField.value = "hallo";

var fileControll = {
	storage : {},
	fileRegister : [],
	maxVersions : {},
	activeVersion : {},
	activeFile : null,
	add : function (fileObj) {
			if (!this.storage.hasOwnProperty(fileObj["fileNO"])) {
			   this.storage[fileObj["fileNO"]] = {};
				//this.storage[fileObj["fileNO"]].maxVersion = 0;
				this.maxVersions[fileObj["fileNO"]] = 0;
				//this.storage[fileObj["fileNO"]].activeVersion = 0;
				this.activeVersion[fileObj["fileNO"]] = 0;
				this.fileRegister.push(fileObj["fileNO"]);
				console.log("init");
			}
		this.storage[fileObj["fileNO"]][fileObj["version"]] = fileObj;
		if (fileObj["version"] > this.maxVersions[fileObj["fileNO"]]) {
			this.maxVersions[fileObj["fileNO"]] = fileObj["version"];
			this.activeVersion[fileObj["fileNO"]] = fileObj["version"];
		}
	},
	
	clear : function() {
		this.storage = {};
		this.fileRegister = [];
	},
	
	render : function() {
		clearObjectsBar();
		this.fileRegister.sort()
		console.log(this.fileRegister.length);
		for (var i = 0; i < this.fileRegister.length; i++) {
			console.log(i);
			addObjects2ObjectsBar(
				this.storage[this.fileRegister[i]] [this.maxVersions[this.fileRegister[i]]].url,
				false,
				this.fileRegister[i]);
			this.activeVersion[this.fileRegister[i]] = this.maxVersions[this.fileRegister[i]];
		}
	},
	
	changeVersion : function (fileNO, vers) { //later only for vers change!!!
		this.activeVersion[fileNO] = vers;
		previewFrame.data = "previews/"+this.storage[fileNO][vers].id;
	},
	
	changeFile : function (fileNO) {
		if (this.activeFile != null) {
			this.activeFile.classList.remove("active");
		}
		previewFrame.data = "previews/"+this.storage[fileNO][this.maxVersions[fileNO]].id;
		this.activeFile = document.getElementById("object"+fileNO);
		this.activeFile.classList.add("active");
	},
};

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
	clearChatList();
	var chatList = JSON.parse(msg);
	for (var i = 0; i<chatList.length; i++) {
		addchat2List(chatList[i]["name"],
					chatList[i]["id"]);
	}
});

socket.on("loadObjectsBar", function (msg) {
	clearObjectsBar();
	fileControll.clear();
	var objList = JSON.parse(msg);
	for (var i = 0; i < objList.length; i++) {
		console.log(objList[i]);
		fileControll.add(objList[i]);
		//addObjects2ObjectsBar("test", false);
	}
	fileControll.render();
});

/*socket.on("loadObjectsBarChat", function(msg) {
	var data = JSON.parse(msg);
	objList = data["files"]
	var objList = JSON.parse(msg);
	for (var i = 0; i < objList.length; i++) {
		console.log(objList[i]);
		fileControll.add(objList[i]);
		//addObjects2ObjectsBar("test", false);
	}
});*/

socket.on("recvPost", function(msg) {
	var chatEnriesJson = JSON.parse(msg);
	for (var i = 0; i<chatEnriesJson.length; i++) { //I'm not lazy. Prob. there're coming multiple posts at same time XD
		if (activeChat != 0
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

socket.on("chkWritePerm", function (msg) {
	writePerm = msg["writePerm"];
	if (writePerm) {
		post.classList.remove("hidden");
	} else {
		post.classList.add("hidden");
	}
	
});

socket.on("chkUploadPerm", function (msg) {
	uploadPerm = msg["uploadPerm"];
	if (uploadPerm) {
		fileDropZoneObject.classList.remove("hidden");
		fileDropZone.classList.remove("hidden");
	} else {
		fileDropZoneObject.classList.add("hidden");
		fileDropZone.classList.add("hidden");
	}
	
});

socket.on("chkGrantPerm", function (msg) {
	grantPerm = msg["grantPerm"];
	
});

function chkWritePerm() {
	socket.emit("chkWritePerm", {chatId: activeChat});
	//console.log("send");
}

function chkUploadPerm() {
	socket.emit("chkUploadPerm", {chatId: activeChat});
}

function chkGrantPerm() {
	socket.emit("chkGrantPerm", {chatId: activeChat});
}

function sendPost () {
	if (activeChat != 0) {
		socket.emit("sendPost", {content: inputField.value, chatId: activeChat});
		inputField.value = '';
	} else {
		alert("Please select a chat!")
	};
}

function allowDrop(ev) {
	ev.preventDefault();
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
	while (objectsBar.firstElementChild != objectsBar.lastElementChild) {
		objectsBar.removeChild(objectsBar.firstChild);
	}
	
	//addObjects2ObjectsBar("+", false);
}

function addObjects2ObjectsBar(content, active, fileNO) {
	var obj = document.createElement("DIV");
	obj.className = "object";
	obj.innerHTML = content;
	obj.setAttribute("fileNO", fileNO);
	obj.setAttribute("id", "object"+fileNO);
	obj.addEventListener("click", function (event) {
		fileControll.changeFile(event.target.getAttribute("fileNO"));
	});
	
	var objTab = document.createElement("DIV");
	objTab.className = active ? "objectTab active" : "objectTab";
	
	objTab.appendChild(obj);
	objectsBar.insertBefore(objTab, objectsBar.lastElementChild);
}

fileDropZone.addEventListener("drop", function (event) {
	event.preventDefault();
	event.stopPropagation(); //test!
	for (var i = 0; i < event.dataTransfer.files.length; i++) {
		uploadQueue.push(event.dataTransfer.files[i]);
		uploadSizes.push(event.dataTransfer.files[i].size);
	}
	uploadFiles()
}, false);

function uploadFiles() {
	console.log(uploadQueue.length);
	while (uploadQueue.length) {
		var xhr = new XMLHttpRequest();
		
		var formDataRequest = new FormData();
		var file = uploadQueue.shift();
		var currentUploadSize = uploadSizes.shift();
		formDataRequest.append("file", file);
		formDataRequest.append("chatId", activeChat);
		
		progressBar.setAttribute("max", currentUploadSize);
		progressBar.classList.add("active");
		
		xhr.upload.addEventListener("progress", function (event) {
			progressBar.setAttribute("value", event.loaded);
		});
		
		xhr.upload.addEventListener("load", function (event) {
			console.log("ready");
			progressBar.classList.remove("active");
		});
		
		xhr.onreadystatechange = function () {
  			if(xhr.readyState === 4 && xhr.status === 200) {
				console.log(xhr.responseText);
			} else if (xhr.readyState === 2 && xhr.status === 401){
				alert("You are not allowed to upload in this section");
			}
		};
		
		xhr.open("POST", "upload", true);
		xhr.send(formDataRequest);
	}
}