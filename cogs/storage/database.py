import pymysql
import configparser

from environment import Environment

class Database(object):
	def __init__(self):
		env = Environment()
		self.config = env.get_config()

	def connectToDatabase(self):
		return pymysql.connect(host=self.config.get("Database","Host"),
						   user=self.config.get("Database","User"),
						   password=self.config.get("Database","Password"),
						   db=self.config.get("Database","Database"),
						   charset='utf8mb4',
						   cursorclass=pymysql.cursors.DictCursor)

	def query(self,query,args = None):
		connection = self.connectToDatabase()

		with connection.cursor() as cursor:
			cursor.execute(query,args)

			connection.commit()
			connection.close()

			return cursor
