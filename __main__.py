# __main__.py
# gordias
# By Markus Ehringer
# Date: 08.04.2018

import database
import notnull
import sys
import sync
import threading
import api
from bottle import run

def main():
	try:
		threading.Thread(target=run, kwargs=dict(host='localhost', port=8080)).start() # Run API
		sync.start_sync()
	except:
		print("Unexpected error: {0}", sys.exc_info()[0])
	finally:
		database.close_connection()	
		notnull.dump_matrices()

if __name__ == "__main__":
    main()
    