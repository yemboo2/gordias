# __main__.py
# gordias
# By Markus Ehringer
# Date: 29.03.2018

import api
import db
import sys
from bottle import run
import sync
import threading

def main():
	try:
		threading.Thread(target=run, kwargs=dict(host='localhost', port=8080)).start() # Run API
		sync.start_sync()
	except:
		print("Unexpected error: {0}", sys.exc_info()[0])
	finally:
		db.close_connection()	
		import notnull
		notnull.dump_matrices()

if __name__ == "__main__":
    main()
    