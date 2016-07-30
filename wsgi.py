#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#

from flaskapp import app as application

#
# Below for testing only
#

if __name__ == "__main__":
	application.run(debug=True)