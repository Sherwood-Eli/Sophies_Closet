import sqlite3

from category_viewer import Category_Viewer
from item_category import Item_Category
from search_view import Search_View
from item import Item

class Item_Category_Viewer(Category_Viewer):
	def __init__(self, outfit_saver):
		self.table_name = "item_categories"
		self.image_type = "item"
				
		super().__init__(outfit_saver)
				
	def add_category(self, sender):
		if not self.remove_mode:
			Item_Category(None, "NEW CATEGORY", "0", self, self.outfit_saver)
		
	def open_category(self, sender):
		if not self.remove_mode:
			category_icon = self.category_icons[sender.name]
			Item_Category(category_icon.id, category_icon.name, category_icon.photo_path, self, self.outfit_saver)
		
	def open_search(self, sender):
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
			self.link_selector = Search_View("Search Clothing Items", search_query, image_query, "item_thumbnails", self.open_item, self.view.background_color, self.outfit_saver)
	
	#Called by link selector
	def open_item(self, sender):
		title = sender.subviews[0].text
		Item(sender.name, self.link_selector, "s", self.outfit_saver)
		
	def remove_category(self, sender):
		category_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "item_categories"
		WHERE category_id = "{}"
		""".format(category_id)
		
		result = cursor.execute(sql)
		
		sql = """
		DELETE FROM "category_items"
		WHERE category_id = "{}"
		""".format(category_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		
		
