import telnetlib
import serial
import sys
import time
import inspect

class utils:
    def __init__ (self, serialport=None, ipaddr='192.168.1.1', telnetport=23):
      self.debug = True
      self.stdout_initial = sys.stdout
      self.shell_prompt = 'root@ugwcpe:'
      self.boardlogin = 'root'
      self.boardpassword = 'admin'
      self.tftp_ip = b'192.168.1.2'
      self.fh = None
      self.loggedin_tn = False
      self.loggedin_serial = False
      self.ipaddr = ipaddr
      self.telnetport = telnetport
      self.helloattempts = 10
      self.serialport = serialport
      self.speed = 115200
      self.sane = False
      self.uboot_prompt = 'GRX500 #'
      self.tftphostapdpath ='wave_drv/builds/ugw7.3-grx550/tools/wifi_opensource/hostapd-2.6/hostapd/'
      self.tftpdrvpath = 'wave_drv/builds/ugw7.3-grx550/binaries/wls/driver/'
      self.tftpiwpath ='wave_drv/builds/ugw7.3-grx550/tools/wifi_opensource/iw-3.17/'
      self.cfg80211path = 'ugw/openwrt/core/staging_dir/target-mips_mips32_uClibc-0.9.33.2_grx550_2000_mr_vdsl_lte_sec_gw_711/root-lantiq/lib/modules/3.10.102/'
      self.tftpfwpath = 'fw/6.0.4/FW_6.0.4_Rel2.0_r12799/'
      self.uname = ''
      try:
        self.tn = telnetlib.Telnet(self.ipaddr, self.telnetport)
      except:
        self.tn = False
      try:
        self.comport = serial.Serial(self.serialport, self.speed)
      except:
        self.comport = False
        
      if(not(self.comport or self.tn)):
        raise("Neither telnet or serial connection to the board available!\n")

    def __del__(self):
        self.log_close()
        sys.stdout = self.stdout_initial

        if(self.loggedin_tn or self.loggedin_serial):
          self.Logout()
        
        if(self.comport and self.comport.isOpen()):
          self.comport.close()
          
        if(self.tn):
          self.tn.close()
        pass
      
    def UBootSane(self):
      Attempts = self.helloattempts
      if(self.comport.isOpen()):
        while(Attempts):
          self.comport.write(b'\n')
          while (self.comport.inWaiting() < 11):
            time.sleep(0.01)
          resp = str(self.comport.read_all())
          if(resp.find(self.uboot_prompt)):
            self.sane = True
            break
          time.sleep(1)
          Attempts = Attempts - 1
      return
    
    def WaitOnSerial(self, string):
      if(self.comport.isOpen()):
        while(True):
          while (self.comport.inWaiting() < len(string)):
            time.sleep(0.01)
          resp = str(self.comport.read_all())
          self.log_write(resp)
          if(resp.find(string) > 0):
            if(self.debug):
              self.log_write("got response: %s" % resp)
            break
      return resp
    
    def ConsoleWrite(self, cmd, expected_response):
      time.sleep(2)
      cmd = cmd.encode('utf-8')
      resp = ''
      if(self.comport):
        self.comport.reset_input_buffer()
        self.comport.reset_output_buffer()
        self.comport.write(cmd)
        if(expected_response is not ''):
          resp = self.WaitOnSerial(expected_response)
      elif(self.tn):
        self.tn.write(cmd)
        resp = self.tn.read_until(expected_response.encode('utf-8'))
        self.log_write(resp)
      else:
        raise ("cannot send the command!\n")
      time.sleep(2)
      return resp
  
    def GetUbootVar(self, var):
      var = self.ConsoleWrite('print %s\n' % var, self.uboot_prompt)
      var = var.split('=')
      try:
        var = var[1].split(self.uboot_prompt)[0]
      except:
        var = "Invalid response!"
      return var.replace('\\r\\n','')
    
    def SetUbootVar(self, var, val):
      var = self.ConsoleWrite('set %s %s\n' % (var, val), self.uboot_prompt)
      return
  
    def log_open(self, filename):
        if self.fh is None:
            self.fh = open(filename, 'w')
            sys.stdout = self.fh
        return

    def log_close(self):
        if self.fh:
            self.fh.close()
            self.fh = None
        return


    def log_write(self, string):
        currenttime = time.localtime(time.time())
        writestring = [ str(currenttime[3]), str(currenttime[4]), str(currenttime[5]) ]
        # writestring.append(' ' + inspect.stack()[2][3] + '\n')
        writestring.append(' ' + inspect.stack()[1][3] + '\n')
        writestring = ':'.join(writestring)
        writestring += str(string)
        if self.fh is not None:
            self.fh.write("%s" % writestring)
            self.fh.flush()
        else:
            print ("%s" % writestring)
        return

    def RebootBoard(self):
        if self.loggedin_tn == True:
          self.tn.write(b'\n')
          s = self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
          self.log_write("%s" % s)
          self.tn.write(b'reboot -f\n')
          s = self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
          self.loggedin_tn = False
        return

    def PrepareBoard(self):
        if (self.ipaddr is not None and self.telnetport is not None):
            msg = ("\tstarted\n")
            tn = telnetlib.Telnet(self.ipaddr, self.telnetport)
            tn.read_until('root@OpenWrt:/#')
            time.sleep(1)
            tn.write('killall -9 dsl_daemon\n')
            tn.read_until('root@OpenWrt:/#')
            tn.close()
            msg += ("\tfinished\n")
            self.log_write("%s" % msg)
        else:
            self.log_write("\tSkipping, IP address or port number is not specified\n")
        return
      
    def TelnetLogin(self):
        if(self.comport):
          if (self.comport.isOpen()):
            self.comport.close()
          self.comport = False
        self.ConsoleWrite('\n', 'login:')
        self.ConsoleWrite(self.boardlogin+'\n', 'Password:')
        self.ConsoleWrite(self.boardpassword+'\n', self.shell_prompt)
        self.loggedin_tn = True
        self.uname = self.ConsoleWrite('uname -r\n', self.shell_prompt).decode("utf-8").splitlines()[1]
        return
      
    def SerialLogin(self):
      if(self.comport):
        self.ConsoleWrite('\n', 'login:')
        self.ConsoleWrite(self.boardlogin+'\n', 'Password:')
        self.ConsoleWrite(self.boardpassword+'\n', self.shell_prompt)
        self.loggedin_serial = True
        self.uname = self.ConsoleWrite('uname -r\n', self.shell_prompt).decode("utf-8").splitlines()[1]
        if(self.debug):
          self.log_write("Logged in via serial")
      else:
        raise('Serial port %d is closed\n', self.serialport)
      return
    
    def Reboot(self):
      self.ConsoleWrite('reboot -f\n', '')

      if(self.loggedin_serial):
        self.loggedin_serial = False
      
      if(self.loggedin_tn):
        self.loggedin_tn = False
      return
    
    def Logout(self):
      self.ConsoleWrite('exit\n', self.shell_prompt)
      return
    
    def TftpCalToBoard(self):
      self.RmFileOnBoard('/opt/lantiq/wave/images/cal_wlan0.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/', 'tmp/cal_wlan0-GRX350-gen4.bin')
      #self.TftpFileGet('/opt/lantiq/wave/images/', 'tmp/EASY389-VDSL-V112-SNR065/cal_wlan0.bin')
      self.ConsoleWrite('cd /opt/lantiq/wave/images', self.shell_prompt)
      self.GetPrompt()
      time.sleep(2)
      self.ConsoleWrite('mv cal_wlan0-GRX350-gen4.bin cal_wlan0.bin\n', self.shell_prompt)
      self.GetPrompt()
      self.ConsoleWrite('cp cal_wlan0.bin /tmp\n', self.shell_prompt)
      self.GetPrompt()
      self.ConsoleWrite('tar czf eeprom.tar.gz cal_*.bin\n', self.shell_prompt)
      self.GetPrompt()
      self.ConsoleWrite('upgrade eeprom.tar.gz wlanconfig 0 0\n', self.shell_prompt)
      self.GetPrompt()
      self.tn.write(b'sync\n')
      self.log_write("\tcal_wlan0.bin transferred to board")
      return
    
    def TftpDrvToBoard(self):
      if(self.loggedin_tn): 
        self.RmFileOnBoard('/opt/lantiq/lib/modules/'+self.uname+'/net/mtlkroot.ko')
        time.sleep(2)
        self.RmFileOnBoard('/opt/lantiq/lib/modules/'+self.uname+'/net/mtlk.ko')
        time.sleep(2)
        
        self.TftpFileGet('/opt/lantiq/lib/modules/'+self.uname+'/net/', self.tftpdrvpath+'mtlkroot.ko')
        time.sleep(10)
        self.TftpFileGet('/opt/lantiq/lib/modules/'+self.uname+'/net/', self.tftpdrvpath+'mtlk.ko')
        time.sleep(10)
        self.tn.write(b'sync\n')
        self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
  
        self.log_write("\tmtlk transferred to board")
      else:
        self.log_write("not logged in to telnet")
      return

    
    def TftpCfg80211ToBoard(self):
      if(self.loggedin_tn): 
        self.RmFileOnBoard('/opt/lantiq/lib/modules/3.10.102/lib80211.ko')
        self.RmFileOnBoard('/opt/lantiq/lib/modules/3.10.102/lib80211_crypt_wep.ko')
        self.RmFileOnBoard('/opt/lantiq/lib/modules/3.10.102/mac80211.ko')
        self.RmFileOnBoard('/opt/lantiq/lib/modules/3.10.102/lib80211_crypt_ccmp.ko')
        self.RmFileOnBoard('/opt/lantiq/lib/modules/3.10.102/cfg80211.ko')
        self.RmFileOnBoard('/opt/lantiq/lib/modules/3.10.102/lib80211_crypt_tkip.ko')

        
        self.TftpFileGet('/opt/lantiq/lib/modules/3.10.102/', self.cfg80211path+'lib80211.ko')
        self.TftpFileGet('/opt/lantiq/lib/modules/3.10.102/', self.cfg80211path+'lib80211_crypt_wep.ko')
        self.TftpFileGet('/opt/lantiq/lib/modules/3.10.102/', self.cfg80211path+'mac80211.ko')
        self.TftpFileGet('/opt/lantiq/lib/modules/3.10.102/', self.cfg80211path+'lib80211_crypt_ccmp.ko')
        self.TftpFileGet('/opt/lantiq/lib/modules/3.10.102/', self.cfg80211path+'cfg80211.ko')
        self.TftpFileGet('/opt/lantiq/lib/modules/3.10.102/', self.cfg80211path+'lib80211_crypt_tkip.ko')

        self.tn.write(b'sync\n')
        self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
  
        self.log_write("\t80211 transferred to board")
      else:
        self.log_write("not logged in to telnet")
      return


    def TftpHostapdToBoard(self):
      if(self.loggedin_tn): 
        self.RmFileOnBoard('/opt/lantiq/bin/hostapd')
        self.RmFileOnBoard('/opt/lantiq/bin/hostapd_cli')
        self.RmFileOnBoard('/opt/lantiq/bin/hostapd_debug')
        self.TftpFileGet('/opt/lantiq/bin/', self.tftphostapdpath+'hostapd')
        self.TftpFileGet('/opt/lantiq/bin/', self.tftphostapdpath+'hostapd_cli')
        self.TftpFileGet('/opt/lantiq/bin/', self.tftphostapdpath+'hostapd_debug')
        
        self.GetPrompt()
        self.tn.write(b'chmod 0777 /opt/lantiq/bin/hostapd\n')
        self.GetPrompt()
        self.tn.write(b'chmod 0777 /opt/lantiq/bin/hostapd_cli\n')
        self.GetPrompt()
        self.tn.write(b'chmod 0777 /opt/lantiq/bin/hostapd_debug\n')
        self.GetPrompt()
        self.tn.write(b'mv /opt/lantiq/bin/hostapd /opt/lantiq/bin/hostapd_ax\n')
        self.GetPrompt()
        self.tn.write(b'sync\n')
        self.GetPrompt()
        
        self.log_write("\thostapd transferred to board")
      else:
        self.log_write("not logged in to telnet")
      return

    def TftpIwToBoard(self):
      if(self.loggedin_tn): 
        self.RmFileOnBoard('/usr/sbin/iw')
        self.TftpFileGet('/usr/sbin/', self.tftpiwpath+'iw')
        self.GetPrompt()
        self.tn.write(b'chmod 0777 /usr/sbin/iw\n')
        self.GetPrompt()
        self.tn.write(b'sync\n')
        self.GetPrompt()
        
        self.log_write("\tiw transferred to board")
      else:
        self.log_write("not logged in to telnet")
      return


    def RmFileOnBoard(self, filename):
      self.GetPrompt()
      cmd = b'rm %s\n' % bytes(filename, 'utf-8')
      self.tn.write(cmd)
      if(self.debug == True):
        self.log_write(cmd)
      self.GetPrompt()
      return
    
    def MkDirOnBoard(self, path):
      self.tn.write(b'cd /\n')
      self.tn.read_until(self.shell_prompt)

      dirs = path.split('/')
      for i in range(1, len(dirs)):
        self.tn.write(b'mkdir %s\n' % bytes(dirs[i], 'utf-8'))
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'cd %s\n' % bytes(dirs[i], 'utf-8'))
        self.tn.read_until(self.shell_prompt)

      return
    
    def GetPrompt(self):
      self.tn.write(b'\n')
      self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
      time.sleep(1)
      return
    
    def TftpFileGet(self, PathOnBoard, RemoteTftpFileName):
      self.tn.write(b'\n')
      self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
      cmd = b'cd %s\n' % bytes(PathOnBoard, 'utf-8')
      self.tn.write(cmd)
      if(self.debug == True):
        self.log_write(cmd)
      self.tn.read_until(bytes(self.shell_prompt, 'utf-8'))
      cmd = b'tftp -gr %s %s\n' % (bytes(RemoteTftpFileName, 'utf-8'), self.tftp_ip)
      self.tn.write(cmd)
      if(self.debug == True):
        self.log_write(cmd)
      self.GetPrompt()
      return
    
    def TftpFwToBoardOld(self):
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_lower_gen5b_wrx_500.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/', self.tftpfwpath+'ap_lower_gen5b_wrx_500.bin')
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_upper_gen5b_wrx_500.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/',self.tftpfwpath+'ap_upper_gen5b_wrx_500.bin')
      '''
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_upper_gen5b_wrx_514.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/',self.tftpfwpath+'ap_upper_gen5b_wrx_514.bin')
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_lower_gen5b_wrx_514.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/',self.tftpfwpath+'ap_lower_gen5b_wrx_514.bin')
      
      self.RmFileOnBoard('/opt/lantiq/wave/images/rx_handler_gen5b.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/',self.tftpfwpath+'rx_handler_gen5b.bin')'
      '''
      self.tn.write(b'sync\n')
      self.GetPrompt()
      self.log_write("\tmtlk transferred to board")
    
    def Tftp500FwToBoard(self):
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_lower_gen5b_wrx_500.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/', self.tftpfwpath+'real_phy_wrx500/ap_lower_gen5b.bin.platform.wave500.asic')
      self.ConsoleWrite('mv ap_lower_gen5b.bin.platform.wave500.asic ap_lower_gen5b_wrx_500.bin\n', self.shell_prompt)
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_upper_gen5b_wrx_500.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/', self.tftpfwpath+'real_phy_wrx500/ap_upper_gen5b.bin.platform.wave500.asic')
      self.ConsoleWrite('mv ap_upper_gen5b.bin.platform.wave500.asic ap_upper_gen5b_wrx_500.bin\n', self.shell_prompt)
      self.tn.write(b'sync\n')
      self.GetPrompt()
      self.log_write("\tmtlk transferred to board")
      return
    
    def Tftp514FwToBoard(self):
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_lower_gen5b_wrx_514.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/', self.tftpfwpath+'real_phy_wrx514/ap_lower_gen5b.bin.platform.wave500.asic')
      self.ConsoleWrite('mv ap_lower_gen5b.bin.platform.wave500.asic ap_lower_gen5b_wrx_514.bin\n', self.shell_prompt)
      self.RmFileOnBoard('/opt/lantiq/wave/images/ap_upper_gen5b_wrx_514.bin')
      self.TftpFileGet('/opt/lantiq/wave/images/', self.tftpfwpath+'real_phy_wrx514/ap_upper_gen5b.bin.platform.wave500.asic')
      self.ConsoleWrite('mv ap_upper_gen5b.bin.platform.wave500.asic ap_upper_gen5b_wrx_514.bin\n', self.shell_prompt)
      self.tn.write(b'sync\n')
      self.GetPrompt()
      self.log_write("\tmtlk transferred to board")
      return

    def RecoverBrd(self):
      self.RebootBoard()
      self.tn.close()
      self.log_write('\tBoard is rebooted\n')
      time.sleep(100)
      self.tn = telnetlib.Telnet(self.ipaddr, self.telnetport)
      self.TelnetLogin()
      self.log_write('\tBoard is prepared\n')
      return
    
    def DebugOn(self):
      if self.loggedin_tn == True:
        self.tn.write(b'echo 8 cdebug=2 > /proc/net/mtlk_log/debug\n')
        self.tn.read_until(self.shell_prompt)
        self.log_write('\tdebug on\n')
      return
      
    def RestartAP(self):
      if self.loggedin_tn == True:
        self.tn.write(b'killall -9 hostapd\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'ifconfig wlan0 down\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'ifconfig wlan1 down\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'rmmod mtlk.ko\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'rmmod mtlkroot.ko\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'insmod /tmp/test/mtlkroot.ko\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'insmod /tmp/test/mtlk.ko\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'/tmp/wlan_wave/fapi_wlan_wave_runner.sh &\n')
        self.tn.read_until(self.shell_prompt)
        self.log_write('\tAP restarted!\n')
      return
    
    def dmesg(self):
      if self.loggedin_tn == True:
        self.tn.write(b'\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'dmesg > /tmp/dmesg.log\n')
        self.tn.read_until(self.shell_prompt)
        self.log_write('\tdone\n')
      return
    
    def rmmod(self):
      if self.loggedin_tn == True:
        self.log_write('t\started\n')
        self.tn.write(b'\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'rmmod mtlk.ko\n')
        self.tn.read_until(self.shell_prompt)
        self.log_write('\tdone\n')
      else:
        self.log_write('\tnot logged in\n')
      return
    
    def insmod(self):
      if self.loggedin_tn == True:
        self.log_write('t\started\n')
        self.tn.write(b'\n')
        self.tn.read_until(self.shell_prompt)
        self.tn.write(b'insmod mtlk.ko\n')
        self.tn.read_until(self.shell_prompt)
        self.log_write('\tdone\n')
      else:
        self.log_write('\tnot logged in\n')
      return

