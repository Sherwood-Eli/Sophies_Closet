import ui
import sqlite3
import math


from buttons import Add_Button, Back_Button, Search_Button, Remove_Button, Small_Remove_Button, Title_Button

class Category_Viewer:
	def __init__(self, model_id, view, outfit_saver):
		self.id = model_id
		self.outfit_saver = outfit_saver
		self.view = view
		self.categories = self.load_categories()
	
	def load_categories(self):
		#Retrieving data
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		sql = '''
		SELECT * FROM "{}"
		'''.format(self.table_name)
		cursor.execute(sql)
		categories = cursor.fetchall()
		conn.close()
		return categories
