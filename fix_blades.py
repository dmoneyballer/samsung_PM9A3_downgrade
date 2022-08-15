#!/usr/bin/env python
import re, os, time, subprocess
from colorama import Fore, init, Style
# blade_sessions = {}
def deColorize( coloredStr ):
    """ Remove color encoding in string """
    deColorizedStr = re.sub( '\\x1b\[\d{1,2}m', '', coloredStr )
    deColorizedStr = re.sub( '\\033\[\d{1,2}m', '', deColorizedStr )
    return deColorizedStr

patterns =  [
    "\s* ([^GDC5602Q]+\/\d\%) GDC5602Q",
    "\s* ([^GDC5502Q]+\/\d\%) GDC5502Q",
    "\s* ([^EDA5502Q]+\/\d\%) EDA5502Q",
    ]
output = subprocess.Popen('ybcli blade status > /tmp/blades', shell=True)
output.wait()
with open('/tmp/blades', 'r') as rf:
    output=deColorize(rf.read())
    output =output.replace('\n', '')
    output =output.replace('\r', '')
for pattern in patterns:
    pat = re.compile('Blade\s+Bay:\s+(\d+)\s+->\s+YBOS READY UUID:\s\d+-\d+-\d+-\d+-[\dA-Z]+ - Version: YBOS-\d+\.\d+\.\d+-\d+-DEBUG\s+BIOS:\s+[A-Za-z_\d\.]+\s+-\s+Memory total\/free: \d+\/\d+ KiB - IB-FW: \d+\.\d+\.\d+\s+BMC: \d+\.\d+\.\d+\s-\sKalidah-\d+: [A-Za-z\d]+\s-\s+Kalidah-\d+: [A-Za-z\d]+\s+CPU:\sAMD\sEPYC\s[\dA-Z]+\s\d+-Core Processor - Microcode: [\dA-Za-z]+ - Cores: \d+ - Load:\s+\d%\s+Address:\s(\d\d\d\.\d\d\d\.\d\d\.\d\d) - Uptime: [\dA-Z]+\s[\dA-Za-z(),]+\s\d+:\d+:\d+ - Worker: Running\s+Encryption Supported: YES - Encryption Enabled:\s[A-Za-z\d]+ - locked:\sN\/A\s+SSD: \d: [A-Za-z\d]+\s+\d: [A-Za-z\d]+\s+\d: [A-Za-z\d]+\s+\d: [A-Za-z\d]+'+pattern)
    bad_blades =re.findall(pat, output)
    if bad_blades:
        print(bad_blades, pattern)
        # exit(0)
        for blade in bad_blades:
            # with ips do a /ybd/nvme-load
            out = subprocess.Popen('ssh root@{} -t "/ybd/nvme-load"'.format(blade[1]), shell=True)
            print('ip is', blade[1])
        # wait 2 minutes for nvmes to load
        print('waiting 2 minutes')
        time.sleep(120)
        tasks = []
        for blade in bad_blades:
            # scp files over to blade's /tmp dir
            out = subprocess.Popen('scp -r /tmp/samsung_PM9A3_downgrade/ root@{}:/tmp'.format(blade[1]), shell=True)
            out.wait()
            # run the downgrade
            print('ssh root@{} -t "/tmp/samsung_PM9A3_downgrade/downgrade_samsung_GDC5602Q_to_GDC5302Q.sh"'.format(blade[1]))
            out = subprocess.Popen('ssh root@{} -t "/tmp/samsung_PM9A3_downgrade/downgrade_samsung_GDC5602Q_to_GDC5302Q.sh"'.format(blade[1]), shell=True)
            tasks.append(out)
        for task in tasks:
            task.wait()
        # time.sleep(300)
        # wait 5 minutes for process to complete
        output = subprocess.Popen('ybcli blade reset all', shell=True)
        output.wait()
        # wait 5 mins for blades to reset
        time.sleep(300)
        break



