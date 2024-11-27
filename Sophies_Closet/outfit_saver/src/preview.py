import ui
import sqlite3

#necessary changes to preview:
	#get rid of silly thpe system and have different preview vlasses that extend Preview

class Preview:
	def __init__(self, sql_data, get_frame, image_type, action):
		self.id = str(sql_data[0])
		self.action = action
		self.name = sql_data[1]
		self.get_frame = get_frame
		self.image_type = image_type
		
		if len(sql_data) == 3:
			self.photo_path = sql_data[2]
			self.type = "c"
		else:
			self.photo_path = ""
			self.type = "u"
		
		#if a clothing unit
		if self.type == "u":
			conn = sqlite3.connect('../db/outfit_saver.db')
			cursor = conn.cursor()
			
			sql = '''
			SELECT {}_image_id
			FROM "{}_images"
			WHERE {}_id="{}"
			'''.format(self.image_type, self.image_type, self.image_type, self.id)
			cursor.execute(sql)
			image_ids = cursor.fetchall()
			conn.close()
			
			self.images = []
			if len(image_ids) > 0:
				#temp_button is for when there is no images yet
				self.temp_button = None
				#create image views
				x = 0		
				for entry in image_ids:
					image_id = str(entry[0])
					image_path = "../images/"+self.image_type+"_thumbnails/"+image_id+".PNG"
					image = ui.Image.named(image_path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
					new_button = ui.Button(name=self.id, action=action)
					if x == 0:
						image_ratio = image.size[1]/image.size[0]
						self.image_ratio = image_ratio
						frame = self.get_frame(image_ratio)
						preview_width = frame[2]
						preview_height = preview_width*image_ratio
					new_image = ui.ImageView(image=image)
					new_image.frame = (0, 0, preview_width, preview_height)
					new_button.frame = ((x*preview_width), 0, preview_width, preview_height)
					new_image.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
					new_button.add_subview(new_image)
					new_button.image_view = new_image
					self.images.append(new_button)
					x+=1
			
			#if there are no images for this clothing unit yet
			else:
				frame = self.get_frame(0)
				preview_width = frame[2]
				preview_height = frame[3]
				self.image_ratio = 0
				self.temp_button = ui.Button(name=self.id, action=action, frame=(0, 0, preview_width, preview_height))
			
			scroll_view = ui.ScrollView()
			scroll_view.frame = (0, 0, preview_width, preview_height)
			scroll_view.content_size = (preview_width*(len(self.images)), preview_height)
			scroll_view.paging_enabled = True
			scroll_view.bounces = False
			self.scroll_view = scroll_view
		
			#now add images to scroll view
			for image in self.images:
				self.scroll_view.add_subview(image)
				
			#if there are no images, add temp button
			if self.temp_button != None:
				self.scroll_view.add_subview(self.temp_button)
			
			self.view = ui.View(border_color="black", name=self.id, border_width=2, background_color="f0fff5")
			self.view.frame=frame
			self.view.add_subview(scroll_view)
				
			
				
		
		#TODO can mess around with opening the directory and cding so you dont need to open the directory every time you open an image
		elif self.type == "c":
			frame = self.get_frame()
			self.view = ui.Button(border_color="black", border_width=2, name=self.id, action=action, background_color="f0fff5")
			self.view.frame = frame
			
			try:
				image = ui.Image.named("../images/background_thumbnails/"+self.photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
				
			except:
				image = None
				
			self.image_view = ui.ImageView(image=image, frame=(0, 0, frame[2], frame[3]), content_mode=ui.CONTENT_SCALE_ASPECT_FILL)
			self.view.add_subview(self.image_view)
			
		self.view.corner_radius = self.view.width/10
		
		buffer = frame[2]/20
		self.title = ui.Label(text_color="black", frame = (buffer, buffer, frame[2]-(2*buffer), frame[3]-(2*buffer)))
		self.title.number_of_lines = 0
		self.title.line_break_mode = ui.LB_WORD_WRAP
		self.title.alignment = ui.ALIGN_LEFT
		self.title.text = self.name
		
		self.view.add_subview(self.title)
		
		#params:
			#[0]new_name
			#[1]new_photo_path
			#[2]image_index (only for clothing unit)

	def update(self, params):
		if params[0] != None:
			self.name = params[0]
			
			self.title.text = self.name
			
		
		#handle image stuff
		if params[1] == None:
			return
		
		preview_width = self.view.frame[2]
		preview_height = self.view.frame[3]
		
		if self.type == "u":
			#figure out if removing image or appending image
			image_index = params[2]
			
			#if < 0 then we are just appending
			if image_index < 0:
				image_path = "../images/"+self.image_type+"_thumbnails/"+params[1]+".PNG"
				image = ui.Image.named(image_path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
				
				new_button = ui.Button(name=self.id, action=self.action)
				new_image = ui.ImageView(image=image)
				new_image.frame = (0, 0, preview_width, preview_height)
				new_button.frame = ((len(self.images)*preview_width), 0, preview_width, preview_height)
				new_image.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
				new_button.add_subview(new_image)
				new_button.image_view = new_image
				self.images.append(new_button)
				
				self.scroll_view.add_subview(new_button)
				self.scroll_view.content_size = (preview_width*(len(self.images)), preview_height)
			
			#else need to remove at index
			else:
				#shift
				for x in range(image_index+1, len(self.images)):
					self.images[x].frame = self.images[x-1].frame
					
					
				removed_image = self.images.pop(image_index)
				
				self.scroll_view.remove_subview(removed_image)
				self.scroll_view.content_size = (preview_width*(len(self.images)), preview_height)
				
					
		#else if category type
		else:
			self.photo_path = params[1]
			
			try:
				new_image = ui.Image.named("../images/background_thumbnails/"+self.photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
				
			except:
				new_image = None
			
			self.image_view.image = new_image
			
			
			
		
	
	
