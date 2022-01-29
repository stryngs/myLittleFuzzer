import sqlite3 as lite

class Corral(object):
    """Saddle a pwnie"""

    def __init__(self):
        self.con = lite.connect('saddle.sqlite3')
        self.db = self.con.cursor()
        self.saddleCheck()
        self.con.commit()


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


if __name__ == '__main__':

    ## Save a horse, ride a pwnie
    py = Corral()
