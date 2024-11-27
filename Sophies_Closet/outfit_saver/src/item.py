import ui
import sqlite3

from clothing_unit import Clothing_Unit

#To get the preview, get the preview saved in the view second from the top.
#Will this always be affective?
#We can make sure it is always affective by calling at the right time

#id: Necessary for retrieving all data related to this Outfit
#view: Necessary for
#outfit_saver: Necessary for calling Nav stuff

class Item(Clothing_Unit):
	def __init__(self, id, params, view, outfit_saver):
		self.type = "item"
		self.link_type = "outfit"
		super().__init__(id, view, outfit_saver)
		
	#Called from:
	#	Clothing_Unit.__init__()
	def get_sql_data(self):
		if self.id == None:
			return "NEW CLOTHING ITEM", 5, ""
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		sql = '''
		SELECT
			"item_name",
			"item_score",
			"item_note"
		FROM "items"
		WHERE item_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		data = cursor.fetchall()[0]
		conn.close()
		return data[0], data[1], data[2]

	#Called from:
	#	self.choose_image()
	#	self.choose_link()
	#	self.choose_category()
	#	self.save_note()
	#	self.save_score()
	#	self.save_title()
	def create(self):
		print("hi")
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "items" (
			"item_name",
			"item_score",
			"item_note"
			)
		VALUES (
			"{}",
			"{}",
			"{}"
			)
		'''.format(self.title, self.score, self.note)
		
		print("hi again")
		result = cursor.execute(sql)
		conn.commit()
		
		sql='''
			select seq from sqlite_sequence where name="items"
			'''
		cursor.execute(sql)
		last_row=cursor.fetchall()
		self.id = str(last_row[0][0])
		
		
		if self.category.id == None:
			self.category.save_category(self.category.name, self.category.photo_path)
		
		
		sql='''
		INSERT INTO "category_items" (
			"category_id",
			"item_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(self.category.id, self.id)
		cursor.execute(sql)
		conn.commit()
		conn.close()
		
	
	#Called from:
	#	self.prompt_delete()
	def delete(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		DELETE FROM "items"
		WHERE "item_id" = "{}"
		'''.format(self.id)
		result = cursor.execute(sql)
		
		sql = '''
		DELETE FROM "category_items"
		WHERE "item_id" = "{}"
		'''.format(self.id)
		cursor.execute(sql)
		
		sql = '''
		DELETE FROM "outfit_items"
		WHERE "item_id" = "{}"
		'''.format(self.id)
		cursor.execute(sql)
		
		sql = '''
		DELETE FROM "item_images"
		WHERE "item_id" = "{}"
		'''.format(self.id)
		cursor.execute(sql)
		
		conn.commit()
		conn.close()
			
	def add_image(self):
		self.outfit_saver.nav.push_view("image_selector", "item", (self.view.choose_image, ""))
			
	def remove_image(self, image_id):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "item_images"
		WHERE item_image_id = "{}" AND item_id = "{}"
		""".format(image_id, self.id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
	def add_link(self):
		search_query = """
		SELECT outfit_id, outfit_name
		FROM outfits
		WHERE outfit_name LIKE 
		"""
		image_query = """
		SELECT outfit_image_id
		FROM outfit_images
		WHERE outfit_id=
		"""
		self.outfit_saver.nav.push_view("search", "outfits", ("Search Outfits", search_query, image_query, "outfit_thumbnails", self.view.choose_link, self.view.background_color))
			
	def remove_link(self, link_id):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "outfit_items"
		WHERE outfit_id = "{}" AND item_id = "{}"
		""".format(link_id, self.id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
	def add_category(self):
		search_query = """
		SELECT category_id, category_name, photo_path
		FROM item_categories
		WHERE category_name LIKE 
		"""
		image_query = ""
		self.outfit_saver.nav.push_view("search", "ic", ("Search Item Categories", search_query, image_query, "background_thumbnails", self.view.choose_category, self.view.background_color))
			
	def remove_category(self, category_id):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_items"
		WHERE item_id = "{}" AND category_id = "{}"
		""".format(self.id, category_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		
	def save_note(self):
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "items" 
			SET
				item_note="{}"
			WHERE item_id="{}"
			'''.format(self.note, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
		
	def save_score(self, new_score):
		self.score = new_score
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "items" 
			SET
				item_score="{}"
			WHERE item_id="{}"
			'''.format(self.score, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
		
	def save_title(self, new_title):
		self.title = new_title
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "items" 
			SET
				item_name="{}"
			WHERE item_id="{}"
			'''.format(self.title, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
