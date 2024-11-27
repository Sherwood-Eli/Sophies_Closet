import sqlite3

from category import Category
from outfit import Outfit


class Outfit_Category(Category):
	def __init__(self, id, params, view, outfit_saver):
		self.table_name = "outfit_categories"
		self.image_type = "outfit"
		super().__init__(id, view, outfit_saver)
		
	def load_preview_data(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT outfits.outfit_id, outfit_name
		FROM "outfits"
		INNER JOIN "category_outfits"
		ON outfits.outfit_id = category_outfits.outfit_id
		WHERE category_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		preview_data = cursor.fetchall()
		conn.close()
		return preview_data
		
	def open_clothing_unit(self, outfit_id):
		self.outfit_saver.nav.push_view("outfit", outfit_id, outfit_id)
		
	def remove_clothing_unit(self, outfit_id):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_outfits"
		WHERE category_id = "{}" AND outfit_id = "{}"
		""".format(self.id, outfit_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
