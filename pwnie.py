#!/usr/bin/python3

import argparse
import binascii
import os
import signal
import sys
import time
from lib.corral import Corral
from lib.fuzzer import Fuzzer
from easyThread import Backgrounder
from scapy.all import *

def signal_handler(signal, frame):
    if args.gen is not None:
        print('Killing ping')
        os.system('killall -q -9 ping')
    print('Closing the corral')
    py.con.commit()
    py.con.close()
    sys.exit(1)


def main(fz, py):
    try:
        signal.signal(signal.SIGINT, signal_handler)
        fz.main(py)

        if fz.inputFile is None and fz.genOnly is None:
            py.con.commit()
            print('Sleeping for 5 seconds to baseline ping')
            time.sleep(5)
            print('Killing ping')
            os.system('killall -q -9 ping')

        if fz.inputFile is None and fz.genOnly is None:
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

        # fs cleanup
        try:
            py.con.commit()
            py.con.close()
        except:
            pass
        if fz.inputFile is None and fz.genOnly is None:
            print('Pruning logs')
            try:
                os.remove('hex.log')
                os.remove('ping.log')
            except:
                pass
    except Exception as E:
        print(traceback.format_exc())
        # print(E)


## Mount up
if __name__ == '__main__':
    py = Corral()
    fz = Fuzzer(py)
    args = py.menu().parse_args()
    fz.start = time.time()

    ## Read from an existing file and send
    if args.file is not None:
        if args.w and args.i:
            fz.inputFile = True
            fz.hexLines, fz.hexList = fz.fuzzRdr(args.file)
            fz.fuzzList = fz.hexList
        else:
            print('Required args for --file:\n -i\n -w')
            sys.exit(1)

    ## Generate only
    if args.gen is True:
        if args.q and args.s and args.t:
            fz.genOnly = True
        else:
            print('Requred args for --gen:\n -q\n -s\n -t')
            sys.exit(1)

    ## Generate and send
    if args.file is None and args.gen is False:

        ### DEBUG
        ### Play with None combinations for fuzz() outcomes
        if args.i and args.w and args.t and args.s:


            try:
                tVal = int(args.q) * float(args.w)
                cVal = 'seconds'
                if tVal > 300:
                    tVal = tVal / 60
                    cVal = 'minutes'
            except:
                pass

            ## Run and send

            if args.gen is False:
                uAcc = input('Estimated time for fuzz is {0} {1}\n Shall we proceed? [Y/n]\n '.format(tVal, cVal))
                if uAcc.lower() == 'y' or uAcc == '':

                    ## Pick your stall and saddle up
                    py.db.execute("""SELECT rd FROM brd ORDER BY 1 DESC;""")
                    rodeo = [i for i in py.db.fetchall()]
                    if len(rodeo) > 0:
                        py.ride = rodeo[0][0]
                        py.ride += 1
                    else:
                        py.ride = 0

                else:
                    print(' Exiting\n')
        else:
            print('Requred args for --run:\n -i\n -q\n -s\n -t\n -w')
            sys.exit(1)

    ## Where to
    py.tgtIP = args.t
    py.srcCIDR = args.s
    py.vCheck = args.v
    py.iFace = args.i
    try:
        py.iVal = float(args.w)
    except:
        pass
    try:
        py.fCount = int(args.q)
    except:
        pass
    try:
        py.port = int(args.p)
    except:
        py.port = args.p

    ## Giddyup
    main(fz, py)
