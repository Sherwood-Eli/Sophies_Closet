import sqlite3

from category_viewer import Category_Viewer
from outfit_category import Outfit_Category
from search_view import Search_View
from outfit import Outfit

class Outfit_Category_Viewer(Category_Viewer):
	def __init__(self, outfit_saver):
		self.table_name = "outfit_categories"
		self.image_type = "outfit"

		super().__init__(outfit_saver)
		
	def add_category(self, sender):
		if not self.remove_mode:
			print("adding category")
			Outfit_Category(None, "NEW CATEGORY", "0", self, self.outfit_saver)
			print("category opened")
		
	def open_category(self, sender):
		if not self.remove_mode:
			category_icon = self.category_icons[sender.name]
			Outfit_Category(category_icon.id, category_icon.name, category_icon.photo_path, self, self.outfit_saver)
		
	def open_search(self, sender):
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
			self.link_selector = Search_View("Search Outfits", search_query, image_query, "outfit_thumbnails", self.open_outfit, self.view.background_color, self.outfit_saver)
		
	def open_outfit(self, sender):
		title = sender.subviews[0].text
		Outfit(sender.name, self.link_selector, "s", self.outfit_saver)
		
	def remove_category(self, sender):
		category_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "outfit_categories"
		WHERE category_id = "{}"
		""".format(category_id)
		
		result = cursor.execute(sql)
		
		sql = """
		DELETE FROM "category_outfits"
		WHERE category_id = "{}"
		""".format(category_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.view.remove_category_from_view(category_id)
			
			
		
		
	

