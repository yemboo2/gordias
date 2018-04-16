# __main__.py
# gordias
# By Markus Ehringer
# Date: 16.04.2018

import sys
import sync
import threading
import api
import database
import notnull
import logging
from bottle import run

def main():
	logging.info("Gordias started")
	try:
		threading.Thread(target=run, kwargs=dict(host='0.0.0.0', port=8080)).start() # Run API
		sync.start_sync()
	except:
		logging.error("Unexpected error: {0}", sys.exc_info()[0])
	finally:
		database.close_connection()	
		notnull.dump_matrices()

if __name__ == "__main__":
    main()
