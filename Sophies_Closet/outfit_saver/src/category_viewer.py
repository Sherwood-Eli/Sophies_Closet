import ui
import sqlite3
import math


from buttons import Add_Button, Back_Button, Search_Button, Remove_Button, Small_Remove_Button, Title_Button
from icon import Icon
from warning_view import Warning_View

class Category_Viewer:
	def __init__(self, outfit_saver):
		self.outfit_saver = outfit_saver
		
	
	def load_categories():
		#Retrieving data
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		sql = '''
		SELECT * FROM "{}"
		'''.format(this.table_name)
		cursor.execute(sql)
		categories = cursor.fetchall()
		conn.close()
		return categories
