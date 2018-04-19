import wlan
board = wlan.utils()

#board.SerialLogin()
#board.Reboot()
#board.WaitOnSerial('Hit any key to stop autoboot')
#board.ConsoleWrite('\n', board.uboot_prompt)
ethaddr = board.GetUbootVar('ethaddr')
board.log_write(ethaddr)
board.ConsoleWrite('run update_bootcore\n', board.uboot_prompt)
board.ConsoleWrite('run update_nandboot\n', board.uboot_prompt)
board.ConsoleWrite('run update_gphyfirmware\n', board.uboot_prompt)
board.ConsoleWrite('run update_fullimage\n', board.uboot_prompt)
board.SetUbootVar('ethaddr', ethaddr)
board.ConsoleWrite('save\n', board.uboot_prompt)
board.ConsoleWrite('reset\n', board.uboot_prompt)
  
