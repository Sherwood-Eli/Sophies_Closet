import ui
import sqlite3
import os

from buttons import  *
from image_selector import Image_Selector
from clothing_unit import Clothing_Unit
from search_view import Search_View

class Outfit(Clothing_Unit):
	#TODO replace "category" with "caller"
	def __init__(self, id, caller, caller_type, outfit_saver):
		self.type = "outfit"
		self.link_type = "item"
		super().__init__(id, caller, caller_type, outfit_saver)
		self.outfit_saver.outfit_view.load_view(self)
		
	#Called from:
	#	Clothing_Unit.__init__()
	def get_sql_data(self):
		if self.id == None:
			return "NEW OUTFIT", 5, ""
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		sql = '''
		SELECT
			"outfit_name",
			"outfit_score",
			"outfit_note"
		FROM "outfits"
		WHERE outfit_id="{}"
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
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "outfits" (
			"outfit_name",
			"outfit_score",
			"outfit_note"
			)
		VALUES (
			"{}",
			"{}",
			"{}"
			)
		'''.format(self.title, self.score, self.note)
			
		result = cursor.execute(sql)
		conn.commit()
		
		sql='''
			select seq from sqlite_sequence where name="outfits"
			'''
		cursor.execute(sql)
		last_row=cursor.fetchall()
		self.id = str(last_row[0][0])
		
		if self.category.id == None:
			self.category.save_category()
		
		sql='''
		INSERT INTO "category_outfits" (
			"category_id",
			"outfit_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(self.category.id, self.id)
		cursor.execute(sql)
		conn.commit()
		conn.close()
		
		if self.caller_type == "c":
			self.category.update_icon(self.id, self.title, self.score)
		
	#Called from:
	#	self.prompt_delete()
	def delete(self, sender):
		if self.id == None:
			self.close_view(None)
			return
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		DELETE FROM "outfits"
		WHERE "outfit_id" = "{}"
		'''.format(self.id)
		result = cursor.execute(sql)
		
		sql = '''
		DELETE FROM "category_outfits"
		WHERE "outfit_id" = "{}"
		'''.format(self.id)
		cursor.execute(sql)
		
		sql = '''
		DELETE FROM "outfit_items"
		WHERE "outfit_id" = "{}"
		'''.format(self.id)
		cursor.execute(sql)
		
		sql = '''
		DELETE FROM "outfit_images"
		WHERE "outfit_id" = "{}"
		'''.format(self.id)
		cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		if self.caller_type == "c":
			self.category.remove_clothing_unit(self.category.icons[self.id].button)
		elif self.caller_type == "s":
			self.category.search(self.category.text_field.text)
		#TODO remove links when caller is item
		
		self.close_view(None)
		
			
	def add_image(self, sender):
		if not self.remove_mode:
			if self.image_selector != None:
				self.image_selector = Image_Selector("outfit_images", "outfit_thumbnails", "", self.choose_image, self.outfit_saver, False, self.view.background_color)
			self.image_selector.open()
	
	def remove_image(self, sender):
		image_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "outfit_images"
		WHERE outfit_image_id = "{}" AND outfit_id = "{}"
		""".format(image_id, self.id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		if len(self.image_icons) == 5 and "0" not in self.image_icons:
			frame = self.get_next_image_frame()
			self.image_icons["0"] = self.create_add_icon(frame, "", self.add_image, 25)
			self.image_scroll_view.add_subview(self.image_icons["0"])
		
		self.remove_icon(image_id, self.image_remove_buttons, self.image_icons, self.image_scroll_view)
		
		print(self.image_icons)
		if len(self.image_icons) == 1:
			self.image_scroll_view.remove_subview(self.image_icons["0"])
			self.image_icons["0"] = self.create_add_icon(self.image_icons["0"].frame, "No outfit images yet :(", self.add_image, 25)
			self.image_scroll_view.add_subview(self.image_icons["0"])
		
		self.last_image_x -= 0
		buffer = self.outfit_saver.screen_width/30
		last_frame = self.image_icons["0"].frame
		self.image_scroll_view.content_size = (last_frame[0]+last_frame[2]+buffer, self.image_scroll_view.content_size[1])
		
		if self.caller_type == "c":
			self.category.update_icon(self.id, self.title, self.score)
		
	def add_link(self, sender):
		if not self.remove_mode:
			search_query = """
			SELECT item_id, item_name
			FROM items
			WHERE item_name LIKE 
			"""
			image_query = """
			SELECT item_image_id
			FROM item_images
			WHERE item_id=
			"""
			if self.link_selector != None:
				self.link_selector = Search_View("Search Clothing Items", search_query, image_query, "item_thumbnails", self.choose_link, self.view.background_color, self.outfit_saver)
			self.link_selector.open()
		
	def remove_link(self, sender):
		link_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "outfit_items"
		WHERE outfit_id = "{}" AND item_id = "{}"
		""".format(self.id, link_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.remove_icon(link_id, self.link_remove_buttons, self.link_icons, self.link_scroll_view)
		
		if len(self.link_icons) == 1:
			self.link_scroll_view.remove_subview(self.link_icons["0"])
			self.link_icons["0"] = self.create_add_icon(self.link_icons["0"].frame, "No outfit items yet :(", self.add_link, 12)
			self.link_scroll_view.add_subview(self.link_icons["0"])
		
		if self.last_link_y == 0:
			self.last_link_x -= 1
			self.last_link_y = 1
		else:
			self.last_link_y = 0
		buffer = self.outfit_saver.screen_width/30
		last_frame = self.link_icons["0"].frame
		self.link_scroll_view.content_size = (last_frame[0]+last_frame[2]+buffer, self.link_scroll_view.content_size[1])
		
	def open_link(self, sender):
		if not self.remove_mode:
			from item import Item
			Item(sender.name, self.category, "o", self.outfit_saver)
	
		
	def add_category(self, sender):
		if not self.remove_mode:
			search_query = """
			SELECT category_id, category_name, photo_path
			FROM outfit_categories
			WHERE category_name LIKE 
			"""
			image_query = ""
			if self.category_selector != None:
				self.category_selector = Search_View("Search Outfit Categories", search_query, image_query, "background_thumbnails", self.choose_category, self.view.background_color, self.outfit_saver)
		
	def remove_category(self, sender):
		category_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_outfits"
		WHERE outfit_id = "{}" AND category_id = "{}"
		""".format(self.id, category_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.remove_icon(category_id, self.category_remove_buttons, self.category_icons, self.category_scroll_view)
		
		if len(self.category_icons) == 1:
			self.category_scroll_view.remove_subview(self.category_icons["0"])
			self.category_icons["0"] = self.create_add_category_icon(self.category_icons["0"].frame, "This outfit is not in any categories :(")
			self.category_scroll_view.add_subview(self.category_icons["0"])
		
		self.last_category_y -= 1
		buffer = self.outfit_saver.screen_width/30
		last_frame = self.category_icons["0"].frame
		self.category_scroll_view.content_size = (self.category_scroll_view.content_size[0], last_frame[1]+last_frame[3]+buffer)
		
		if self.caller_type == "c":
			if self.category.id == category_id:
				self.category.remove_clothing_unit_icon(self.id)
		
	
	def save_note(self):
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "outfits" 
			SET
				outfit_note="{}"
			WHERE outfit_id="{}"
			'''.format(self.note, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
		
	def save_score(self):
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "outfits" 
			SET
				outfit_score="{}"
			WHERE outfit_id="{}"
			'''.format(self.score, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
			if self.caller_type == "c":
				self.category.update_icon(self.id, self.title, self.score)
		
	def save_title(self):
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "outfits" 
			SET
				outfit_name="{}"
			WHERE outfit_id="{}"
			'''.format(self.title, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
			if self.caller_type == "c":
				self.category.update_icon(self.id, self.title, self.score)
