import wlan
from threading import Thread

def per_board(ip):
  board = wlan.utils(ipaddr=ip)
  board.tftpdrvpath = 'wave_drv/builds/ugw7.2-grx550/binaries/wls/driver/'
  board.tftpfwpath = 'fw/FW_6.0.4_Rel3.1_CDB_r15408/'
  board.tftphostapdpath = 'wave_drv/builds/ugw7.3-grx550/tools/wifi_opensource/hostapd-2.6/hostapd/'
  board.TelnetLogin()
  board.TftpDrvToBoard()
  #board.TftpFwToBoardOld()
  #board.TftpCalToBoard()
  board.TftpHostapdToBoard()
  board.Reboot()


if __name__ == '__main__':
  t1 = Thread(target=per_board,args=['192.168.1.101'])
  t2 = Thread(target=per_board,args=['192.168.1.111'])
  t1.start()
  t2.start()
  t1.join()
  t2.join()
