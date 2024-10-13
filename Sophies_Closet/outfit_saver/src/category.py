import ui
import photos
import sqlite3
import math

from buttons import Add_Button, Back_Button, Title_Button, Image_Button, Title_Edit_Field, Remove_Button, Small_Remove_Button
from image_selector import Image_Selector
from icon import Icon
from warning_view import Warning_View

class Category:
	@ui.in_background
	def __init__(self, bg_color, outfit_saver):
		self.outfit_saver = outfit_saver
		self.remove_mode = False
		self.remove_buttons = []
		self.warning_view = None
		self.bg_image = None
		
		self.last_c1_y = outfit_saver.screen_width/30
		self.last_c2_y = outfit_saver.screen_width/30
			
		self.view = ui.View(background_color = bg_color, height = outfit_saver.screen_height, width = outfit_saver.screen_width)
		
		self.image_view = ui.ImageView(height = outfit_saver.screen_height*.85, width = outfit_saver.screen_width, content_mode=ui.CONTENT_SCALE_ASPECT_FILL)
		try:
			self.bg_image = ui.Image.named("../images/background_images/"+self.photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			self.image_view.image = self.bg_image
		except:
			pass
		self.image_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		
		s_width = self.outfit_saver.screen_width
		s_height = self.outfit_saver.screen_height
		
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
		
		pattern_image = ui.Image.named("../images/button_images/white_pattern.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		pattern_view = ui.ImageView(width=width, height=width, center=(s_width/2, s_height/2))
		pattern_view.image = pattern_image
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.view.add_subview(pattern_view)
		
		self.view.add_subview(self.image_view)
		
		self.scroll_view = ui.ScrollView()
		self.scroll_view.width = outfit_saver.screen_width
		self.scroll_view.height = outfit_saver.screen_height*.85
		self.scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.5)
		self.scroll_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.view.add_subview(self.scroll_view)
		
		#Title_Button
		self.title_button = Title_Button(self.title, self.edit_title, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.title_button.button)
		self.title_edit_field = Title_Edit_Field(self.title_button.button, self.change_title)
	
		#Add_Button
		self.add_button = Add_Button(self.add_clothing_unit, outfit_saver)
		self.view.add_subview(self.add_button.button)
		
		#Remove_Button
		remove_button = Remove_Button(self.toggle_remove_mode, outfit_saver)
		self.view.add_subview(remove_button.button)
		
		#Back_Button
		self.back_button = Back_Button(self.close_view, self.outfit_saver.screen_width, self.outfit_saver.screen_height)
		self.view.add_subview(self.back_button.button)
		
		#Image_Button
		self.image_button = Image_Button(self.choose_background_image, self.outfit_saver.screen_width, self.outfit_saver.screen_height)
		self.view.add_subview(self.image_button.button)
		
		#TODO make sure view is pushed imediately, icons can be put on as soon as theyre ready
		self.outfit_saver.nav.push_view(self.view)
		self.icons = self.load_icons()
		self.put_icons_on_view()
		
	def icon_button_pressed(self, sender):
		icon = self.icons[sender.name]
		self.open_clothing_unit(icon)
		
	def remove_icons_from_view(self):
		for id in self.icons:
			self.scroll_view.remove_subview(self.icons[id].button)
		self.icons = {}
		self.last_c1_y = self.outfit_saver.screen_width/30
		self.last_c2_y = self.outfit_saver.screen_width/30
		
	def put_icons_on_view(self):
		for id in self.icons:
			self.scroll_view.add_subview(self.icons[id].button)
			
	def next_icon_frame(self, image_ratio):
		#TODO i want to make it so the scroll view is scrollable when an icon is past the top of the add button
		
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/30
		
		width =(screen_width/2)-(2*buffer)
		if image_ratio == 0:
			height = (screen_height/5)-(2*buffer)
		else:
			height = width*image_ratio
		
		if self.last_c1_y <= self.last_c2_y:
			frame = (buffer, self.last_c1_y, width, height)
			self.last_c1_y+=(buffer+height)
			if self.last_c1_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (screen_width, self.last_c1_y)
		else:
			frame = (buffer+(screen_width/2), self.last_c2_y, width, height)
			self.last_c2_y+=(buffer+height)
			if self.last_c2_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (screen_width, self.last_c2_y)
	
		return frame
		
	def edit_title(self, sender):
		self.view.remove_subview(self.title_button.button)
		self.view.add_subview(self.title_edit_field.text_field)
		self.title_edit_field.text_field.begin_editing()
		
	def change_title(self, sender):
		self.title = sender.text
		self.title_button.button.title = self.title
		self.view.remove_subview(self.title_edit_field.text_field)
		self.view.add_subview(self.title_button.button)
		
		self.save_category()
		
	def choose_background_image(self, sender):
		if not self.remove_mode:
			Image_Selector("background_images", "background_thumbnails", self.photo_path, self.set_background_image, self.outfit_saver, True, self.view.background_color)
		
	def set_background_image(self, image, image_name):
		self.photo_path = image_name
		self.image_view.image = image
		self.bg_image = image
		self.save_category()
		
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
				
	def save_category(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		if self.id == None:
			#insert into table
			sql = '''
			INSERT INTO "{}" (
				"category_name",
				"photo_path")
			VALUES (
				"{}",
				"{}")
			'''.format(self.db_table, self.title, self.photo_path)
			
			
			cursor.execute(sql)
			conn.commit()
			sql='''
			select seq from sqlite_sequence where name="{}"
			'''.format(self.db_table)
			cursor.execute(sql)
			last_row=cursor.fetchall()
			self.id = str(last_row[0][0])
		else:
			sql = '''
			UPDATE "{}" 
			SET
				category_name="{}",
				"photo_path"="{}"
			WHERE category_id="{}"
			'''.format(self.db_table, self.title, self.photo_path, self.id)
			cursor.execute(sql)
			conn.commit()
			
		conn.close()
		
		
		
		#refresh icons
		#TODO could be more effieciently done
		#id must be non-null now please fix
		
		self.category_viewer.refresh_icons()
	
	#TODO update score on icon if i end up putting it on there in the first place
	def update_icon(self, icon_id, title, score):
		if icon_id in self.icons:
			icon = self.icons[icon_id]
			self.scroll_view.remove_subview(icon.button)
			
			frame = icon.button.frame
			clothing_unit = (icon_id, title)
			self.icons[icon_id] = Icon(clothing_unit, lambda x:frame, self.image_type, self.icon_button_pressed)
			self.scroll_view.add_subview(self.icons[icon_id].button)
		else:
			clothing_unit = (icon_id, title)
			self.icons[icon_id] = Icon(clothing_unit, self.next_icon_frame, self.image_type, self.icon_button_pressed)
			self.scroll_view.add_subview(self.icons[icon_id].button)
			
	def toggle_remove_mode(self, sender):
		if not self.remove_mode:
			self.add_remove_buttons_to_view()
			self.remove_mode = True
			sender.background_color = "bbfad0"
		else:
			self.remove_remove_buttons_from_view()
			self.remove_mode = False
			sender.background_color = "f0fff5"
			
	def prompt_remove(self, sender):
		icon = self.icons[sender.name]
		title = icon.title.text
		self.warning_view = Warning_View("Delete '"+title+"'?", "This will not be a complete deletion but simply delete from the category", self.remove_clothing_unit, self.cancel_remove, sender.name, self.outfit_saver)
		self.view.add_subview(self.warning_view)
		
		
	def cancel_remove(self, sender):
		self.view.remove_subview(self.warning_view)
		self.warning_view = None
		
	def add_remove_buttons_to_view(self):
		self.remove_buttons = []
		buffer = self.outfit_saver.screen_width*.0125
		for icon_id in self.icons:
			frame = self.icons[icon_id].button.frame
			name = icon_id
			center = (frame[0]+buffer, frame[1]+buffer)
			remove_button = Small_Remove_Button(self.prompt_remove, name, center, self.outfit_saver)
			self.scroll_view.add_subview(remove_button.button)
			self.remove_buttons.append(remove_button)
			
	def remove_remove_buttons_from_view(self):
		for button in self.remove_buttons:
			self.scroll_view.remove_subview(button.button)
			
	def remove_clothing_unit_icon(self, id):
		#save icons because remove_icons.. deletes it
		icons = self.icons
		self.remove_icons_from_view()
		self.icons = icons
		
		del self.icons[id]
				
		self.remove_remove_buttons_from_view()
		
		for icon_id in self.icons:
			icon = self.icons[icon_id]
			icon.button.frame = self.next_icon_frame(icon.image_ratio)
			
		self.put_icons_on_view()
		
		if self.remove_mode:
			self.add_remove_buttons_to_view()
		
		if self.warning_view != None:
			self.view.remove_subview(self.warning_view)
			self.warning_view = None
