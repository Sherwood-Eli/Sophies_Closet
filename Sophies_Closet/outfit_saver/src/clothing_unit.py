import ui
import sqlite3
import math
import os
from threading import Thread

#for testing:
import time

from buttons import  *
from warning_view import Warning_View

class Clothing_Unit:
	def __init__(self, id, category, caller_type, outfit_saver):
		self.id = id
		self.category = category
		self.caller_type = caller_type
		self.outfit_saver = outfit_saver
		
		self.title, self.score, self.note = self.get_sql_data()
		
		self.remove_mode = False



####################################################
####	Begin Image Icon Code 					####

	#Called from:
	#	Clothing_Unit_View.load_view
	#pwd when called: ~
	def load_image_icons(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT {}_image_id
		FROM "{}_images"
		WHERE {}_id="{}"
		'''.format(self.type, self.type, self.type, self.id)
		cursor.execute(sql)
		image_ids = cursor.fetchall()
		self.image_icons = {}
		
		for entry in image_ids:
			image_id = str(entry[0])
			image = ui.Image.named("../images/"+self.type+"_images/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			
			frame = self.get_next_image_frame()
			self.image_icons[image_id] = self.create_image_icon(frame, image, image_id)
			self.view.image_scroll_view.add_subview(self.image_icons[image_id])
			
			#View is presented once the first image is loaded
			if len(self.image_icons) == 1:
				self.outfit_saver.nav.push_view(self.view)
		
		if len(self.image_icons) < 5:
			frame = self.get_next_image_frame()
			if len(self.image_icons) == 0:
				self.image_icons["0"] = self.create_add_icon(frame, """No {} images yet :(""".format(self.type), self.add_image, 25)
			else:
				self.image_icons["0"] = self.create_add_icon(frame, "", self.add_image, 25)
			self.view.image_scroll_view.add_subview(self.image_icons["0"])
			if len(self.image_icons) == 1:
				self.outfit_saver.nav.push_view(self.view)
		
		conn.close()
	
	#Called from:
	#	Image_Selector.return_function
	#pwd when called: ~
	def choose_image(self, image, image_name):
		if self.id == None:
			self.create()
		
		if image_name in self.image_icons:
			self.image_selector.show_warning("Image already selected")
			return
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "{}_images" (
			"{}_image_id",
			"{}_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(self.type, self.type, self.type, int(image_name), int(self.id))
		
		result = cursor.execute(sql)
		conn.commit()
		conn.close()
		
		#Add new image icon to image scroll view
		frame = self.image_icons["0"].frame
		self.image_icons[image_name] = self.create_image_icon(frame, image, image_name)
		
		add_button = self.image_icons["0"]
		del self.image_icons["0"]
		#If there are now 5 images, get rid of the add button
		if len(self.image_icons) == 5:
			self.view.image_scroll_view.remove_subview(add_button)
		else:
			next_frame = self.get_next_image_frame()
			#If we are adding the first image, change the add button label to reflect that
			if len(self.image_icons) == 1:
				self.view.image_scroll_view.remove_subview(add_button)
				self.image_icons["0"] = self.create_add_icon(next_frame, "".format(self.type), self.add_image, 25)
			#Default case - make sure add image is at the end
			else:
				add_button.frame = next_frame
				self.image_icons["0"] = add_button
			self.view.image_scroll_view.add_subview(self.image_icons["0"])
		self.view.image_scroll_view.add_subview(self.image_icons[image_name])

		
		#Pops the image selector view
		self.outfit_saver.nav.pop_view()
		
		#TODO make icon get resized
		if self.caller_type == "c":
			self.category.update_icon(self.id, self.title, self.score)
	
	#Called by:
	#	self.get_image_icons()
	#	self.choose_image()
	def create_image_icon(self, frame, image, image_name):
		button = ui.Button(border_width=2, border_color = "black", frame=frame, action=self.select_image, background_color="f0fff5")
		button.corner_radius = button.width/10
		button.name = image_name
		button.image = image
		return button

	def get_next_image_frame(self):
		self.last_image_x+=1
		x = self.last_image_x
		
		screen_width = self.outfit_saver.screen_width
		screen_height = self.outfit_saver.screen_height
		scroll_view_width = screen_width
		scroll_view_height = screen_height*.7
		
		buffer = screen_width/30
		starting_x = (scroll_view_width*x)+(buffer)
		starting_y = (buffer)
		width = (screen_width)-(2*buffer)
		height = (scroll_view_height)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		if starting_x+width > self.view.image_scroll_view.content_size[1]:
			self.view.image_scroll_view.content_size = (starting_x+width+(buffer), scroll_view_height)

		return frame
		
####	End Image Icon Code 					####
####################################################

####################################################
####	Begin Link Icon Code 					####

	#Called from:
	#	Image_Selector.return_function
	#pwd when called: ~
	def load_link_icons(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT {}s.{}_id, {}_name
		FROM "{}s"
		INNER JOIN "outfit_items"
		ON {}s.{}_id = outfit_items.{}_id
		WHERE {}_id="{}"
		'''.format(self.link_type, self.link_type, self.link_type, self.link_type, self.link_type, self.link_type, self.link_type, self.type, self.id)
		cursor.execute(sql)
		item_ids = cursor.fetchall()
		conn.close()
		self.link_icons = {}
		for entry in item_ids:
			link_id = str(entry[0])
			link_name = entry[1]
			self.link_icons[link_id] = self.create_link_icon(link_id, link_name)
			self.view.link_scroll_view.add_subview(self.link_icons[link_id])

		#get icon for adding a link
		if len(item_ids) == 0:
			self.link_icons["0"] = self.create_add_icon(self.get_next_link_frame(),"No "+self.link_type+"s yet :(", self.add_link, 12)
		else:
			self.link_icons["0"] = self.create_add_icon(self.get_next_link_frame(),"", self.add_link, 12)
		self.view.link_scroll_view.add_subview(self.link_icons["0"])
	
	def choose_link(self, sender):
		link_id = sender.name
		
		if self.id == None:
			self.create()
		
		if link_id in self.link_icons:
			self.link_selector.show_warning("Link already selected")
			return
			
		#add outfit_item
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "outfit_items" (
			"{}_id",
			"{}_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(self.type, self.link_type, int(self.id), int(link_id))
		
		result = cursor.execute(sql)
		conn.commit()
		conn.close()
		
		#need this to keep "+" button at the end in view
		link_title = sender.subviews[0].text
		new_link = self.create_link_icon(link_id, link_title)
		new_frame = new_link.frame
		new_link.frame = self.link_icons["0"].frame
		add_button = self.link_icons["0"]
		if len(self.link_icons) == 1:
			#need to remake if adding the first image
			self.link_scroll_view.remove_subview(add_button)
			add_button = self.create_add_icon(new_frame, "", self.add_link, 0)
			self.link_scroll_view.add_subview(add_button)
		else:
			add_button.frame = new_frame
		self.link_icons[link_id] = new_link
		#to make sure the add button is at the end of the dictionary
		del self.link_icons["0"]
		self.link_icons["0"] = add_button
		
		self.link_scroll_view.add_subview(new_link)
		
		self.outfit_saver.nav.pop_view()
	
	def create_link_icon(self, link_id, link_name):
		frame = self.get_next_link_frame()
		
		button = ui.Button(border_width=2, border_color="black", frame=frame, background_color="f0fff5")
		button.corner_radius = button.width/10
		button.name = link_id
		
		buffer = frame[2]/20
		
		title = ui.Label(frame = (buffer, buffer, frame[2]-(2*buffer), frame[3]-(2*buffer)))
		title.number_of_lines = 0
		title.line_break_mode = ui.LB_WORD_WRAP
		title.alignment = ui.ALIGN_LEFT
		title.text = link_name
		button.add_subview(title)
		
		button.action = self.open_link
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT "{}_image_id"
		FROM "{}_images"
		WHERE {}_id="{}"
		'''.format(self.link_type, self.link_type, self.link_type, link_id)
		cursor.execute(sql)
		image_ids = cursor.fetchall()
		conn.close()
		
		#only take the first one
		if len(image_ids) != 0:
			image_id = str(image_ids[0][0])
			image = ui.Image.named("../images/"+self.link_type+"_thumbnails/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FILL, frame=(0,0,frame[2],frame[3]))
			image_view.image = image
			button.add_subview(image_view)
		
		return button
		
	def get_next_link_frame(self):
		if self.last_link_y == 1:
			self.last_link_y = -1
			self.last_link_x += 1
			
		self.last_link_y+=1
		x = self.last_link_x
		y = self.last_link_y
		
		
		scroll_view_width = self.view.link_scroll_view.width
		scroll_view_height = self.view.link_scroll_view.height
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
		
		if starting_x+width > self.view.link_scroll_view.content_size[0]:
			self.view.link_scroll_view.content_size = (starting_x+width+(buffer), scroll_view_height)

		return frame
		

####	End Link Icon Code 						####
####################################################

####################################################
####	Begin Category Icon Code 				####

	def load_category_icons(self):
		#the first category is implied
		if self.id == None:
			categories = {}
			category_id = self.category.id
			category_name = self.category.title
			photo_path = self.category.photo_path
			categories[category_id] = self.create_category_icon(category_id, category_name, photo_path)
			
			#get icon for adding a category
			category_id = "0"
			categories[category_id] = self.create_add_category_icon(self.get_next_category_frame(), "")
			return categories
			
		
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT {}_categories.category_id, {}_categories.category_name, {}_categories.photo_path
		FROM "{}_categories"
		INNER JOIN "category_{}s"
		ON {}_categories.category_id = category_{}s.category_id
		WHERE {}_id="{}"
		'''.format(self.type, self.type, self.type, self.type, self.type, self.type, self.type, self.type, self.id)
		cursor.execute(sql)
		rows = cursor.fetchall()
		conn.close()
		self.category_icons = {}
		for category in rows:
			category_id = str(category[0])
			self.category_icons[category_id] = self.create_category_icon(str(category[0]), str(category[1]), category[2])
			self.view.category_scroll_view.add_subview(self.category_icons[category_id])

		#get icon for adding a category
		category_id = "0"
		if len(rows) == 0:
			self.category_icons[category_id] = self.create_add_category_icon(self.get_next_category_frame(), "This {} is not in any categories :(")
		else:
			self.category_icons[category_id] = self.create_add_category_icon(self.get_next_category_frame(), "")
		self.view.category_scroll_view.add_subview(self.category_icons["0"])
		
	def choose_category(self, sender):
		category_id = sender.name
		
		if self.id == None:
			self.create()
 
		if category_id in self.category_icons:
			self.category_selector.show_warning("category already selected")
			return
			
		#add category_outfit
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		#insert into table
		sql = '''
		INSERT INTO "category_{}s" (
			"category_id",
			"{}_id"
			)
		VALUES (
			"{}",
			"{}"
			)
		'''.format(self.type, self.type, int(category_id), int(self.id))
		
		result = cursor.execute(sql)
		conn.commit()
		
		sql = '''
		SELECT category_name, photo_path
		FROM "{}_categories"
		WHERE category_id = {}
		'''.format(self.type, int(category_id))
		
		result = cursor.execute(sql)
		category = cursor.fetchall()
		category = category[0]
		
		conn.close()
		
		#need this to keep "+" button at the end
		new_category = self.create_category_icon(category_id, category[0], category[1])
		new_frame = new_category.frame
		new_category.frame = self.category_icons["0"].frame
		add_button = self.category_icons["0"]
		if len(self.category_icons) == 1:
			#need to remake if adding the first image
			self.category_scroll_view.remove_subview(add_button)
			add_button = self.create_add_category_icon(new_frame, "")
			self.category_scroll_view.add_subview(add_button)
		else:
			add_button.frame = new_frame
		self.category_icons[category_id] = new_category
		#to make sure the add button is at the end of the dictionary
		del self.category_icons["0"]
		self.category_icons["0"] = add_button
		
		self.category_scroll_view.add_subview(new_category)
		
		self.outfit_saver.nav.pop_view()()
		
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
		
		if starting_y+height > self.view.category_scroll_view.content_size[1]:
			self.view.category_scroll_view.content_size = (screen_width, starting_y+height+buffer)

		return frame
		
	def create_category_icon(self, category_id, category_name, photo_path):
		
		frame = self.get_next_category_frame()
		
		button = ui.Button(border_width=2, border_color="black", frame=frame, background_color="f0fff5")
		button.corner_radius = button.height/4
		button.name = category_id
		
		if photo_path != "0":
			image = ui.Image.named("../images/background_images/"+photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		else:
			image = None
		image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FILL, frame=(0,0,frame[2],frame[3]))
		button.action = None
		
		image_view.image = image
		button.add_subview(image_view)
		
		title = ui.Label(frame = (frame[0], frame[0], frame[2]-(2*frame[0]), frame[3]-(2*frame[0])))
		title.number_of_lines = 0
		title.line_break_mode = ui.LB_WORD_WRAP
		title.alignment = ui.ALIGN_LEFT
		title.text = category_name
		button.add_subview(title)
		
		return button
		
	def create_add_category_icon(self, frame, title_text):
		button = ui.Button(border_width=2, border_color="black", frame=frame, background_color="f0fff5")
		button.corner_radius = button.height/4
		
		image = ui.Image.named("../images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		image_view = ui.ImageView(height=button.height/2, width=button.height/2, center=(button.width/2, button.height/2))
		button.action = self.add_category
		
		title = ui.Label(frame = (frame[0], frame[0], frame[2]/3, frame[3]-(2*frame[0])))
		title.number_of_lines = 0
		title.line_break_mode = ui.LB_WORD_WRAP
		title.alignment = ui.ALIGN_LEFT
		title.text = title_text
		button.add_subview(title)
		
		image_view.image = image
		button.add_subview(image_view)
		return button

		

####	End Category Icon Code 					####
####################################################
		
	def set_title(self, sender):
		self.title = sender.text
		self.title_button.button.title = self.title
		self.view.remove_subview(self.title_edit_field.text_field)
		self.view.add_subview(self.title_button.button)
		
		self.save_title()
		
	def set_score(self, sender):
		new_score = sender.value
		self.score = round(new_score * 10, 1)
		sender.value = self.score/10
		self.score_label.text = str(self.score)+"/10"
		self.save_score()

		
	def select_image(self, sender):
		pass
		
	def close_view(self, sender):
		self.view.close_view()
		
		
	def create_add_icon(self, frame, title, action, font_size):
		button = ui.Button(frame=frame, background_color="f0fff5", border_width=2, action=action)
		button.corner_radius = button.width/10
		
		label = ui.Label(frame=(frame[2]/10, frame[2]/10, frame[2]-(frame[2]/5), frame[3]/5), text=title, font=("<system>", font_size), alignment=ui.ALIGN_CENTER, number_of_lines=0, line_break_mode=ui.LB_WORD_WRAP)
		button.add_subview(label)
		
		image_view = ui.ImageView(image=self.view.add_icon_PNG, width=button.width*.375, height=button.width*.375)
		image_view.center = (button.width/2, button.height/2)
		button.add_subview(image_view)
		
		return button
		
	def toggle_remove(self, sender):
		if self.id == None:
			return
		if self.remove_mode:
			self.remove_remove_buttons_from_view()
			self.remove_mode = False
			sender.background_color = "f0fff5"
		else:
			self.add_remove_buttons_to_view()
			self.remove_mode = True
			sender.background_color = "bbfad0"
			
	def add_remove_buttons_to_view(self):		
		buffer = self.outfit_saver.screen_width*.0125
		#image icons
		for id in self.image_icons:
			if id != "0":
				frame = self.image_icons[id].frame
				name = id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.remove_image, name, center, self.outfit_saver)
				self.view.image_scroll_view.add_subview(remove_button.button)
				self.image_remove_buttons.append(remove_button)
		for id in self.link_icons:
			if id != "0":
				frame = self.link_icons[id].frame
				name = id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.remove_link, name, center, self.outfit_saver)
				self.view.link_scroll_view.add_subview(remove_button.button)
				self.link_remove_buttons.append(remove_button)
		for id in self.category_icons:
			if id != "0":
				frame = self.category_icons[id].frame
				name = id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.remove_category, name, center, self.outfit_saver)
				self.view.category_scroll_view.add_subview(remove_button.button)
				self.category_remove_buttons.append(remove_button)
		
		#title view
		frame = self.title_button.button.frame
		name = "0"
		center = (frame[0]+buffer, frame[1]+buffer)
		remove_button = Small_Remove_Button(self.prompt_delete, name, center, self.outfit_saver)
		self.view.add_subview(remove_button.button)
		self.unit_remove_button = remove_button
		
			
			
	def remove_remove_buttons_from_view(self):
		for button in self.image_remove_buttons:
			self.view.image_scroll_view.remove_subview(button.button)
		for button in self.link_remove_buttons:
			self.view.link_scroll_view.remove_subview(button.button)
		for button in self.category_remove_buttons:
			self.view.category_scroll_view.remove_subview(button.button)
		self.view.remove_subview(self.unit_remove_button.button)
		self.image_remove_buttons = []
		self.link_remove_buttons = []
		self.category_remove_buttons = []
		self.unit_remove_button = None
		
	def remove_icon(self, id, remove_buttons, icons, view):
		x = len(remove_buttons)-1
		keys = list(icons.keys())
		#first move the add button
		if len(remove_buttons) < len(icons):
			icons["0"].center = icons[keys[x]].center
		while remove_buttons[x].button.name != id:
			remove_buttons[x].button.center = remove_buttons[x-1].button.center
			key = keys[x]
			next_key = keys[x-1]
			icons[key].center = icons[next_key].center
			
			x-=1
			
		view.remove_subview(remove_buttons[x].button)
		view.remove_subview(icons[id])
			
		remove_buttons.pop(x)
		del icons[id]
	
		
	def prompt_delete(self, sender):
		self.warning_view = Warning_View("Delete '"+self.title+"'?", "All data contained in this item and references to it will be deleted", self.delete, self.cancel_remove, self.title, self.outfit_saver)
		self.view.add_subview(self.warning_view)
		
		
	def cancel_remove(self, sender):
		self.view.remove_subview(self.warning_view)
		self.warning_view = None
		
		
class ScrollViewDelegate:
	def __init__(self, clothing_unit_view):
		self.clothing_unit_view = clothing_unit_view
		
	def scrollview_did_scroll(self, scrollview):
		if self.clothing_unit_view.note_view != None:
			self.clothing_unit_view.note_view.end_editing()
		
		
class TextViewDelegate:
	def __init__(self, clothing_unit_view):
		self.clothing_unit = clothing_unit_view
		
	def textview_did_end_editing(self, textview):
		self.clothing_unit_view.model.note = textview.text
		self.clothing_unit_view.model.save_note()



class Clothing_Unit_View(ui.View):
	def __init__(self, bg_color, outfit_saver):
		
	
