import sqlite3

class DBHandler:
	def connect(self):
		self.conn = sqlite3.connect("db.sqlite3")
		self.cursor = self.conn.cursor()

	def create_table(self):
		self.cursor.execute(
			"""CREATE TABLE IF NOT EXISTS netlimits (
			network			CHAR(18)	PRIMARY KEY UNIQUE,
			last_request	REAL		NOT NULL,
			requests		INTEGER		NOT NULL,
			banned_since	REAL
			)
		""")

	def insert_new_network(self, network, last_request, requests, banned_since):
		sql = f"""
			INSERT INTO netlimits VALUES (
				'{network}',
				'{last_request}',
				'{requests}',
				'{banned_since}'
			)
		"""
		self.cursor.execute(sql)
		self.conn.commit()

	def update_banned_since(self, network, banned_since):
		sql = f"""
			UPDATE netlimits 
			SET banned_since = '{banned_since}'
			WHERE network = '{network}'
		"""
		self.cursor.execute(sql)
		self.conn.commit()

	def update_rate_limiter_all(self, network, last_request, requests):
		sql = f"""
			UPDATE netlimits 
			SET last_request = '{last_request}',
				requests = '{requests}'
			WHERE network = '{network}'
		"""
		self.cursor.execute(sql)
		self.conn.commit()

	def select(self, network, column):
		sql = f'''SELECT {column}
			FROM netlimits
			WHERE network = '{network}'
			'''
		self.cursor.execute(sql)
		response = self.cursor.fetchone()
		if response:
			return response[0]
		return response

	def delete(self, network):
		sql = f'''DELETE FROM netlimits
			WHERE network = '{network}'
			'''
		self.cursor.execute(sql)

	def disconnect(self):
		self.cursor.close()
		self.conn.close()