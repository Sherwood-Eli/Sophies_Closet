import ui
import sqlite3
import math


from buttons import Add_Button, Back_Button
from icon import Icon

class Category_Viewer:
	def __init__(self, outfit_saver):
		self.outfit_saver = outfit_saver
		self.category_icons = {}
		self.last_category_x = -1
		self.last_category_y = 0
		
		s_width = self.outfit_saver.screen_width
		s_height = self.outfit_saver.screen_height
		
		self.view = ui.View(height = s_height, width = s_width)
		
		#create the background image
		rotation_angle = math.pi/18
		
		#calculate dimentions of rotated pattern
		#TODO if the rotation angle is larger than tan^-1(y/x), it might be messed up
		if s_width > s_height:
			x = s_width
			y = s_height
		else:
			y = s_width
			x = s_height
		width = math.cos(rotation_angle)*((y*math.tan(rotation_angle))+x)
		
		pattern_image = ui.Image.named("images/button_images/white_pattern.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		image_view = ui.ImageView(width=width, height=width, center=(s_width/2, s_height/2))
		image_view.image = pattern_image
		image_view.transform = ui.Transform.rotation(-rotation_angle)
		self.view.add_subview(image_view)
		
		
		
		#TODO dimentions are not exactly right, put in buttons file
		self.scroll_view = ui.ScrollView()
		self.scroll_view.width = outfit_saver.screen_width
		self.scroll_view.height = outfit_saver.screen_height*.85
		self.scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.5)
		self.scroll_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.view.add_subview(self.scroll_view)
		
		view_title = ui.Button(title = self.title, font = ('<system-bold>', 20))
		view_title.center = (outfit_saver.screen_width/2, outfit_saver.screen_height/10)
		self.view.add_subview(view_title)
		
		add_button = Add_Button(self.add_category, outfit_saver)
		self.view.add_subview(add_button.button)
		
		back_button = Back_Button(self.close_view, self.outfit_saver.screen_width, self.outfit_saver.screen_height)
		self.view.add_subview(back_button.button)
		
	def load_category_icons(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		sql = '''
		SELECT * FROM "{}"
		'''.format(self.db_table)
		cursor.execute(sql)
		categories = cursor.fetchall()
		category_icons = {}
		for category in categories:
			category_icons[str(category[0])] = Icon(category, self.next_icon_frame, self.image_type, self.open_category)
		
		return category_icons
		
	def remove_category_icons_from_view(self):
		for id in self.category_icons:
			self.scroll_view.remove_subview(self.category_icons[id].button)
		self.category_icons = {}
		self.last_category_x = -1
		self.last_category_y = 0
		
	def put_category_icons_on_view(self):
		for id in self.category_icons:
			self.scroll_view.add_subview(self.category_icons[id].button)
		
	def refresh_icons(self):
		self.remove_category_icons_from_view()
		self.category_icons = self.load_category_icons()
		self.put_category_icons_on_view()
		
	def next_icon_frame(self):
		self.last_category_x+=1
		if self.last_category_x == 3:
			self.last_category_x = 0
			self.last_category_y += 1
		x = self.last_category_x
		y = self.last_category_y
		
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/30
		starting_x = (buffer)+((screen_width/3)*x)
		starting_y = ((screen_height/5)*y)+(buffer)
		width = (screen_width/3)-(2*buffer)
		height = (screen_height/5)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		if starting_y+height > self.scroll_view.content_size[1]:
			self.scroll_view.content_size = (screen_width, starting_y+height+(2*buffer))
			
		return frame
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
