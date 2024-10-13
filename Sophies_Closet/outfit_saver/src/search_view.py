import ui
import os
import sqlite3
import math

from buttons import Back_Button, Title_Button

class Search_View:
	def __init__(self, search_title, search_query, image_query, image_directory, choose_icon, bg_color, outfit_saver):
		self.outfit_saver = outfit_saver
		self.search_title = search_title
		self.search_query = search_query
		self.image_query = image_query
		self.choose_icon = choose_icon
		self.image_directory = image_directory
		
		self.last_c1_y = outfit_saver.screen_width/30
		self.last_c2_y = outfit_saver.screen_width/30
		self.last_c3_y = outfit_saver.screen_width/30
		
		self.view = ui.View(background_color = bg_color, height = self.outfit_saver.screen_height, width = self.outfit_saver.screen_width)
		
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
		
		self.title = Title_Button(search_title, None, outfit_saver.screen_width, outfit_saver.screen_height)
		self.view.add_subview(self.title.button)
		
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		self.text_field = ui.TextField(frame=(screen_width*.1, screen_height*.1375, screen_width*.8, screen_height*.05), delegate=MyTextFieldDelegate(self), bordered=True)
		self.view.add_subview(self.text_field)
		
		self.scroll_view = ui.ScrollView()
		self.scroll_view.content_size = (outfit_saver.screen_width, outfit_saver.screen_height*.5)
		self.scroll_view.frame = (0, outfit_saver.screen_height*.2, outfit_saver.screen_width, outfit_saver.screen_height*.8)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.view.add_subview(self.scroll_view)
		
		self.icons = self.get_icons("")
		self.add_icons()
		
	def open(self):
		self.outfit_saver.open_a_view(self)
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def search(self, search_string):
		self.remove_icons()
		self.icons = self.get_icons(search_string)
		self.add_icons()
		
	def add_icons(self):
		for icon in self.icons:
			self.scroll_view.add_subview(self.icons[icon])
			
	def remove_icons(self):
		for icon in self.icons:
			self.scroll_view.remove_subview(self.icons[icon])
		self.last_c1_y = self.outfit_saver.screen_width/30
		self.last_c2_y = self.outfit_saver.screen_width/30
		self.last_c3_y = self.outfit_saver.screen_width/30
	
	def get_icons(self, search_string):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		{}"{}%"
		'''.format(self.search_query, search_string)
		cursor.execute(sql)
		rows = cursor.fetchall()
		icons = {}
		
		os.chdir("../images/"+self.image_directory)
		
		if len(rows) > 0:
			if len(rows[0]) == 2:
				#for items and outfits
				for row in rows:
					id = row[0]
					name = row[1]
					
					sql = '''
					{}"{}"
					'''.format(self.image_query, id)
					cursor.execute(sql)
					rows = cursor.fetchall()
					
					#just get the first one for each
					if len(rows) > 0:
						image_id = str(rows[0][0])
					else:
						image_id = "0"
					icons[id] = self.create_icon(id, image_id, name)
						
			elif len(rows[0]) == 3:
				#for categories
				for row in rows:
					id, name, image_id = row
					icons[id] = self.create_icon(id, image_id, name)
			
		os.chdir("../../src")
		
		conn.close()
			
		return icons
		
	def create_icon(self, id, image_id, name):
		#TODO rethink when titoes are needed
		if image_id != "0":
			image = ui.Image.named(image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			image_ratio = image.size[1]/image.size[0]
			frame = self.get_next_frame(image_ratio)
		else:
			image = None
			frame = self.get_next_frame(0)
		
		icon = ui.Button(name=str(id), action=self.choose_icon, frame=frame, border_width=2, border_color="black")
		icon.corner_radius = icon.width/10
		icon.image=image
		
		if name != "":
			buffer = frame[2]/20
			title = ui.Label(frame = (buffer, buffer, frame[2]-(2*buffer), frame[3]-(2*buffer)))
			title.number_of_lines = 0
			title.line_break_mode = ui.LB_WORD_WRAP
			title.alignment = ui.ALIGN_LEFT
			title.text = name
			
			icon.add_subview(title)
		
		return icon
		
		
	def get_next_frame(self, image_ratio):
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		
		buffer = screen_width/30
		
		width = (screen_width/3)-(2*buffer)
		if image_ratio == 0:
			height = (screen_height/5)-(2*buffer)
		else:
			height = width*image_ratio
		
		if self.last_c1_y <= self.last_c2_y and self.last_c1_y <= self.last_c3_y:
			frame = (buffer, self.last_c1_y, width, height)
			self.last_c1_y+=(buffer+height)
			if self.last_c1_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (screen_width, self.last_c1_y)
		elif self.last_c2_y <= self.last_c3_y:
			frame = (buffer+(screen_width/3), self.last_c2_y, width, height)
			self.last_c2_y+=(buffer+height)
			if self.last_c2_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (screen_width, self.last_c2_y)
		else:
			frame = (buffer+((2*screen_width)/3), self.last_c3_y, width, height)
			self.last_c3_y+=(buffer+height)
			if self.last_c3_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (screen_width, self.last_c3_y)
		
		return frame
		
	def show_warning(self, message):
		print(message)
		
		
		
		
		
class MyTextFieldDelegate (object):
	def __init__(self, search_view):
		self.search_view = search_view
	
	def textfield_did_change(self, textfield):
		self.search_view.search(textfield.text)
