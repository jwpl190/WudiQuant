import requests
a = '600460'
b = '000651'
msg1 = {}
msg1['stock'] = a
msg2 = {}
msg2['stock'] = b
dictToSend = []
dictToSend.append(msg1)
dictToSend.append(msg2)
# dictToSend.append(msg2)
requests.post('http://18.216.249.24:80/weimaiAlertProc', json=dictToSend)