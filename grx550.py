import wlan


if __name__ == '__main__':
  
  board = wlan.utils('COM8', '192.168.1.1')

  
  board.tftpdrvpath = 'wave_drv/builds/ugw7.2-grx550/binaries/wls/driver/'
  board.tftpfwpath = 'fw/FW_6.0.4_Rel3.1_CDB_r15408/'
  board.tftphostapdpath = 'wave_drv/builds/ugw7.2-grx550/tools/wifi_opensource/hostapd-2.6/hostapd/'
  board.TelnetLogin()
  #board.TftpCalToBoard()
  board.TftpDrvToBoard()
  #board.TftpFwToBoardOld()
  #board.Tftp500FwToBoard()
  board.TftpHostapdToBoard()
  board.Reboot()


