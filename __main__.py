# __main__.py
# gordias
# By Markus Ehringer
# Date: 20.03.2018

import api
import db

def main():
	api.start()

if __name__ == "__main__":
    # execute only if run as a script
    main()
    db.close_connection()