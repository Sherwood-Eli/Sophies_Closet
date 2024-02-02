from category_viewer import Category_Viewer
from item_category import Item_Category

class Item_Category_Viewer(Category_Viewer):
	def __init__(self, outfit_saver):
		self.title = "CLOTHING ITEM CATEGORIES"
		self.db_table = "item_categories"
		self.image_type = "item"

		super().__init__(outfit_saver)
		
		self.view.background_color = "DCBCDA"

	def add_category(self, sender):
		Item_Category(None, "NEW CATEGORY", "0", self, self.outfit_saver)
		
	def open_category(self, sender):
		category_icon = self.category_icons[sender.name]
		Item_Category(category_icon.id, category_icon.name, category_icon.photo_path, self, self.outfit_saver)
