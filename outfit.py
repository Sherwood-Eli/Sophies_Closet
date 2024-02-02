import ui
import sqlite3

from buttons import  *
from image_selector import Image_Selector
from clothing_unit import Clothing_Unit
from search_view import Search_View

class Outfit(Clothing_Unit):
	"""
	Create a new entry in the outfits table and create new enties in the outfits_items table. 
	"""
	def __init__(self, id, title, category, category_read_only, outfit_saver):
		super().__init__(id, title, category, category_read_only, outfit_saver)
		
	def create(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "outfits" (
			"outfit_name"
			)
		VALUES (
			"{}"
			)
		'''.format(self.title)
			
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
		
	def get_image_icons(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT outfit_image_id
		FROM "outfit_images"
		WHERE outfit_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		image_ids = cursor.fetchall()
		images = {}
		for entry in image_ids:
			frame = self.get_next_image_frame()
			image_id = str(entry[0])
			image = ui.Image.named("images/outfit_images/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			
			images[image_id] = self.create_image_icon(frame, image, image_id)
		
		if len(images) < 5:
			frame = self.get_next_image_frame()
			image_id = "0"
			image = ui.Image.named("images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			images[image_id] = self.create_image_icon(frame, image, image_id)
			images[image_id].action = self.add_image
		
		return images
	
	def save_new_image(self, image, image_name):		
		if self.id == None:
			self.create()
		
		if image_name in self.image_icons:
			self.image_selector.show_warning("Image already selected")
			return
		
		#add outfit_image
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "outfit_images" (
			"outfit_image_id",
			"outfit_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(int(image_name), int(self.id))
		
		result = cursor.execute(sql)
		conn.commit()
		
		#TODO make this more efficient
		self.remove_icons_from_view(self.image_scroll_view, self.image_icons)
		self.last_image_x = -1
		self.image_icons = self.get_image_icons()
		self.put_icons_on_view(self.image_scroll_view, self.image_icons)
		
		self.outfit_saver.nav.pop_view()
		
		#TODO make icon get resized
		if not self.category_read_only:
			self.category.update_icon(self.id, self.title)
			
	def add_image(self, sender):
		self.image_selector = Image_Selector("outfit_images", "outfit_thumbnails", "", self.save_new_image, self.outfit_saver, False)
		
	def get_link_icons(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT items.item_id, item_name
		FROM "items"
		INNER JOIN "outfit_items"
		ON items.item_id = outfit_items.item_id
		WHERE outfit_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		item_ids = cursor.fetchall()
		links = {}
		for entry in item_ids:
			link_id = str(entry[0])
			link_name = entry[1]
			links[link_id] = self.create_link_icon(link_id, link_name)
		#get icon for adding a link
		link_id = "0"
		links[link_id] = self.create_link_icon(link_id, "")
		
		return links
		
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
			conn = sqlite3.connect('db/outfit_saver.db')
			cursor = conn.cursor()
			
			sql = '''
			SELECT "item_image_id"
			FROM "item_images"
			WHERE item_id="{}"
			'''.format(link_id)
			cursor.execute(sql)
			image_ids = cursor.fetchall()
			
			#only take the first one
			image_id = str(image_ids[0][0])
			image = ui.Image.named("images/item_thumbnails/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FILL, frame=(0,0,frame[2],frame[3]))
			button.action = self.open_link
		else:
			image = ui.Image.named("images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			image_view = ui.ImageView(height=button.width/2, width=button.width/2, center=(button.width/2, button.height/2))
			button.action = self.add_link
			
		image_view.image = image
		button.add_subview(image_view)
		
		return button
		
	def add_link(self, sender):
		self.link_selector = Search_View("Search Clothing Items", "items", "item_id", "item_name", "item_image_id", "item_images", "item_thumbnails", self.choose_link, self.outfit_saver)
		
	def choose_link(self, sender):
		link_id = sender.name
		
		if self.id == None:
			self.create()
		
		if link_id in self.link_icons:
			self.link_selector.show_warning("Link already selected")
			return
			
		#add outfit_item
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "outfit_items" (
			"outfit_id",
			"item_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(int(self.id), int(link_id))
		
		result = cursor.execute(sql)
		conn.commit()
		
		#need this to keep "+" button at the end
		new_link = self.create_link_icon(link_id)
		new_frame = new_link.frame
		new_link.frame = self.link_icons["0"].frame
		self.link_icons["0"].frame = new_frame
		self.link_icons[link_id] = new_link
		
		self.link_scroll_view.add_subview(new_link)
		
		self.outfit_saver.nav.pop_view()
		
	def open_link(self, sender):
		from item import Item
		title = sender.subviews[0].text
		Item(sender.name, title, self.category, True, self.outfit_saver)
	
	def get_category_icons(self):
		#the first category is implied
		if self.id == None:
			categories = {}
			category_id = self.category.id
			category_name = self.category.title
			photo_path = self.category.photo_path
			categories[category_id] = self.create_category_icon(category_id, category_name, photo_path)
			return categories
		
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT outfit_categories.category_id, outfit_categories.category_name, outfit_categories.photo_path
		FROM "outfit_categories"
		INNER JOIN "category_outfits"
		ON outfit_categories.category_id = category_outfits.category_id
		WHERE outfit_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		rows = cursor.fetchall()
		categories = {}
		
		for category in rows:
			category_id = str(category[0])
			categories[category_id] = self.create_category_icon(str(category[0]), str(category[1]), category[2])
		#get icon for adding a category
		category_id = "0"
		categories[category_id] = self.create_category_icon("0", None, None)
		
		return categories
		
	def add_category(self, sender):
		self.category_selector = Search_View("Search Outfit Categories", "outfit_categories", "category_id, category_name, photo_path", "category_name", None, None, "background_thumbnails", self.choose_category, self.outfit_saver)
		
	def choose_category(self, sender):
		category_id = sender.name
		
		if self.id == None:
			self.create()
 
		if category_id in self.category_icons:
			self.category_selector.show_warning("category already selected")
			return
			
		#add category_outfit
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "category_outfits" (
			"category_id",
			"outfit_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(int(category_id), int(self.id))
		
		result = cursor.execute(sql)
		conn.commit()
		
		sql = '''
		SELECT category_name, photo_path
		FROM "outfit_categories" 
		WHERE category_id = {}
		'''.format(int(category_id))
		
		result = cursor.execute(sql)
		category = cursor.fetchall()
		
		conn.close()
		
		#need this to keep "+" button at the end
		new_category = self.create_category_icon(category_id, category[0], category[1])
		new_category = new_category.frame
		new_category.frame = self.category_icons["0"].frame
		self.category_icons["0"].frame = new_frame
		self.category_icons[category_id] = new_category
		
		self.category_scroll_view.add_subview(new_category)
		
		self.outfit_saver.nav.pop_view()
		
	def save(self):
		if self.id == None:
			self.create()
		else:
			conn = sqlite3.connect('db/outfit_saver.db')
			cursor = conn.cursor()
			sql = '''
			UPDATE "outfits" 
			SET
				outfit_name="{}"
			WHERE outfit_id="{}"
			'''.format(self.title, self.id)
			result = cursor.execute(sql)
			conn.commit()
		if not self.category_read_only:
			self.category.update_icon(self.id, self.title)
