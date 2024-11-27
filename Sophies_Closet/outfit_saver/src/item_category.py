import sqlite3

from category import Category
from item import Item


class Item_Category(Category):
	def __init__(self, id, params, view, outfit_saver):
		self.table_name = "item_categories"
		self.image_type = "item"
		super().__init__(id, view, outfit_saver)
		
	def load_preview_data(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT items.item_id, item_name
		FROM "items"
		INNER JOIN "category_items"
		ON items.item_id = category_items.item_id
		WHERE category_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		preview_data = cursor.fetchall()
		conn.close()
		return preview_data
			
	def open_clothing_unit(self, item_id):
		self.outfit_saver.nav.push_view("item", item_id, item_id)
			
	def remove_clothing_unit(self, item_id):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_items"
		WHERE category_id = "{}" AND item_id = "{}"
		""".format(self.id, item_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
