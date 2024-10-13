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
		print("calling super constructor")
		super().__init__("97C1B0", outfit_saver)
		print("done with that")
		
	def load_icons(self):
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
		outfits = cursor.fetchall()
		conn.close()
		outfit_icons = {}
		for outfit in outfits:
			outfit_icons[str(outfit[0])] = Icon(outfit, self.next_icon_frame, self.image_type, self.icon_button_pressed)
		
		return outfit_icons
		
	def open_clothing_unit(self, outfit_icon):
		if not self.remove_mode:
			Outfit(outfit_icon.id, self, "c", self.outfit_saver)
		
	def add_clothing_unit(self, sender):
		if not self.remove_mode:
			Outfit(None, self, "c", self.outfit_saver)
		
	def remove_clothing_unit(self, sender):
		outfit_id = sender.name
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = """
		DELETE FROM "category_outfits"
		WHERE category_id = "{}" AND outfit_id = "{}"
		""".format(self.id, outfit_id)
		
		result = cursor.execute(sql)
		
		conn.commit()
		conn.close()
		
		self.remove_clothing_unit_icon(outfit_id)
	
	
