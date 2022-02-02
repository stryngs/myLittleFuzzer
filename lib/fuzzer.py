import binascii
import os
import time
import traceback
import sys
from easyThread import Backgrounder
from scapy.all import *

class Fuzzer(object):
    def __init__(self, py):
        self.py = py
        self.inputFile = None
        self.genOnly = None
        self.vCheck = None

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


    def fuzzRdr(self, fName = 'hex.log'):
        print('Reading hex ++ creating list of fuzzed packets to send')
        hexList = []
        with open(fName) as iFile:
            hexLines = iFile.read().splitlines()
        for hex in hexLines:
            hexList.append(IP(binascii.unhexlify(hex)))
        print(int(time.time() - self.start), 'seconds of processing, give or take')
        return hexLines, hexList


    def fuzzStb(self):
        """The list is volatile, so call and store the return via hex.log"""
        self.fuzzList = [i for i in self.fuzzDict.values()]
        print(int(time.time() - self.start), 'seconds of processing, give or take')
        print('Storing hex')
        with open('hex.log', 'w') as oFile:
            for fuzz in self.fuzzList:
                oFile.write(hexstr(fuzz, onlyhex = 1).replace(' ', '') + '\n')
        print(int(time.time() - self.start), 'seconds of processing, give or take')

    def pingThread(self):
        os.system('ping -D {0} 2>&1 > ping.log'.format(self.py.tgtIP))

    def main(self, py):
        fuzzHits = {}
        count = 0


        self.fuzzDict = {}
        fuzzCounter = 0

        if self.inputFile is None and self.genOnly is True:
            print('Generating fuzz')
            for f in self.fuzzGen(self.py.fCount):
                self.fuzzDict.update({fuzzCounter: f})
                fuzzCounter += 1
            self.fuzzStb()

            ## Exit here if generate only
            if self.genOnly is True:
                self.py.con.close()
                return

        ## Stable object in memory now
        self.hexLines, self.hexList = self.fuzzRdr()

        ## Map the intended trail
        if self.inputFile is None:
            print('Storing hex to sql')
            for hex in self.hexLines:
                py.db.execute("""
                              INSERT INTO hex(rd, value) VALUES(?, ?);
                              """, (py.ride, hex)
                              )
            py.con.commit()

            ## Eyeball it
            print('Storing summary to sql')
            for hex in self.hexLines:
                thePkt = IP(binascii.unhexlify(hex.replace(' ', '')))
                py.db.execute("""
                              INSERT INTO sum(rd, value) VALUES(?, ?);
                              """, (py.ride, thePkt.summary(),)
                              )
            py.con.commit()
            print(int(time.time() - self.start), 'seconds of processing, give or take')


        ## Scout from the hills
        if self.inputFile is None and self.genOnly is None:
            print('Backgrounding ping')
            Backgrounder.theThread = self.pingThread
            bg = Backgrounder()
            bg.easyLaunch()
        sTime = time.time()
        if self.inputFile is None and self.genOnly is None:
            self.fuzzList = self.hexList
        print('Sending', len(self.fuzzList), 'packets')
        py.biteStart = time.time()
        try:
            if py.vCheck is False:
                send(self.fuzzList, iface = self.py.iFace, inter = self.py.iVal, realtime = True, verbose = False)
            else:
                send(self.fuzzList, iface = self.py.iFace, inter = self.py.iVal, realtime = True, verbose = True)
        except Exception as E:
            print(traceback.format_exc())
            # print(E)
            pass
        eTime = time.time()
        py.biteEnd = eTime

        ## pwnie is thirsty again
        if self.inputFile is None:
            print('Killing ping')
            os.system('killall -9 ping')
        runTime = eTime - sTime
        runCnt = str(runTime).split('.')[0]
        runDec = str(runTime).split('.')[1][0:3]
        print(len(self.fuzzList), 'packets fuzzed in', '.'.join([runCnt, runDec]), 'seconds')
