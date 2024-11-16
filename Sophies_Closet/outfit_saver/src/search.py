import ui
import os
import sqlite3
import math

from buttons import Back_Button, Title_Button

class Search:
	def __init__(self, id, params, view, outfit_saver):
		self.id = id
		self.view = view
		self.outfit_saver = outfit_saver
		
		self.search_query = params[1]
		self.image_query = params[2]
		self.image_directory = params[3]
		
	
	def search(self, search_string):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		{}"{}%"
		'''.format(self.search_query, search_string)
		cursor.execute(sql+" LIMIT 20")
		rows = cursor.fetchall()
		data = []
		
		if len(rows) > 0:
			if self.image_directory == "":
				pass
				
			elif self.image_directory == "background_thumbnails":
				#for categories
				os.chdir("../images/"+self.image_directory)
				for row in rows:
					id, name, image_id = row
					data.append((id, self.get_image(image_id), name))
				os.chdir("../../src")
						
			else:
				#for items and outfits
				os.chdir("../images/"+self.image_directory)
				for row in rows:
					id = row[0]
					name = row[1]
					
					sql = '''
					{}"{}"
					'''.format(self.image_query, id)
					cursor.execute(sql)
					rows = cursor.fetchall()
					
					#just get the first one for each
					if len(rows) > 0:
						image_id = str(rows[0][0])
					else:
						image_id = "0"
					data.append((id, self.get_image(image_id), name))
				os.chdir("../../src")
		
		conn.close()
			
		return data
		
	
	def get_image(self, image_id):
		if image_id != "0":
			return ui.Image.named(image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		else:
			return None
		
	
	def show_warning(self, message):
		print(message)
		
