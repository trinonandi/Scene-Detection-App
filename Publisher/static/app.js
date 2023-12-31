document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log('Connected to server');
    });

    socket.on('upload_progress', function (data) {
        var progressBar = document.getElementById('progressBar');
        progressBar.value = data.percent_complete;
        var status = document.getElementById('status');
        status.innerHTML = 'Uploading... ' + data.percent_complete.toFixed(2) + '%';
    });

    socket.on('upload_complete', function (data) {
        var progressBar = document.getElementById('progressBar');
        progressBar.value = 100;
        var status = document.getElementById('status');
        status.innerHTML = 'Upload complete!';
        console.log('File URL:', data.file_url);
    });
});

function uploadFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }

    var formData = new FormData();
    formData.append('file', file);

    fetch('http://' + document.domain + ':' + location.port + '/upload', {
        method: 'POST',
        body: formData,
        headers: {
            // Include any headers if needed (e.g., for authentication)
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(HTTP error! Status: ${response.status});
        }
        return response.json();
    })
    .then(data => {
        var progressBar = document.getElementById('progressBar');
        progressBar.value = 100;
        var status = document.getElementById('status');
        status.innerHTML = 'Upload complete!';
        console.log('File URL:', data.file_url);
    })
    .catch(error => {
        var status = document.getElementById('status');
        status.innerHTML = 'Error occurred during upload: ' + error.message;
    });
}