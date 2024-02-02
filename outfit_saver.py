import sqlite3
import photos
import ui
import math

from outfit_category_viewer import Outfit_Category_Viewer
from item_category_viewer import Item_Category_Viewer

class Outfit_Saver:
	def __init__(self):
		#TODO handle this better
		try:
			self.initialize_database()
		except:
			pass

		#initialize main view
		self.screen_width, self.screen_height = ui.get_screen_size()
		self.view = ui.View(background_color = "f0fff5", height = self.screen_height, width = self.screen_width)
		self.nav = ui.NavigationView(self.view, navigation_bar_hidden = True)
	
		#initialize "outfits"" and "clothing items" buttons
		pattern_image = ui.Image.named("images/button_images/colored_pattern.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		panel_image = ui.Image.named("images/button_images/white_panel.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		
		#initialize some dimentions
		buffer = self.screen_width/30
		rotation_angle = math.pi/18
		button_width = (self.screen_width-(2*buffer))
		button_height = (self.screen_height/2)-((3*buffer)+(buffer/2))
		
		#calculate dimentions of rotated pattern
		#TODO if the rotation angle is larger than tan^-1(y/x), it might be messed up
		if button_width > button_height:
			x = button_width
			y = button_height
		else:
			y = button_width
			x = button_height
		width = math.cos(rotation_angle)*((y*math.tan(rotation_angle))+x)
		
		#initialize "outfits" button
		outfit_button_frame = (buffer, 3*buffer, button_width, button_height)
		self.outfits_button = ui.Button(frame=outfit_button_frame, border_width=2, border_color="black", background_color="97C1B0", action=self.open_outfit_category_viewer)
		
		pattern_view = ui.ImageView(width=width, height=width, center=(button_width/2, button_height/2))
		pattern_view.image = pattern_image
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.outfits_button.add_subview(pattern_view)
		
		panel_view = ui.ImageView(frame=((3*buffer), (2*outfit_button_frame[3]/5), outfit_button_frame[2]-(6*buffer), outfit_button_frame[3]/5))
		panel_view.image = panel_image
		self.outfits_button.add_subview(panel_view)
		
		title_view = ui.ImageView(frame=(0, 2*buffer/3, outfit_button_frame[2]-(6*buffer), (outfit_button_frame[3]/5)-(buffer)), content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		title_image = ui.Image.named("images/button_images/text_outfits_purple.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		title_view.image = title_image
		panel_view.add_subview(title_view)
		
		self.view.add_subview(self.outfits_button)
		
		self.outfit_category_viewer = Outfit_Category_Viewer(self)
		
		
		#initialize "clothing items" button
		item_button_frame = (buffer, (self.screen_height/2)+(buffer/2), button_width, button_height)
		self.items_button = ui.Button(frame=item_button_frame, border_width=2, border_color="black", background_color="DCBCDA", action=self.open_item_category_viewer)
		
		pattern_view = ui.ImageView(width=width, height=width, center=(button_width/2, button_height/2))
		pattern_view.image = pattern_image
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.items_button.add_subview(pattern_view)
		
		panel_view = ui.ImageView(frame=((3*buffer), (2*outfit_button_frame[3]/5), outfit_button_frame[2]-(6*buffer), outfit_button_frame[3]/5))
		panel_view.image = panel_image
		self.items_button.add_subview(panel_view)
		
		title_view = ui.ImageView(frame=(0, 2*buffer/3, outfit_button_frame[2]-(6*buffer), (outfit_button_frame[3]/5)-(buffer)), content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		title_image = ui.Image.named("images/button_images/text_clothingitems_purple.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		title_view.image = title_image
		panel_view.add_subview(title_view)
		
		self.view.add_subview(self.items_button)
		
		self.item_category_viewer = Item_Category_Viewer(self)
		
		self.nav.present("fullscreen", hide_title_bar=True)
		
		
	def initialize_database(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		
		#TODO figure out if text shiukd be varchar
		
		#create outfits table
		sql = '''
		CREATE TABLE "outfits" (
			"outfit_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"outfit_name"	TEXT
		)
		'''
		cursor.execute(sql)
		
		#create items table
		sql = '''
		CREATE TABLE "items" (
			"item_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"item_name"	TEXT
		)
		'''
		cursor.execute(sql)

		#create outfit_categories table
		sql = '''
		CREATE TABLE "outfit_categories" (
			"category_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"category_name"	TEXT,
			"photo_path"	TEXT
		)
		'''
		cursor.execute(sql)
		
		#create item_categories table
		sql = '''
		CREATE TABLE "item_categories" (
			"category_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"category_name"	TEXT,
			"photo_path"	TEXT
			)
		'''
		cursor.execute(sql)
		
		#create outfit_items table
		sql = '''
		CREATE TABLE "outfit_items" (
			"outfit_id"	INTEGER,
			"item_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#create category_outfits table
		sql = '''
		CREATE TABLE "category_outfits" (
			"category_id"	INTEGER,
			"outfit_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#create category_items table
		sql = '''
		CREATE TABLE "category_items" (
			"category_id"	INTEGER,
			"item_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#TODO the image dorextory column will take up a lot of space for no reason
		
		#create images table
		sql = '''
		CREATE TABLE "images" (
			"image_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"image_directory"	TEXT
			)
		'''
		cursor.execute(sql)
		
		#create outfit_images table
		sql = '''
		CREATE TABLE "outfit_images" (
			"outfit_image_id"	INTEGER,
			"outfit_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#create item_images table
		sql = '''
		CREATE TABLE "item_images" (
			"item_image_id"	INTEGER,
			"item_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		conn.close()
		
	def open_outfit_category_viewer(self, sender):
		#TODO does this need to be done every time?
		self.outfit_category_viewer.remove_category_icons_from_view()
		self.outfit_category_viewer.category_icons = self.outfit_category_viewer.load_category_icons()
		self.outfit_category_viewer.put_category_icons_on_view()
		
		self.nav.push_view(self.outfit_category_viewer.view)	
		
	def open_item_category_viewer(self, sender):
		self.item_category_viewer.remove_category_icons_from_view()
		self.item_category_viewer.category_icons = self.item_category_viewer.load_category_icons()
		self.item_category_viewer.put_category_icons_on_view()
		
		self.nav.push_view(self.item_category_viewer.view)
				
outfit_saver = Outfit_Saver()
