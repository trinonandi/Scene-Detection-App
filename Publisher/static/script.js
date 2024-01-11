function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

uuid = guid()
const eventSource = new EventSource('http://127.0.0.1:5000/sse');

eventSource.onmessage = function (currentEvent) {
if (currentEvent.data.length > 0) {
    if(currentEvent.data.startsWith("Progress: ")) {
        let percent = Number(currentEvent.data.toString().split("Progress: ")[1])
        document.getElementById("progressBar").value = percent;
    }
}
};

eventSource.onerror = function (error) {
  console.log(error);
}

