from peewee import MySQLDatabase
from environment import Environment

class DatabaseFactory:
	def __init__(self):
		env = Environment()
		self.config = env.get_config()

		self._database = None

	def get_database_connection(self):
		if None == self._database:
			self._database = MySQLDatabase(self.config.get("Database","Database"),
			host     = self.config.get("Database","Host"),
			user     = self.config.get("Database","User"),
			password = self.config.get("Database","Password"),
			charset  = 'utf8mb4')

		return self._database
