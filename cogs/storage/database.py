import pymysql

class Database(object):
	DATABASE_HOST = 'discord.crtejrmgafyl.us-east-1.rds.amazonaws.com'
	DATABASE_PASS = 'ImABot12'
	DATABASE_USER = 'lewis'
	DATABASE_DATA = 'discord'
	
	def __init__(self):
		self.something = "something"
		
	def connectToDatabase(this):
		return pymysql.connect(host=this.DATABASE_HOST,
						   user=this.DATABASE_USER,
						   password=this.DATABASE_PASS,
						   db=this.DATABASE_DATA,
						   charset='utf8mb4',
						   cursorclass=pymysql.cursors.DictCursor)
		
	def query(this,query,args):
		connection = this.connectToDatabase()
		
		with connection.cursor() as cursor:
			cursor.execute(query,args)
				
			connection.commit()
			connection.close()
			
			return cursor