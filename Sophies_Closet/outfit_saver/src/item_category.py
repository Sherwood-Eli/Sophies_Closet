import sqlite3

from category import Category
from item import Item
from icon import Icon

class Item_Category(Category):
	def __init__(self, id, title, photo_path, category_viewer, outfit_saver):
		self.id = id
		self.title = title
		self.photo_path = photo_path
		self.db_table = "item_categories"
		self.image_type = "item"
		self.category_viewer = category_viewer

		super().__init__("DCBCDA", outfit_saver)
		
	def load_icons(self):
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
		items = cursor.fetchall()
		conn.close()
		item_icons = {}
		for item in items:
			item_icons[str(item[0])] = Icon(item, self.next_icon_frame, self.image_type, self.icon_button_pressed)
		return item_icons
			
	def open_clothing_unit(self, item_icon):
		if not self.remove_mode:
			Item(item_icon.id, self, "c", self.outfit_saver)
		
	def add_clothing_unit(self, sender):
		if not self.remove_mode:
			Item(None, self, "c", self.outfit_saver)
			
	def remove_clothing_unit(self, sender):
		item_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_items"
		WHERE category_id = "{}" AND item_id = "{}"
		""".format(self.id, item_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.remove_clothing_unit_icon(item_id)
