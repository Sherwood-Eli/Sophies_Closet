import ui
import photos
import sqlite3
import os
import math
from PIL import Image
from io import BytesIO

from buttons import Back_Button, Title_Button, Import_Button, Top_Right_Add_Button, Camera_Button

class Image_Selector:
	def __init__(self, image_directory, thumbnail_directory, selected_image, return_function, outfit_saver, have_null_image, bg_color):
		self.image_directory = image_directory
		self.thumbnail_directory = thumbnail_directory
		self.selected_image = selected_image
		self.return_function = return_function
		self.outfit_saver = outfit_saver
		self.have_null_image = have_null_image
		
		self.add_options_visible = False
		self.warning_visible = False
		
		self.last_x = -1
		self.last_y = 0
		
		self.view = ui.View(background_color=bg_color, height=outfit_saver.screen_height, width=outfit_saver.screen_width)
		
		s_width = self.outfit_saver.screen_width
		s_height = self.outfit_saver.screen_height
		buffer = s_width/30
		
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
		
		self.back_button = Back_Button(self.close_view, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.back_button.button)
		
		self.title = Title_Button(image_directory, None, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.title.button)
		
		self.add_button = Top_Right_Add_Button(self.toggle_add_options, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.add_button.button)
		
		b_width = self.add_button.button.width
		b_height = self.add_button.button.height
		b_center = self.add_button.button.center
		
		self.add_options = ui.View(width=(1.5*b_width), height=(2.75*b_height), background_color="f0fff5", border_width=2)
		self.add_options.corner_radius = self.add_options.width/4
		self.add_options.center = (self.add_button.button.center[0], self.add_button.button.center[1]+(b_height*2))
		
		self.import_button = Import_Button(self.import_photo, outfit_saver.screen_width, outfit_saver.screen_height)
		self.import_button.button.center = (b_width*.75, b_width*.75)
		self.add_options.add_subview(self.import_button.button)
		
		self.camera_button = Camera_Button(self.take_photo, outfit_saver.screen_width, outfit_saver.screen_height)
		self.camera_button.button.center = (b_width*.75, b_width*2)
		self.add_options.add_subview(self.camera_button.button)
		
		frame=(s_width/5, s_height/3, s_width*(.6), s_height/5)
		self.importing_message = ui.View(frame=frame, border_width=2, background_color="orange")
		label = ui.Label(text="Importing image, \nplease wait...", frame=(buffer, buffer, frame[2]-(2*buffer), frame[3]-(2*buffer)), alignment=ui.ALIGN_CENTER, font=("<system-bold>", 20), number_of_lines=0, line_break_mode=ui.LB_WORD_WRAP)
		self.importing_message.corner_radius = self.importing_message.width/10
		self.importing_message.add_subview(label)
		
		self.scroll_view = ui.ScrollView()
		self.scroll_view.width = outfit_saver.screen_width
		self.scroll_view.height = outfit_saver.screen_height*.85
		self.scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.5)
		self.scroll_view.center = (outfit_saver.screen_width/2, outfit_saver.screen_height*.575)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.view.add_subview(self.scroll_view)
				
		self.put_images_on_view()
		self.outfit_saver.open_a_view(self)

		
	def open(self):
		self.outfit_saver.open_a_view(self)
		
	def toggle_add_options(self, sender):
		if self.add_options_visible:
			self.add_button.button.background_color = "f0fff5"
			self.view.remove_subview(self.add_options)
			self.add_options_visible = False
		else:
			self.add_button.button.background_color = "bbfad0"
			self.view.add_subview(self.add_options)
			self.add_options_visible = True
		
	def take_photo(self, sender):
		try:
			pil_img = photos.capture_image()
		except:
			return
		self.view.add_subview(self.importing_message)
		self.save_photo(pil_img)
		
	def import_photo(self, sender):
		Album_Picker_View(self.choose_import, self.outfit_saver)

	def choose_import(self, my_photo):
		#this works but it takes a long time
		#unfortunately converting it straight to PIL from the asset doesnt always work
		pil_img = Image.open(BytesIO(my_photo.get_ui_image().to_png()))
		self.save_photo(pil_img)
		
	@ui.in_background
	def save_photo(self, pil_img):
		if pil_img == None:
			return
		
		self.view.add_subview(self.importing_message)
		
		conn = sqlite3.connect('../db/outfit_saver.db')
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
		conn.close()
		image_id = str(last_row[0][0])
		pil_img.save("../images/"+self.image_directory+"/"+image_id+".PNG")
		
		thumbnail = self.convert_to_thumbnail(pil_img)
		thumbnail.save("../images/"+self.thumbnail_directory+"/"+image_id+".PNG")
		
		ui_img = ui.Image.named("../images/"+self.thumbnail_directory+"/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		
		frame = self.get_next_frame()
		button = self.create_button(frame, ui_img, image_id)
		self.images[image_id] = button
		self.scroll_view.add_subview(button)
		
		self.toggle_add_options(None)
		self.view.remove_subview(self.importing_message)
		
	def convert_to_thumbnail(self, image):
		image_ratio = image.size[1]/image.size[0]
		width = 256
		size = (width, int(width*image_ratio))
		return image.resize(size, Image.ANTIALIAS)
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def load_images(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT image_id
		FROM "images"
		WHERE image_directory="{}"
		'''.format(self.image_directory)
		cursor.execute(sql)
		image_ids = cursor.fetchall()
		conn.close()
		images = {}
		for entry in image_ids:
			try:
				image_id = str(entry[0])
				image = ui.Image.named("../images/"+self.thumbnail_directory+"/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
					
				frame = self.get_next_frame()
				images[image_id] = self.create_button(frame, image, image_id)
			except:
				pass
		
		return images
		
	def put_images_on_view(self):
		if self.have_null_image:
			frame = self.get_next_frame()
		
		self.images = self.load_images()
		
		if self.have_null_image:
			image = ui.Image.named("../images/button_images/none_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			button = self.create_button(frame, None, "0")
			image_view = ui.ImageView(width=button.width*.75, height=button.width*.75, center=(button.width*.5, button.height*.5), image=image)
			button.add_subview(image_view)
			
			self.images["0"] = button
		
		for image_id in self.images:
			self.scroll_view.add_subview(self.images[image_id])
		
		
	def create_button(self, frame, image, image_id):
		button = ui.Button(border_width=1, border_color = "black", frame=frame, action=self.select_image)
		button.corner_radius = button.width/10
		button.name = image_id
		button.image = image
		
		if image_id == self.selected_image:
			button.border_width = 5
			button.border_color = "bbfad0"
		
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
		image_id = sender.name
		
		if self.add_options_visible:
			self.toggle_add_options(None)
		
		if self.selected_image != "":
			old_selection = self.images[self.selected_image]
			old_selection.border_width = 1
			old_selection.border_color = "black"
			
			self.selected_image = image_id
			new_selection = self.images[image_id]
			new_selection.border_width = 5
			new_selection.border_color = "bbfad0"
		
		if image_id == "0":
			image = None
		else:
			image = ui.Image.named("../images/"+self.image_directory+"/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.return_function(image, image_id)
		
	def show_warning(self, warning_message):
		self.warning = ui.Label()
		
	def hide_warning(self):
		pass
	

class Album_Picker_View (ui.View):
	def __init__(self, return_function, outfit_saver):
		self.background_color = "white"
		self.width = outfit_saver.screen_width
		self.height = outfit_saver.screen_height
		self.return_function = return_function
		self.outfit_saver = outfit_saver
	
		self.add_subview(Back_Button(self.close_view, self.width, self.height).button)
		self.add_subview(Title_Button("Pick Album", None, self.width, self.height).button)
		
		self.b_buffer = self.width/30
		self.last_y = 0
		
		self.scroll_view = ui.ScrollView(frame=(0, self.height*.15, self.width, self.height*.85), content_size=(0,0))
		self.add_subview(self.scroll_view)
		albums = photos.get_smart_albums() + photos.get_albums()
		self.albums = albums
		for x in range(len(albums)):
			self.scroll_view.add_subview(self.create_album_button(albums[x], str(x)))
			
		self.outfit_saver.nav.push_view(self)
	
	def create_album_button(self, album, name):
		frame = (0, self.last_y, self.width, self.height*.1)
		self.last_y+=(self.height*.1)
		if self.last_y > self.scroll_view.height:
			self.scroll_view.content_size = (self.width, self.last_y)
		
		button = ui.Button(frame=frame, action=self.choose_album, border_width=1, name=name)
		button.add_subview(ui.Label(frame=(self.b_buffer, self.b_buffer, frame[2]-(2*self.b_buffer),frame[3]-(2*self.b_buffer)), alignment=ui.ALIGN_LEFT, text=album.title, text_color="black"))
		return button
		
	def choose_album(self, sender):
		my_photo = photos.pick_asset(self.albums[int(sender.name)])
		if type(my_photo) != type(None):
			self.close_view(None)
			self.return_function(my_photo)
	
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
	
		
