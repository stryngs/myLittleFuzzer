import binascii
import os
import time
import traceback
from easyThread import Backgrounder
from scapy.all import *

class Fuzzer(object):
    def __init__(self, py):
        self.py = py

    def fuzzMaker(self):
        if self.py.port is None:
            frm = IP(dst = self.py.tgtIP, src = RandIP(self.py.srcCIDR))/TCP()
        else:
            frm = IP(dst = self.py.tgtIP, src = RandIP(self.py.srcCIDR))/TCP(dport = self.py.port)
        return fuzz(frm)


    def fuzzGen(self, i):
        fSet = []
        for fuzz in range(i):
            ourScp = self.fuzzMaker()
            fSet.append(ourScp)
        return fSet

    def pingThread(self):
        os.system('ping -D {0} 2>&1 > ping.log'.format(self.py.tgtIP))

    def main(self, py):
        fuzzHits = {}
        count = 0
        start = time.time()

        fuzzDict = {}
        fuzzCounter = 0

        print('Generating fuzz')
        for f in self.fuzzGen(self.py.fCount):
            fuzzDict.update({fuzzCounter: f})
            fuzzCounter += 1

        ## This list is volatile, so call and store the return via hex.log
        fuzzList = [i for i in fuzzDict.values()]
        self.fuzzList = fuzzList
        print(int(time.time() - start), 'seconds of processing, give or take')
        print('Storing hex')
        with open('hex.log', 'w') as oFile:
            for fuzz in fuzzList:
                oFile.write(hexstr(fuzz, onlyhex = 1) + '\n')
        print(int(time.time() - start), 'seconds of processing, give or take')

        ## Stable object in memory now
        print('Reading hex ++ creating list of fuzzed packets to send')
        hexList = []
        with open('hex.log') as iFile:
            hexLines = iFile.read().splitlines()
        for hex in hexLines:
            hexList.append(IP(binascii.unhexlify(hex.replace(' ', ''))))
        print(int(time.time() - start), 'seconds of processing, give or take')

        ## Map the intended trail
        print('Storing hex to sql')
        for hex in hexLines:
            py.db.execute("""
                          INSERT INTO hex(rd, value) VALUES(?, ?);
                          """, (py.ride, hex)
                          )
        py.con.commit()

        ## Eyeball it
        print('Storing summary to sql')
        for hex in hexLines:
            thePkt = IP(binascii.unhexlify(hex.replace(' ', '')))
            py.db.execute("""
                          INSERT INTO sum(rd, value) VALUES(?, ?);
                          """, (py.ride, thePkt.summary(),)
                          )
        py.con.commit()
        print(int(time.time() - start), 'seconds of processing, give or take')

        ## Scout from the hills
        print('Backgrounding ping')
        Backgrounder.theThread = self.pingThread
        bg = Backgrounder()
        bg.easyLaunch()
        sTime = time.time()
        print('Sending', len(fuzzList), 'packets')
        py.biteStart = time.time()
        try:
            if py.vCheck is None:
                send(fuzzList, iface = self.py.iFace, inter = self.py.iVal, realtime = True, verbose = False)
            else:
                send(fuzzList, iface = self.py.iFace, inter = self.py.iVal, realtime = True, verbose = True)
        except Exception as E:
            print(traceback.format_exc())
        eTime = time.time()
        py.biteEnd = eTime

        ## pwnie is thirsty again
        print('Killing ping')
        os.system('killall -9 ping')
        runTime = eTime - sTime
        runCnt = str(runTime).split('.')[0]
        runDec = str(runTime).split('.')[1][0:3]
        print(len(fuzzList), 'packets fuzzed in', '.'.join([runCnt, runDec]), 'seconds')
