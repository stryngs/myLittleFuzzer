#!/usr/bin/python3

import binascii
import os
import signal
import sys
import time
from easyThread import Backgrounder
from scapy.all import *

class Fuzzer(object):
    def __init__(self, tgtIP, srcCIDR, fCount, vCheck, iVal):
        self.tgtIP = tgtIP
        self.srcCIDR = srcCIDR
        self.fCount = fCount
        self.iVal = iVal
        if vCheck is None:
            self.vCheck = None
        else:
            self.vCheck = True

    def fuzzMaker(self):
        return fuzz(IP(dst = self.tgtIP, src = RandIP(self.srcCIDR)))
        (TCP(dport = 80))

    def fuzzGen(self, i):
        fSet = []
        for fuzz in range(i):
            ourScp = self.fuzzMaker()
            fSet.append(ourScp)
        return fSet

    def pingThread(self):
        os.system('ping -D {0} 2>&1 > ping.log'.format(self.tgtIP))

    def main(self):
        fuzzHits = {}
        count = 0
        start = time.time()

        fuzzDict = {}
        fuzzCounter = 0
        print('Generating fuzz')
        for f in self.fuzzGen(self.fCount):
            fuzzDict.update({fuzzCounter: f})
            fuzzCounter += 1
        fuzzList = [i for i in fuzzDict.values()]
        print(int(time.time() - start), 'seconds of processing, give or take')

        print('Storing hex')
        with open('hex.log', 'w') as oFile:
            for fuzz in fuzzList:
                oFile.write(hexstr(fuzz, onlyhex = 1) + '\n')
        print(int(time.time() - start), 'seconds of processing, give or take')

        print('Creating list of fuzzed packets to send')
        hexList = []
        with open('hex.log') as iFile:
            hexLines = iFile.read().splitlines()
        for hex in hexLines:
            hexList.append(IP(binascii.unhexlify(hex.replace(' ', ''))))
        print(int(time.time() - start), 'seconds of processing, give or take')

        print('Storing summary')
        with open('summary.log', 'w') as oFile:
            for hex in hexLines:
                thePkt = IP(binascii.unhexlify(hex.replace(' ', '')))
                oFile.write(thePkt.summary() + '\n')
        print(int(time.time() - start), 'seconds of processing, give or take')

        print('Backgrounding ping')
        Backgrounder.theThread = self.pingThread
        bg = Backgrounder()
        bg.easyLaunch()
        sTime = time.time()

        print('Sending', len(fuzzList), 'packets')
        try:
            if self.vCheck is None:
                send(fuzzList, iface = 'wlan0', inter = self.iVal, realtime = True, verbose = False)
            else:
                send(fuzzList, iface = 'wlan0', inter = self.iVal, realtime = True, verbose = True)
        except Exception as E:
            print(E)
        eTime = time.time()

        print('Killing ping')
        os.system('killall -9 ping')
        runTime = eTime - sTime
        runCnt = str(runTime).split('.')[0]
        runDec = str(runTime).split('.')[1][0:3]
        print(len(fuzzList), 'packets fuzzed in', '.'.join([runCnt, runDec]), 'seconds')

def signal_handler(signal, frame):
    cTime = time.time() - start
    runCnt = str(cTime).split('.')[0]
    runDec = str(cTime).split('.')[1][0:3]
    print('Cancelled run lasted', '.'.join([runCnt, runDec]), 'seconds')
    os.system('killall -q -9 ping')
    sys.exit(0)

if __name__ == '__main__':
    try:
        tgtIP = sys.argv[1]
        srcCIDR = sys.argv[2]
        fCount = int(sys.argv[3])
        iVal = float(sys.argv[4])
        try:
            vCheck = int(sys.argv[5])
        except:
            vCheck = None
        signal.signal(signal.SIGINT, signal_handler)
        sh = Fuzzer(tgtIP, srcCIDR, fCount, vCheck, iVal)
        sh.main()
    except:
        print('\n\n./pwnie.py <target ip> <source cidr> <fuzzed packet count> <interval>')
        print(' -i.e.')
        print('  ./pwnie.py 192.168.100.1 192.167.100.0/27 25 .0001')
        print('  ./pwnie.py 192.168.100.1 192.167.100.0/27 25 .4 1 << for verbose')
        print('    [!] Avoid verbosity for high number packet count')
