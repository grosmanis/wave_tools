import wlan

board = wlan.utils('COM3', '192.168.1.1')
board.tftphostapdpath = ''
board.tftpdrvpath = ''
board.TftpdStart()
board.TelnetLogin()
board.TftpDrvToBoard()
board.TftpHostapdToBoard()
board.Reboot()
board.TftpdStop() 

