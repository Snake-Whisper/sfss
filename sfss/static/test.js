var socket = io.connect('https://' + document.domain + ':' + location.port);
socket.on('connect', function() {
	socket.emit('my event', {data: 'I\'m connected!'});
	alert("connected");
    });
socket.on("response", function(msg) {
	alert(msg);
});
var inputField = document.getElementById("postField");
inputField.value = "hallo";
function submitChat () {
	alert("try to send");
	socket.emit("my event", {data: inputField.value});
	inputField.value = '';
	alert("send");
}
