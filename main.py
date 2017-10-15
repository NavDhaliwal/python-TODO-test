"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
"""
from docopt import docopt
import subprocess
import os,sys

from alayatodo import app


def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError as ex:
        print (ex.output)
        os.exit(1)

def addTODOstatus():
    _run_sql('resources/addTODOstatus.sql')
    print ("AlayaTodo: Database altered. TODO status Column added.")

if __name__ == '__main__':
    args = docopt(__doc__)
    #print (app.config['DATABASE'])
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/fixtures.sql')
        print ("AlayaTodo: Database initialized.")
        addTODOstatus()
    else:
        app.run(use_reloader=True)
