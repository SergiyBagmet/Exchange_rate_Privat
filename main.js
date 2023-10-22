console.log('Hello world!')

const ws = new WebSocket('ws://127.0.0.1:8080')

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
  }

formChat.addEventListener('submit', (e) => {
  e.preventDefault()
  ws.send(textField.value)
  textField.value = null
})

ws.onmessage = (e) => {
  console.log(e.data)
  text = e.data

  const parts = e.data.split(":");
  if (parts.length >= 2) {
    const type = parts[0].trim();
    const content = parts[1].trim();
    
    if (type === "html") {
      // Отобразить HTML
      const elHtml = document.createElement('div');
      elHtml.innerHTML = content;
      subscribe.appendChild(elHtml);
    }
    else{
      const elMsg = document.createElement('div')
      elMsg.textContent = text
      subscribe.appendChild(elMsg)
    }
  }
}
  


