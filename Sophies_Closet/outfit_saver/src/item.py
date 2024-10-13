import ui
import sqlite3

from buttons import  *
from image_selector import Image_Selector
from clothing_unit import Clothing_Unit
from search_view import Search_View

class Item(Clothing_Unit):
	def __init__(self, id, caller, caller_type, outfit_saver):
		self.type = "item"
		self.link_type = "outfit"
		super().__init__(id, caller, caller_type, outfit_saver)
		self.outfit_saver.item_view.load_view(self)
			
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
			
		result = cursor.execute(sql)
		conn.commit()
		
		sql='''
			select seq from sqlite_sequence where name="items"
			'''
		cursor.execute(sql)
		last_row=cursor.fetchall()
		self.id = str(last_row[0][0])
				
		if self.category.id == None:
			self.category.save_category()
		
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
		
		if self.caller_type == "c":
			self.category.remove_clothing_unit(self.category.icons[self.id].button)
		elif self.caller_type == "s":
			self.category.search(self.category.text_field.text)
		
		self.close_view(None)
			
	def add_image(self, sender):
		if not self.remove_mode:
			if self.image_selector != None:
				self.image_selector = Image_Selector("item_images", "item_thumbnails", "", self.choose_image, self.outfit_saver, False, self.view.background_color)
			self.image_selector.open()
			
	def remove_image(self, sender):
		image_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "item_images"
		WHERE item_image_id = "{}" AND item_id = "{}"
		""".format(image_id, self.id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		if len(self.image_icons) == 5 and "0" not in self.image_icons:
			frame = self.get_next_image_frame()
			self.image_icons["0"] = self.create_add_icon(frame, "", self.add_image, 25)
			self.image_scroll_view.add_subview(self.image_icons["0"])
		
		self.remove_icon(image_id, self.image_remove_buttons, self.image_icons, self.image_scroll_view)
		
		if len(self.image_icons) == 1:
			self.image_scroll_view.remove_subview(self.image_icons["0"])
			self.image_icons["0"] = self.create_add_icon(self.image_icons["0"].frame, "No item images yet :(", self.add_image, 25)
			self.image_scroll_view.add_subview(self.image_icons["0"])
		
		self.last_image_x -= 0
		buffer = self.outfit_saver.screen_width/30
		last_frame = self.image_icons["0"].frame
		self.image_scroll_view.content_size = (last_frame[0]+last_frame[2]+buffer, self.image_scroll_view.content_size[1])
		
		if self.caller_type == "c":
			self.category.update_icon(self.id, self.title, self.score)
		
	def create_link_icon(self, link_id, link_name):
		frame = self.get_next_link_frame()
		
		button = ui.Button(border_width=2, border_color="black", frame=frame, background_color="f0fff5")
		button.corner_radius = button.width/10
		button.name = link_id
		
		buffer = frame[2]/20
		title = ui.Label(frame = (buffer, buffer, frame[2]-(2*buffer), frame[3]-(2*buffer)))
		title.number_of_lines = 0
		title.line_break_mode = ui.LB_WORD_WRAP
		title.alignment = ui.ALIGN_LEFT
		title.text = link_name
		button.add_subview(title)
		
		if link_id != "0":
			button.action = self.open_link
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			
			sql = '''
			SELECT "outfit_image_id"
			FROM "outfit_images"
			WHERE outfit_id="{}"
			'''.format(link_id)
			cursor.execute(sql)
			image_ids = cursor.fetchall()
			conn.close()
			
			#only take the first one
			if len(image_ids) == 0:
				return button
			image_id = str(image_ids[0][0])
			image = ui.Image.named("../images/outfit_thumbnails/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FILL, frame=(0,0,frame[2],frame[3]))
			
		image_view.image = image
		button.add_subview(image_view)
		
		return button
		
	def add_link(self, sender):
		if not self.remove_mode:
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
			if self.link_selector != None:
				self.link_selector = Search_View("Search Outfits", search_query, image_query, "outfit_thumbnails", self.choose_link, self.view.background_color, self.outfit_saver)
			self.link_selector.open()
			
	def remove_link(self, sender):
		link_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "outfit_items"
		WHERE outfit_id = "{}" AND item_id = "{}"
		""".format(link_id, self.id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.remove_icon(link_id, self.link_remove_buttons, self.link_icons, self.link_scroll_view)
		
		if len(self.link_icons) == 1:
			self.link_scroll_view.remove_subview(self.link_icons["0"])
			self.link_icons["0"] = self.create_add_icon(self.link_icons["0"].frame, "Not in any outfits yet :(", self.add_link, 12)
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
			from outfit import Outfit
			Outfit(sender.name, self.category, "i", self.outfit_saver)
		
		
	def add_category(self, sender):
		if not self.remove_mode:
			search_query = """
			SELECT category_id, category_name, photo_path
			FROM item_categories
			WHERE category_name LIKE 
			"""
			image_query = ""
			if self.category_selector != None:
				self.category_selector = Search_View("Search Item Categories", search_query, image_query, "background_thumbnails", self.choose_category, self.view.background_color, self.outfit_saver)
			self.category_selector.open()
			
	def remove_category(self, sender):
		category_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_items"
		WHERE item_id = "{}" AND category_id = "{}"
		""".format(self.id, category_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.remove_icon(category_id, self.category_remove_buttons, self.category_icons, self.category_scroll_view)
		
		if len(self.category_icons) == 1:
			self.category_scroll_view.remove_subview(self.category_icons["0"])
			self.category_icons["0"] = self.create_add_category_icon(self.category_icons["0"].frame, "This item is not in any categories :(")
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
			UPDATE "items" 
			SET
				item_note="{}"
			WHERE item_id="{}"
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
			UPDATE "items" 
			SET
				item_score="{}"
			WHERE item_id="{}"
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
			UPDATE "items" 
			SET
				item_name="{}"
			WHERE item_id="{}"
			'''.format(self.title, self.id)
			result = cursor.execute(sql)
			conn.commit()
			conn.close()
			if self.caller_type == "c":
				self.category.update_icon(self.id, self.title, self.score)
