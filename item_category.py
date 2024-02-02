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

		super().__init__(outfit_saver)

	def load_icons(self):
		conn = sqlite3.connect('db/outfit_saver.db')
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
		item_icons = {}
		for item in items:
			item_icons[str(item[0])] = Icon(item, self.next_icon_frame, self.image_type, self.icon_button_pressed)
		return item_icons
			
	def open_clothing_unit(self, item_icon):
		Item(item_icon.id, item_icon.name, self, False, self.outfit_saver)
		
	def add_clothing_unit(self):
		Item(None, "NEW CLOTHING ITEM", self, False, self.outfit_saver)
