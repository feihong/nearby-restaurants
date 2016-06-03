# let ws = new WebSocket('ws://' + window.location.host + '/status/')
#
# ws.onopen = () => {
#   console.log('Starting...');
#   $.get('/start/')
# }
#
# ws.onmessage = (evt) => {
#   let obj = JSON.parse(evt.data)
#
#   switch (obj.type) {
#     case 'console':
#       console.log(obj.value)
#       break
#     default:
#       console.log(obj)
#   }
# }

from browser.html import P
from browser import document

document <= P('hello brython!!')
