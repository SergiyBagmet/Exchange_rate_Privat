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

  const elMsg = document.createElement('div')
  elMsg.textContent = text
  subscribe.appendChild(elMsg)
}