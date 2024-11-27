import sqlite3

from category_viewer import Category_Viewer
from outfit_category import Outfit_Category
from outfit import Outfit

class Outfit_Category_Viewer(Category_Viewer):
	def __init__(self, model_id, params, view, outfit_saver):
		self.table_name = "outfit_categories"
		self.image_type = "outfit"

		super().__init__(model_id, view, outfit_saver)
		
	def open_search(self):
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
		self.outfit_saver.nav.push_view("search", "outfits", ("Search Outfits", search_query, image_query, "outfit_thumbnails", self.open_outfit, self.view.background_color))
	
	#Called by link selector
	def open_outfit(self, sender):
		outfit_id = sender.name
		self.outfit_saver.nav.push_view("outfit", outfit_id, outfit_id)
		
	def remove_category(self, category_id):
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
