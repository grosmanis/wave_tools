import wlan

board = wlan.utils('COM3', '192.168.1.1') 
board.TelnetLogin()
#board.TftpCalToBoard()
board.TftpDrvToBoard()
#board.TftpIwToBoard()
#board.TftpFwToBoardOld()
#board.Tftp500FwToBoard()
#board.TftpHostapdToBoard()
board.Reboot()


