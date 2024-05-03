// script.js
var video = document.getElementById('video-stream');
var startStopBtn = document.getElementById('start-stop-btn');
var isStreaming = true;


startStopBtn.addEventListener('click', function() {
    fetch('/toggle_camera', {method:'GET'});
    if (isStreaming) {
        isStreaming = false;
        startStopBtn.textContent = "Hide Camera";
        video.style.display="none";
    } else {
        isStreaming= true;
        startStopBtn.textContent = "Show Camera";
        video.style.display="block";
    }
});
