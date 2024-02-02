import sqlite3

from category import Category
from outfit import Outfit
from icon import Icon

class Outfit_Category(Category):
	def __init__(self, id, title, photo_path, category_viewer, outfit_saver):
		self.id = id
		self.title = title
		self.photo_path = photo_path
		self.db_table = "outfit_categories"
		self.image_type = "outfit"
		self.category_viewer = category_viewer

		super().__init__(outfit_saver)

	def load_icons(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT outfits.outfit_id, outfit_name
		FROM "outfits"
		INNER JOIN "category_outfits"
		ON outfits.outfit_id = category_outfits.outfit_id
		WHERE category_id="{}"
		'''.format(self.id)
		cursor.execute(sql)
		outfits = cursor.fetchall()
		outfit_icons = {}
		for outfit in outfits:
			outfit_icons[str(outfit[0])] = Icon(outfit, self.next_icon_frame, self.image_type, self.icon_button_pressed)
		
		return outfit_icons
		
	def open_clothing_unit(self, outfit_icon):
		Outfit(outfit_icon.id, outfit_icon.name, self, False, self.outfit_saver)
		
	def add_clothing_unit(self):
		Outfit(None, "NEW OUTFIT", self, False, self.outfit_saver)
