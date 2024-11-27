import sqlite3

from category_viewer import Category_Viewer
from item_category import Item_Category
from item import Item

class Item_Category_Viewer(Category_Viewer):
	def __init__(self, model_id, params, view, outfit_saver):
		self.table_name = "item_categories"
		self.image_type = "item"
				
		super().__init__(model_id, view, outfit_saver)
		
	def open_search(self):
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
		self.outfit_saver.nav.push_view("search", "items", ("Search Clothing Items", search_query, image_query, "item_thumbnails", self.open_item, self.view.background_color))
	
	#Called by link selector
	def open_item(self, sender):
		item_id = sender.name
		self.outfit_saver.nav.push_view("item", item_id, item_id)
		
	def remove_category(self, category_id):
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
