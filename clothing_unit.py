import ui
import sqlite3

from buttons import  *
from image_selector import Image_Selector

class Clothing_Unit:
	def __init__(self, id, title, category, category_read_only, outfit_saver):
		self.id = id
		self.title = title
		self.category = category
		self.category_read_only = category_read_only
		self.outfit_saver = outfit_saver
		
		self.last_image_x = -1
		self.last_link_x = 0
		self.last_link_y = -1
		self.last_category_y = -1
		
		self.view = ui.View(background_color = "f0fff5", height = outfit_saver.screen_height, width = outfit_saver.screen_width)
		
		self.background_view = ui.ImageView(frame = (0, outfit_saver.screen_height*.15, outfit_saver.screen_width, outfit_saver.screen_height*.85))
		self.background_view.image = category.image_view.image
		self.view.add_subview(self.background_view)
		
		temp_view = ui.View(frame = (0, outfit_saver.screen_height*.15, outfit_saver.screen_width, int(outfit_saver.screen_height*.85)))
		self.main_scroll_view = ui.ScrollView()
		self.main_scroll_view.frame = (0, 0, outfit_saver.screen_width, int(outfit_saver.screen_height*.85))
		self.main_scroll_view.border_width = 2
		self.main_scroll_view.paging_enabled = True
		self.main_scroll_view.bounces = False
		self.main_scroll_view.shows_vertical_scroll_indicator = False
		temp_view.add_subview(self.main_scroll_view)
		self.main_scroll_view.content_size = (outfit_saver.screen_width, (self.main_scroll_view.height*2))
		self.view.add_subview(temp_view)
		
		self.image_scroll_view = ui.ScrollView()
		self.image_scroll_view.frame = (0, 0, outfit_saver.screen_width, outfit_saver.screen_height*.85)
		self.image_scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.85)
		self.image_scroll_view.border_width = 2
		self.image_scroll_view.paging_enabled = True
		self.image_scroll_view.bounces = False
		self.main_scroll_view.add_subview(self.image_scroll_view)
		
		self.image_icons = self.get_image_icons()
		self.put_icons_on_view(self.image_scroll_view, self.image_icons)
		
		self.link_scroll_view = ui.View()
		self.link_scroll_view.frame = (0, outfit_saver.screen_height*.85, outfit_saver.screen_width, outfit_saver.screen_height*.425)
		self.link_scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.425)
		self.link_scroll_view.border_width=2
		self.main_scroll_view.add_subview(self.link_scroll_view)
		
		self.link_icons = self.get_link_icons()
		self.put_icons_on_view(self.link_scroll_view, self.link_icons)
		
		self.category_scroll_view = ui.ScrollView()
		self.category_scroll_view.frame = (0, outfit_saver.screen_height*1.275, outfit_saver.screen_width, outfit_saver.screen_height*.425)
		self.category_scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.425)
		self.category_scroll_view.border_width = 2
		self.main_scroll_view.add_subview(self.category_scroll_view)
		
		self.category_icons = self.get_category_icons()
		self.put_icons_on_view(self.category_scroll_view, self.category_icons)
		
		self.title_button = Title_Button(title, self.edit_title, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.title_button.button)
		
		self.title_edit_field = Title_Edit_Field(self.title_button.button, self.change_title)
		
		self.back_button = Back_Button(self.close_view, self.outfit_saver.screen_width, self.outfit_saver.screen_height)
		self.view.add_subview(self.back_button.button)

		self.outfit_saver.nav.push_view(self.view)

	def print_size(self, sender):
		print(self.main_scroll_view.content_size, self.main_scroll_view.height)
		
	def edit_title(self, sender):
		self.view.remove_subview(self.title_button.button)
		self.view.add_subview(self.title_edit_field.text_field)
		self.title_edit_field.text_field.begin_editing()
		
	def change_title(self, sender):
		self.title = sender.text
		self.title_button.button.title = self.title
		self.view.remove_subview(self.title_edit_field.text_field)
		self.view.add_subview(self.title_button.button)
		
		self.save()
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def put_icons_on_view(self, view, icons):
		for icon in icons:
			view.add_subview(icons[icon])
			
	def remove_icons_from_view(self, view, icons):
		for icon in icons:
			view.remove_subview(icons[icon])
		
	def get_next_image_frame(self):
		self.last_image_x+=1
		x = self.last_image_x
		
		scroll_view_width = self.main_scroll_view.width
		scroll_view_height = self.main_scroll_view.height
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/30
		starting_x = (scroll_view_width*x)+(buffer)
		starting_y = (buffer)
		width = (screen_width)-(2*buffer)
		height = (scroll_view_height)-(7*buffer)
		frame=(starting_x, starting_y, width, height)
		
		if starting_x+width > self.image_scroll_view.content_size[1]:
			self.image_scroll_view.content_size = (starting_x+width+(buffer), scroll_view_height)

		return frame
		
	def select_image(self, sender):
		pass
		
	def create_image_icon(self, frame, image, image_name):
		button = ui.Button(border_width=2, border_color = "black", frame=frame, action=self.select_image, background_color="f0fff5")
		button.corner_radius = button.width/10
		button.name = image_name
		button.image = image
		return button	
		
	def get_next_link_frame(self):
		if self.last_link_y == 1:
			self.last_link_y = -1
			self.last_link_x += 1
			
		self.last_link_y+=1
		x = self.last_link_x
		y = self.last_link_y
		
		
		scroll_view_width = self.link_scroll_view.width
		scroll_view_height = self.link_scroll_view.height
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/30
		link_region_width = scroll_view_width/3
		link_region_height = scroll_view_height/2
		
		starting_x = (link_region_width*x)+(buffer)
		starting_y = (link_region_height*y)+(buffer)
		width = link_region_width-(2*buffer)
		height = link_region_height-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		if starting_x+width > self.link_scroll_view.content_size[0]:
			self.link_scroll_view.content_size = (starting_x+width+(buffer), scroll_view_height)

		return frame
		
	def get_next_category_frame(self):
		self.last_category_y += 1
		y = self.last_category_y
		
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/30
		
		width = screen_width-(2*buffer)
		height = (screen_height/10)
		starting_x = (buffer)
		starting_y = buffer+(height+buffer)*y
		
		frame=(starting_x, starting_y, width, height)
		
		if starting_x+width > self.category_scroll_view.content_size[1]:
			self.category_scroll_view.content_size = (screen_width, starting_y+height+buffer)

		return frame
		
	def create_category_icon(self, category_id, category_name, photo_path):
		
		frame = self.get_next_category_frame()
		
		button = ui.Button(border_width=2, border_color="black", frame=frame, background_color="f0fff5")
		button.corner_radius = button.height/4
		button.name = category_id
		button.title = category_name
		
		if category_id != "0":
			if photo_path != "0":
				image = ui.Image.named("images/background_images/"+photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			else:
				image = None
			image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FILL, frame=(0,0,frame[2],frame[3]))
			button.action = None
		else:
			image = ui.Image.named("images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			image_view = ui.ImageView(height=button.height/2, width=button.height/2, center=(button.width/2, button.height/2))
			button.action = self.add_category
			
		image_view.image = image
		button.add_subview(image_view)
		
		return button
		
	def select_link(self, sender):
		pass
