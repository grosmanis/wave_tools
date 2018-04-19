import time
import wlan
''''
board = wlan.utils('COM4')
board.ConsoleWrite('\n', board.uboot_prompt)
ethaddr = board.GetUbootVar('ethaddr')
ipaddr = board.GetUbootVar('ipaddr')
serverip = board.GetUbootVar('serverip')
tftppath = board.GetUbootVar('tftppath')
board.log_write(ethaddr)
board.log_write(ipaddr)
board.log_write(serverip)
board.log_write(tftppath)
board.SetUbootVar('serverip', '192.168.1.2')
board.SetUbootVar('ipaddr', '192.168.1.3')
board.SetUbootVar('tftppath', '/ugw/openwrt/core/bin/lantiq/grx550_2000_mr_vdsl_lte_sec_gw_711/')

board.ConsoleWrite('nand erase clean\n', board.uboot_prompt)
board.ConsoleWrite('run update_nandboot\n', board.uboot_prompt)
board.ConsoleWrite('run update_bootcore update_fullimage\n', board.uboot_prompt)
board.SetUbootVar('ethaddr', ethaddr)
board.SetUbootVar('ipaddr', ipaddr)
board.SetUbootVar('serverip', serverip)
board.SetUbootVar('tftppath', tftppath)
board.ConsoleWrite('save\n','')
board.ConsoleWrite('reset\n','')
del board
'''
board = wlan.utils('COM6')
board.ConsoleWrite('\n', board.uboot_prompt)
ethaddr = board.GetUbootVar('ethaddr')
board.log_write(ethaddr)
board.SetUbootVar('serverip', '192.168.1.2')
board.SetUbootVar('ipaddr', '192.168.1.1')
board.SetUbootVar('tftppath', 'ugw/openwrt/core/bin/lantiq/grx550_2000_mr_vdsl_lte_sec_gw_711/')
#board.SetUbootVar('tftppath', 'ugw_sw/ugw/openwrt/core/bin/lantiq/grx550_2000_mr_vdsl_lte_sec_gw_711/')
#master mac AC:9A:96:F3:D0:00
#slave mac AC:9A:96:F4:84:A0
#board.SetUbootVar('tftppath', 'grx550_2000_mr_vdsl_lte_sec_gw_711/')

board.ConsoleWrite('nand erase clean\n', board.uboot_prompt)
board.ConsoleWrite('run update_nandboot\n', board.uboot_prompt)
#board.ConsoleWrite('run update_gphyfirmware\n', board.uboot_prompt)
#time.sleep(4)
board.SetUbootVar('tftppath', '/ugw/openwrt/core/bin/lantiq/grx550_2000_mr_vdsl_lte_sec_gw_711/')
board.ConsoleWrite('run update_bootcore update_fullimage\n', board.uboot_prompt)
board.SetUbootVar('ethaddr', ethaddr)
board.ConsoleWrite('save\n','')
board.ConsoleWrite('reset\n','')

