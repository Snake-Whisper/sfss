var socket = io.connect('https://' + document.domain + ':' + location.port);
socket.on('connect', function() {
	socket.emit('my event', {data: 'I\'m connected!'});
	alert("connected");
    });

function
