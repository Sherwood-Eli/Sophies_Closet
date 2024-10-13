import sqlite3

from category_viewer import Category_Viewer
from item_category import Item_Category
from search_view import Search_View
from item import Item

class Item_Category_Viewer(Category_Viewer):
	def __init__(self, outfit_saver):
		self.title = "ITEM CATEGORIES"
		self.db_table = "item_categories"
		self.image_type = "item"
		
		super().__init__(outfit_saver)
		
		self.view.background_color = "DCBCDA"

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
		
		x = len(self.remove_buttons)-1
		category_keys = list(self.category_icons.keys())
		while self.remove_buttons[x].button.name != category_id:
			self.remove_buttons[x].button.center = self.remove_buttons[x-1].button.center
			key = category_keys[x]
			next_key = category_keys[x-1]
			self.category_icons[key].button.center = self.category_icons[next_key].button.center
			
			x-=1
			
		self.scroll_view.remove_subview(self.remove_buttons[x].button)
		self.scroll_view.remove_subview(self.category_icons[category_id].button)
			
		self.remove_buttons.pop(x)
		del self.category_icons[category_id]
		
		self.view.remove_subview(self.warning_view)
		
		self.warning_view = None
