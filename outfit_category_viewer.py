from category_viewer import Category_Viewer
from outfit_category import Outfit_Category

class Outfit_Category_Viewer(Category_Viewer):
	def __init__(self, outfit_saver):
		self.title = "OUTFIT CATEGORIES"
		self.db_table = "outfit_categories"
		self.image_type = "outfit"

		super().__init__(outfit_saver)
		
		self.view.background_color = "97C1B0"

	def add_category(self, sender):
		Outfit_Category(None, "NEW CATEGORY", "0", self, self.outfit_saver)
		
	def open_category(self, sender):
		category_icon = self.category_icons[sender.name]
		Outfit_Category(category_icon.id, category_icon.name, category_icon.photo_path, self, self.outfit_saver)
		
	

