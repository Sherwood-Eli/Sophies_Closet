import ui
import sqlite3

class Icon:
	def __init__(self, sql_data, get_frame, image_type, action):
		self.id = str(sql_data[0])
		self.name = sql_data[1]
		self.get_frame = get_frame
		self.image_type = image_type
		
		if len(sql_data) == 3:
			self.photo_path = sql_data[2]
			self.type = "c"
		else:
			self.photo_path = ""
			self.type = "o"
		
		if self.type == "o":
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
			
			if len(image_ids) > 0:
				#create image views
				x = 0
				images = []		
				for entry in image_ids:
					image_id = str(entry[0])
					image_path = "../images/"+self.image_type+"_thumbnails/"+image_id+".PNG"
					image = ui.Image.named(image_path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
					new_button = ui.Button(name=self.id, action=action)
					if x == 0:
						image_ratio = image.size[1]/image.size[0]
						self.image_ratio = image_ratio
						frame = self.get_frame(image_ratio)
						icon_width = frame[2]
						icon_height = icon_width*image_ratio
					new_image = ui.ImageView(image=image)
					new_image.frame = (0, 0, icon_width, icon_height)
					new_button.frame = ((x*icon_width), 0, icon_width, icon_height)
					new_image.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
					new_button.add_subview(new_image)
					images.append(new_button)
					x+=1
					
				scroll_view = ui.ScrollView()
				scroll_view.frame = (0, 0, icon_width, icon_height)
				scroll_view.content_size = (images[0].width*(len(images)), images[0].height)
				scroll_view.paging_enabled = True
				scroll_view.bounces = False
			
				#now add images to scroll view
				for image in images:
					scroll_view.add_subview(image)
				
				self.button = ui.View(border_color="black", name=self.id, border_width=2)
				self.button.frame=frame
				self.button.add_subview(scroll_view)
				
			else:
				frame = self.get_frame(0)
				self.image_ratio = 0
				self.button = ui.Button(frame=frame, border_color="black", border_width=2, name=self.id, action=action, background_color="f0fff5")
				
		
		#TODO can mess around with opening the directory and cding so you dont need to open the directory every time you open an image
		elif self.type == "c":
			frame = self.get_frame()
			self.button = ui.Button(border_color="black", border_width=2, name=self.id, action=action, background_color="f0fff5")
			self.button.frame = frame
			
			try:
				image = ui.Image.named("../images/background_thumbnails/"+self.photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
				self.button.add_subview(ui.ImageView(image=image, frame=(0, 0, frame[2], frame[3]), content_mode=ui.CONTENT_SCALE_ASPECT_FILL))
			except:
				pass
			
		self.button.corner_radius = self.button.width/10
		
		buffer = frame[2]/20
		self.title = ui.Label(frame = (buffer, buffer, frame[2]-(2*buffer), frame[3]-(2*buffer)))
		self.title.number_of_lines = 0
		self.title.line_break_mode = ui.LB_WORD_WRAP
		self.title.alignment = ui.ALIGN_LEFT
		self.title.text = self.name
		
		self.button.add_subview(self.title)
