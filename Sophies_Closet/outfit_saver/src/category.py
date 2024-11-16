import ui
import photos
import sqlite3
import math

from buttons import Add_Button, Back_Button, Title_Button, Image_Button, Title_Edit_Field, Remove_Button, Small_Remove_Button

class Category:
	def __init__(self, model_id, view, outfit_saver):
		self.id = model_id
		self.view = view
		self.outfit_saver = outfit_saver
		
		self.name, self.photo_path = self.load_category()
				
	def save_category(self, name, photo_path):
		self.name = name
		self.photo_path = photo_path
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		if self.id == None:
			#insert into table
			sql = '''
			INSERT INTO "{}" (
				"category_name",
				"photo_path")
			VALUES (
				"{}",
				"{}")
			'''.format(self.table_name, self.name, self.photo_path)
			
			
			cursor.execute(sql)
			conn.commit()
			sql='''
			select seq from sqlite_sequence where name="{}"
			'''.format(self.table_name)
			cursor.execute(sql)
			last_row=cursor.fetchall()
			self.id = str(last_row[0][0])
		else:
			sql = '''
			UPDATE "{}" 
			SET
				category_name="{}",
				"photo_path"="{}"
			WHERE category_id="{}"
			'''.format(self.table_name, self.name, self.photo_path, self.id)
			cursor.execute(sql)
			conn.commit()
			
		conn.close()
		
	def load_category(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		sql = '''
		SELECT * FROM "{}"
		WHERE category_id = "{}"
		'''.format(self.table_name, self.id)
		cursor.execute(sql)
		data = cursor.fetchall()
		conn.close()
		return data[0][1], data[0][2]
	
	#TODO update score on icon if i end up putting it on there in the first place
	def update_icon(self, icon_id, title, score):
		if icon_id in self.icons:
			icon = self.icons[icon_id]
			self.scroll_view.remove_subview(icon.button)
			
			frame = icon.button.frame
			clothing_unit = (icon_id, title)
			self.icons[icon_id] = Icon(clothing_unit, lambda x:frame, self.image_type, self.icon_button_pressed)
			self.scroll_view.add_subview(self.icons[icon_id].button)
		else:
			clothing_unit = (icon_id, title)
			self.icons[icon_id] = Icon(clothing_unit, self.next_icon_frame, self.image_type, self.icon_button_pressed)
			self.scroll_view.add_subview(self.icons[icon_id].button)
			
			
	def change_background_image(self):
		self.outfit_saver.nav.push_view("image_selector", self.image_type[0]+"c", (self.view.choose_background_image, self.photo_path))
			
	
			
	
