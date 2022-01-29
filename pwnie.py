#!/usr/bin/python3

import argparse
import binascii
import os
import signal
import sys
import time
import traceback
from lib.corral import Corral
from lib.fuzzer import Fuzzer
from easyThread import Backgrounder
from scapy.all import *

def signal_handler(signal, frame):
    print('Killing ping')
    os.system('killall -q -9 ping')
    print('Closing the corral')
    py.con.commit()
    py.con.close()
    sys.exit(1)


def main(py):
    try:
        signal.signal(signal.SIGINT, signal_handler)
        sh = Fuzzer(py)
        sh.main(py)
        py.con.commit()
        print('Sleeping for 5 seconds to baseline ping')
        time.sleep(5)
        print('Killing ping')
        os.system('killall -q -9 ping')
        print('Storing ping to sql')
        with open('ping.log') as iFile:
            pList = iFile.read().splitlines()
        for p in pList:
            py.db.execute("""
                          INSERT INTO png(rd, value) VALUES(?, ?);
                          """, (py.ride, p)
                          )

        ## Send to the corral
        py.db.execute("""
                      INSERT INTO brd(rd, start, end, span) VALUES(?, ?, ?, ?);
                      """, (py.ride, int(py.biteStart), int(py.biteEnd), int(py.biteEnd - py.biteStart))
                      )
        py.con.commit()
        py.con.close()

        # fs cleanup
        print('Pruning logs')
        try:
            os.remove('hex.log')
            os.remove('ping.log')
        except:
            pass
    except:
        print(traceback.format_exc())


## Mount up
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'myLittleFuzzer')
    parser.add_argument('-i',
                        help = 'Interface',
                        required = True)
    parser.add_argument('-p',
                        help = 'Target Port',
                        required = False)
    parser.add_argument('-q',
                        help = 'Quantity of packets fuzzed',
                        required = True)
    parser.add_argument('-s',
                         help = 'CIDR source range',
                         required = True)
    parser.add_argument('-t',
                        help = 'Target IP',
                        required = True)
    parser.add_argument('-v',
                        help = 'Verbosity',
                        required = False)
    parser.add_argument('-w',
                        help = 'Wait between injects',
                        required = True)
    args = parser.parse_args()
    tVal = int(args.q) * float(args.w)
    cVal = 'seconds'
    if tVal > 300:
        tVal = tVal / 60
        cVal = 'minutes'
    uAcc = input('Estimated time for fuzz is {0} {1}\n Shall we proceed? [Y/n]\n '.format(tVal, cVal))
    if uAcc.lower() == 'y' or uAcc == '':

        ## Pick your stall and saddle up
        py = Corral()
        py.db.execute("""SELECT rd FROM brd ORDER BY 1 DESC;""")
        rodeo = [i for i in py.db.fetchall()]
        if len(rodeo) > 0:
            py.ride = rodeo[0][0]
            py.ride += 1
        else:
            py.ride = 0

        ## Where to
        py.tgtIP = args.t
        py.srcCIDR = args.s
        py.fCount = int(args.q)
        py.iVal = float(args.w)
        py.vCheck = args.v
        py.iFace = args.i
        try:
            py.port = int(args.p)
        except:
            py.port = args.p

        ## Giddyup
        main(py)
    else:
        print(' Exiting\n')
