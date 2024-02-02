import ui
import photos
import sqlite3

from buttons import Add_Button, Back_Button, Cancel_Button, Save_Button, Title_Button, Image_Button, Title_Edit_Field
from image_selector import Image_Selector
from icon import Icon

class Category:
	def __init__(self, outfit_saver):
		self.outfit_saver = outfit_saver
		
		self.last_c1_y = outfit_saver.screen_width/30
		self.last_c2_y = outfit_saver.screen_width/30
			
		self.view = ui.View(background_color = "f0fff5", height = outfit_saver.screen_height, width = outfit_saver.screen_width)
		
		self.image_view = ui.ImageView(height = outfit_saver.screen_height*.85, width = outfit_saver.screen_width, content_mode=ui.CONTENT_SCALE_ASPECT_FILL)
		try:
			image = ui.Image.named("images/background_images/"+self.photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			self.image_view.image = image
		except:
			pass
		self.image_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		self.view.add_subview(self.image_view)
		
		
		self.scroll_view = ui.ScrollView()
		self.scroll_view.width = outfit_saver.screen_width
		self.scroll_view.height = outfit_saver.screen_height*.85
		self.scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.5)
		self.scroll_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.view.add_subview(self.scroll_view)
		
		self.title_button = Title_Button(self.title, self.edit_title, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.title_button.button)
		
		self.title_edit_field = Title_Edit_Field(self.title_button.button, self.change_title)
		
		self.add_button = Add_Button(self.add_button_pressed, outfit_saver)
		self.view.add_subview(self.add_button.button)
		
		self.back_button = Back_Button(self.close_view, self.outfit_saver.screen_width, self.outfit_saver.screen_height)
		self.view.add_subview(self.back_button.button)
		
		self.image_button = Image_Button(self.choose_background_image, self.outfit_saver.screen_width, self.outfit_saver.screen_height)
		self.view.add_subview(self.image_button.button)
		
		#TODO make sure view is pushed imediately, icons can be put on as soon as theyre ready
		self.outfit_saver.nav.push_view(self.view)
		self.icons = self.load_icons()
		self.put_icons_on_view()

		
	def add_button_pressed(self, sender):
		self.add_clothing_unit()
		
	def icon_button_pressed(self, sender):
		icon = self.icons[sender.name]
		self.open_clothing_unit(icon)
		
	def remove_icons_from_view(self):
		for id in self.icons:
			self.scroll_view.remove_subview(self.icons[id].button)
		self.icons = {}
		self.last_c1_y = outfit_saver.screen_width/30
		self.last_c2_y = outfit_saver.screen_width/30
		
	def put_icons_on_view(self):
		for id in self.icons:
			self.scroll_view.add_subview(self.icons[id].button)
			
	def next_icon_frame(self, image_ratio):
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
		Image_Selector("background_images", "background_thumbnails", self.photo_path, self.set_background_image, self.outfit_saver, True)
		
	def set_background_image(self, image, image_name):
		self.photo_path = image_name
		self.image_view.image = image
		self.save_category()
		
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def save_category(self):
		conn = sqlite3.connect('db/outfit_saver.db')
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
		
		
		
		#refresh icons
		#TODO could be more effieciently done
		#id must be non-null now please fix
		
		self.category_viewer.refresh_icons()
	
	def update_icon(self, icon_id, title):
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
