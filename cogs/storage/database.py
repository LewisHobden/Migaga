import pymysql
import configparser

class Database(object):
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read("../../config.ini")

	def connectToDatabase(this):
		return pymysql.connect(host=self.config.get("Database","Host"),
						   user=self.config.get("Database","User"),
						   password=self.config.get("Database","Password"),
						   db=self.config.get("Database","Database"),
						   charset='utf8mb4',
						   cursorclass=pymysql.cursors.DictCursor)

	def query(this,query,args):
		connection = this.connectToDatabase()

		with connection.cursor() as cursor:
			cursor.execute(query,args)

			connection.commit()
			connection.close()

			return cursor
