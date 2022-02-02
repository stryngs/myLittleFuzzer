import argparse
import sqlite3 as lite

class Corral(object):
    """Saddle a pwnie"""

    def __init__(self):
        self.con = lite.connect('saddle.sqlite3')
        self.db = self.con.cursor()
        self.saddleCheck()
        self.con.commit()
        self.inputFile = None
        self.genOnly = None


    def menu(self):
        parser = argparse.ArgumentParser(description = 'myLittleFuzzer')
        group = parser.add_mutually_exclusive_group(required = True)
        group.add_argument('--file',
                           help = 'Read from a file instead of generating fuzz')
        group.add_argument('--gen',
                           action = 'store_true',
                           help = 'Generate a stream of fuzz for usage later')
        group.add_argument('--run',
                           action = 'store_true',
                           help = 'Generate and send fuzz')
        parser.add_argument('-i',
                            help = 'Interface')
        parser.add_argument('-p',
                            help = 'Target Port')
        parser.add_argument('-q',
                            help = 'Quantity of packets fuzzed')
        parser.add_argument('-s',
                             help = 'CIDR source range')
        parser.add_argument('-t',
                            help = 'Target IP')
        parser.add_argument('-v',
                            action = 'store_true',
                            help = 'Verbosity')
        parser.add_argument('-w',
                            help = 'Wait between injects')
        return parser


    def saddleCheck(self):
        """Prep the tables"""

        ## Holds the calculated hex
        self.db.execute("""
                        CREATE TABLE IF NOT EXISTS
                        hex(id INTEGER PRIMARY KEY AUTOINCREMENT, rd INTEGER, value TEXT);
                        """)

        ## Holds the ping logs
        self.db.execute("""
                        CREATE TABLE IF NOT EXISTS
                        png(id INTEGER PRIMARY KEY AUTOINCREMENT, rd INTEGER, value TEXT);
                        """)

        ## Holds the summary logs
        self.db.execute("""
                        CREATE TABLE IF NOT EXISTS
                        sum(id INTEGER PRIMARY KEY AUTOINCREMENT, rd INTEGER, value TEXT);
                        """)

        ## Guide future hex based on the bridle
        self.db.execute("""
                        CREATE TABLE IF NOT EXISTS
                        brd(rd INTEGER PRIMARY KEY, start INTEGER, end INTEGER, span INTEGER);
                        """)
