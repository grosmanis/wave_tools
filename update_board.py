import time
import wlan
board = wlan.utils(serialport = 'COM8')
board.SerialLogin()
#board.ConsoleWrite('res\n', 'Hit any key to stop autoboot')
board.ConsoleWrite('\n', board.uboot_prompt)
ethaddr = board.GetUbootVar('ethaddr')
ipaddr = board.GetUbootVar('ipaddr')
serverip = board.GetUbootVar('serverip')
tftppath = board.GetUbootVar('tftppath')
board.log_write(ethaddr)
board.log_write(ipaddr)
board.log_write(serverip)
board.log_write(tftppath)
#AC:9A:96:F3:DD:00 master
#AC:9A:96:F4:84:A0 slave
board.SetUbootVar('serverip', '192.168.1.2')
board.SetUbootVar('ipaddr', '192.168.1.1')
board.SetUbootVar('tftppath', 'tmp/grx550_2000_mr_vdsl_lte_sec_gw_711/')
board.ConsoleWrite('nand erase clean\n', board.uboot_prompt)
board.ConsoleWrite('run update_nandboot\n', board.uboot_prompt)
board.ConsoleWrite('run update_gphyfirmware\n')
time.sleep(3)
board.ConsoleWrite('run update_bootcore update_fullimage\n', board.uboot_prompt)
board.SetUbootVar('ethaddr', ethaddr)
board.SetUbootVar('ipaddr', ipaddr)
board.SetUbootVar('serverip', serverip)
board.SetUbootVar('tftppath', tftppath)
board.ConsoleWrite('save\n','')
board.ConsoleWrite('reset\n','')

  
