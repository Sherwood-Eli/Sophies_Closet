import ui
import photos
import sqlite3
import os
from PIL import Image

from buttons import Back_Button, Title_Button, Import_Button

class Image_Selector:
	def __init__(self, image_directory, thumbnail_directory, selected_image, return_function, outfit_saver, have_null_image):
		self.image_directory = image_directory
		self.thumbnail_directory = thumbnail_directory
		self.selected_image = selected_image
		self.return_function = return_function
		self.outfit_saver = outfit_saver
		self.have_null_image = have_null_image
		
		self.last_x = -1
		self.last_y = 0
		
		self.view = ui.View(background_color="f0fff5", height=outfit_saver.screen_height, width=outfit_saver.screen_width)
		
		self.back_button = Back_Button(self.close_view, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.back_button.button)
		
		self.title = Title_Button(image_directory, None, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.title.button)
		
		self.import_button = Import_Button(self.import_photo, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.import_button.button)
		
		self.scroll_view = ui.ScrollView()
		self.scroll_view.width = outfit_saver.screen_width
		self.scroll_view.height = outfit_saver.screen_height*.85
		self.scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.5)
		self.scroll_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.view.add_subview(self.scroll_view)
		
		self.put_images_on_view()
		
		self.outfit_saver.nav.push_view(self.view)
		
	def import_photo(self, sender):
		#TODO add error handling
		my_photo = photos.pick_asset()
		try:
			pil_img = my_photo.get_image()
			ui_img = my_photo.get_ui_image().with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		except:
			return 
		
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()

		#insert into table
		sql = '''
		INSERT INTO "images" (
			"image_directory")
		VALUES (
			"{}")
		'''.format(self.image_directory)
		
		
		cursor.execute(sql)
		conn.commit()
		sql='''
		select seq from sqlite_sequence where name="images"
		'''
		cursor.execute(sql)
		last_row=cursor.fetchall()
		image_id = str(last_row[0][0])
		
		pil_img.save("images/"+self.image_directory+"/"+image_id+".PNG")
		
		thumbnail = self.convert_to_thumbnail(pil_img)
		
		thumbnail.save("images/"+self.thumbnail_directory+"/"+image_id+".PNG")
		
		
		frame = self.get_next_frame()
		button = self.create_button(frame, ui_img, image_id)
		self.scroll_view.add_subview(button)
		
	def convert_to_thumbnail(self, image):
		image_ratio = image.size[1]/image.size[0]
		width = 256
		size = (width, int(width*image_ratio))
		return image.resize(size, Image.ANTIALIAS)
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def load_images(self):
		conn = sqlite3.connect('db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT image_id
		FROM "images"
		WHERE image_directory="{}"
		'''.format(self.image_directory)
		cursor.execute(sql)
		image_ids = cursor.fetchall()
		images = {}
		for entry in image_ids:
			frame = self.get_next_frame()
			image_id = str(entry[0])
			image = ui.Image.named("images/"+self.thumbnail_directory+"/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			
			images[image_id] = self.create_button(frame, image, image_id)
		
		return images
		
	def put_images_on_view(self):
		if self.have_null_image:
			frame = self.get_next_frame()
		
		images = self.load_images()
		
		if self.have_null_image:
			image = ui.Image.named("images/button_images/none_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			images["0"] = self.create_button(frame, image, "0")
		
		for image_id in images:
			self.scroll_view.add_subview(images[image_id])
		
		
	def create_button(self, frame, image, image_name):
		button = ui.Button(border_width=1, border_color = "black", frame=frame, action=self.select_image)
		button.corner_radius = button.width/10
		button.name = image_name
		button.image = image
		
		return button
		
	def get_next_frame(self):
		self.last_x+=1
		if self.last_x == 6:
			self.last_x = 0
			self.last_y += 1
		x = self.last_x
		y = self.last_y
		
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/60
		starting_x = (buffer)+((screen_width/6)*x)
		starting_y = ((screen_height/10)*y)+(buffer)
		width = (screen_width/6)-(2*buffer)
		height = (screen_height/10)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		if starting_y+height > self.scroll_view.content_size[1]:
			self.scroll_view.content_size = (screen_width, starting_y+height+(2*buffer))
			
		return frame
		
	def select_image(self, sender):
		print("selected:", sender.name)
		image_name = sender.name
		if image_name == "0":
			image = None
		else:
			image = ui.Image.named("images/"+self.image_directory+"/"+image_name+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.return_function(image, image_name)
		
	def show_warning(self, warning_message):
		print(warning_message)
	
