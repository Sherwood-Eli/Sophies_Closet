import ui
import time
import gc
import math
import photos
from io import BytesIO
from PIL import Image
from threading import Thread

from buttons import *
from preview import Preview
from outfit_category_viewer import Outfit_Category_Viewer
from item_category_viewer import Item_Category_Viewer
from outfit_category import Outfit_Category
from item_category import Item_Category
from outfit import Outfit
from item import Item
from image_selector import Image_Selector
from search import Search


#DESIGN DECISION JUSTIFICATIONS:
# - Each view keeps a stack of models and populates itself with the data for the top model,
#	this stack consists of strings so that we do not have to keep our memory full of objects.
#	Instead we create each object on demand, stressing the cpu, not the ram...

#DESIGN RULES
# The top two views on the view stack are the only views that MUST be loaded at all times.


#Preview management
# Have a preview stack for each view, the top of the preview stack is the id of the
# preview that is responsible for opening the current view. By sending this id to
# the nav view methods: remove_preview or edit_preview, we can ensure that preview
# management is done responsibly.


#TODO:
	# - make sure title edit field is set to correct value when opening edit field


#Reusable images
white_pattern = ui.Image.named("../images/button_images/white_pattern.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
colored_pattern = ui.Image.named("../images/button_images/colored_pattern.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
add_icon_PNG =  ui.Image.named("../images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
down_icon_PNG = ui.Image.named("../images/button_images/down_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
up_icon_PNG =  ui.Image.named("../images/button_images/up_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
panel_image = ui.Image.named("../images/button_images/white_panel.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)

#Reusable values
s_width, s_height = ui.get_screen_size()
const_buffer = s_width/30
rotation_angle = math.pi/18

#calculate dimentions of rotated pattern
#TODO if the rotation angle is larger than tan^-1(y/x), it might be messed up
if s_width > s_height:
	x = s_width
	y = s_height
else:
	y = s_width
	x = s_height
pattern_width = math.cos(rotation_angle)*((y*math.tan(rotation_angle))+x)



class Nav_View(ui.View):
	def __init__(self, outfit_saver):
		self.outfit_saver = outfit_saver
		
		self.view_stack = []
		self.duration = 0.35
		self.active_warning = None
		
		#initialize other views:
		self.root_view = Root_View(outfit_saver)
		self.all_views = {}
		self.all_views["outfit_category_viewer"] = Category_Viewer_View("97C1B0", "OUTFIT_CATEGORIES", Outfit_Category_Viewer, outfit_saver)
		self.all_views["item_category_viewer"] = Category_Viewer_View("DCBCDA", "ITEM_CATEGORIES", Item_Category_Viewer, outfit_saver)
		self.all_views["outfit_category"] = Category_View("97C1B0", Outfit_Category, outfit_saver)
		self.all_views["item_category"] = Category_View("DCBCDA", Item_Category, outfit_saver)
		self.all_views["outfit"] = Clothing_Unit_View("97C1B0", Outfit, outfit_saver)
		self.all_views["item"] = Clothing_Unit_View("DCBCDA", Item, outfit_saver)
		self.all_views["image_selector"] = Image_Selector_View(Image_Selector, outfit_saver)
		self.all_views["search"] = Search_View(Search, outfit_saver)

		self.add_subview(self.root_view)
			
	#returns the index of the newly pushed view
	def push_view(self, view_type, model_id, params):
		#get view
		cur_view = self.all_views[view_type]
		#pushes model to view and populates necessary stuff for viewing, sends the place view is in in view stack
		cur_view.push_model(len(self.view_stack), model_id, params)
		
		#Show view
		if len(cur_view.model_stack) == 1:
			#this means view is not actually in stack yet so need to add to subview
			self.add_subview(cur_view)
		else:
			#this means view is already presented so we just need to bring to front
			cur_view.bring_to_front()
		
		#Add new view+model pairing to nav_view view stack
		self.view_stack.append(view_type)
		
	def pop_view(self):
		#hide warning if theres a warning
		if self.active_warning != None:
			self.hide_warning()
		
		#pop view+model pairing from nav_view view stack
		popped_view = self.all_views[self.view_stack.pop(-1)]
		
		#get and prepare new cur view, if any
		if len(self.view_stack) != 0:
			cur_view = self.all_views[self.view_stack[-1]]
			
			#animate popped view close, revealing cur_view on top
			cur_view.bring_to_front()
			popped_view.bring_to_front()
			popped_view.send_to_back()
		
		#pops model from popped view and does initial steps for new model at top of model stack
		popped_view.pop_model()
		
		#removes popped view if no more models left
		if len(popped_view.model_stack) == 0:
			self.remove_subview(popped_view)
	
	#Removes the preview from the next view down on the stack
	def remove_preview(self, view_index, preview_id, params):
		if view_index > 0:
			self.all_views[self.view_stack[view_index-1]].remove_preview(preview_id, params)
	
	#Edits the preview on the next view down on the stack
	def edit_preview(self, view_index, preview_id, params):
		if view_index > 0:
			self.all_views[self.view_stack[view_index-1]].edit_preview(preview_id, params)
			
			
	def add_preview(self, view_index, preview_id, params):
		if view_index > 0:
			self.all_views[self.view_stack[view_index-1]].add_preview(preview_id, params)
			
	#returns category background_image if applicable
	def get_cur_category(self, category_type):
		if len(self.view_stack) > 1:
			return self.all_views[category_type+"_category"]
			
	def show_warning(self, primary_message, secondary_message, yes_action, no_action, id_to_delete):
		if self.active_warning != None:
			print("warning already active")
			return
		self.active_warning = Warning_View(primary_message, secondary_message, yes_action, no_action, id_to_delete)
		self.all_views[self.view_stack[-1]].add_subview(self.active_warning)
		
	def hide_warning(self):
		self.all_views[self.view_stack[-1]].remove_subview(self.active_warning)
		self.active_warning = None
		
		

##################################
#
# Root_View
#
##################################

class Root_View(ui.View):
	def __init__(self, outfit_saver):
		#initialize view properties
		self.background_color = "f0fff5"
		self.height = s_height
		self.width = s_width
		
		#initialize dimentions for root view buttons
		button_width = (self.width-(2*const_buffer))
		button_height = (self.height/2)-((3*const_buffer)+(const_buffer/2))
		
		if button_width > button_height:
			x = button_width
			y = button_height
		else:
			y = button_width
			x = button_height
		pattern_width = math.cos(rotation_angle)*((y*math.tan(rotation_angle))+x)
		
		#initialize "outfits" button
		outfit_button_frame = (const_buffer, 3*const_buffer, button_width, button_height)
		self.outfits_button = ui.Button(frame=outfit_button_frame, border_width=2, border_color="black", background_color="97C1B0", action=outfit_saver.open_outfit_category_viewer)
		#pattern view is calculated for full screen background not button background so may not be exactly right
		button_pattern_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(button_width/2, button_height/2))
		button_pattern_view.image = colored_pattern
		button_pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.outfits_button.add_subview(button_pattern_view)
		panel_view = ui.ImageView(frame=((3*const_buffer), (2*outfit_button_frame[3]/5), outfit_button_frame[2]-(6*const_buffer), outfit_button_frame[3]/5))
		panel_view.image = panel_image
		self.outfits_button.add_subview(panel_view)
		title_view = ui.ImageView(frame=(0, 2*const_buffer/3, outfit_button_frame[2]-(6*const_buffer), (outfit_button_frame[3]/5)-(const_buffer)), content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		title_image = ui.Image.named("../images/button_images/text_outfits_purple.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		title_view.image = title_image
		panel_view.add_subview(title_view)
		
		self.add_subview(self.outfits_button)
		
		
		#initialize "clothing items" button
		item_button_frame = (const_buffer, (self.height/2)+(const_buffer/2), button_width, button_height)
		self.items_button = ui.Button(frame=item_button_frame, border_width=2, border_color="black", background_color="DCBCDA", action=outfit_saver.open_item_category_viewer)
		button_pattern_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(button_width/2, button_height/2))
		button_pattern_view.image = colored_pattern
		button_pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.items_button.add_subview(button_pattern_view)
		panel_view = ui.ImageView(frame=((3*const_buffer), (2*outfit_button_frame[3]/5), outfit_button_frame[2]-(6*const_buffer), outfit_button_frame[3]/5))
		panel_view.image = panel_image
		self.items_button.add_subview(panel_view)
		title_view = ui.ImageView(frame=(0, 2*const_buffer/3, outfit_button_frame[2]-(6*const_buffer), (outfit_button_frame[3]/5)-(const_buffer)), content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		title_image = ui.Image.named("../images/button_images/text_clothingitems_purple.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		title_view.image = title_image
		panel_view.add_subview(title_view)
		
		self.add_subview(self.items_button)


##################################
#
# Stackable_View_Template
#
##################################

class Stackable_View_Template(ui.View):
	def __init__(self, Model_Class, outfit_saver):
		self.width = s_width
		self.height = s_height
		self.view_index_stack = []
		self.model_stack = []
		self.param_stack = []
		self.outfit_saver = outfit_saver
		self.Model = Model_Class
		self.model = None
		
		
	def push_model(self, view_index, model_id, params):
		#push model_id to model_stack
		self.view_index_stack.append(view_index)
		self.model_stack.append(model_id)
		self.param_stack.append(params)
		
		#get rid of old model stuff if exists and is different
		if self.model != None and self.model.id != model_id:
			self.depopulate_view()
			self.model = None
		
		#would be none if first model creation or previous model is deleted
		if self.model == None:
			#create model if doesnt exist
			self.model = self.Model(model_id, params, self, self.outfit_saver)
			self.populate_view(params)
		else:
			#Restore state of view if necessary
			self.prepare_for_open(params)
		
	def pop_model(self):
		self.view_index_stack.pop(-1)
		self.model_stack.pop(-1)
		params = self.param_stack.pop(-1)
		
		#get rid of old model stuff and replace if different
		if len(self.model_stack) != 0 and self.model.id != self.model_stack[-1]:
			self.depopulate_view()
			params = self.param_stack[-1]
			self.model = self.Model(self.model_stack[-1], params, self, self.outfit_saver)
			self.populate_view(params)
		else:
			#Restore state of view if necessary
			#TODO this might be in the wrong spot, maybe i need tohave this mot happen if there is no model
			self.prepare_for_open(params)
	
	

	
		
				
	def prepare_for_open(self, params):
		pass

	

##################################
#
# Category_Viewer_View
#
##################################

class Category_Viewer_View(Stackable_View_Template):
	def __init__(self, background_color, title, Model_Class, outfit_saver):
		self.background_color = background_color
		self.title = title
		super().__init__(Model_Class, outfit_saver)
		
		
		self.category_previews = {}
		self.remove_buttons = []
		self.remove_mode = False
		self.last_category_x = -1
		self.last_category_y = 0

			
		#Create background image
		image_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(s_width/2, s_height/2))
		image_view.image = white_pattern
		image_view.transform = ui.Transform.rotation(-rotation_angle)
		self.add_subview(image_view)
		
		#Scroll View
		self.scroll_view = Std_Scroll_View(s_width, s_height)
		self.add_subview(self.scroll_view.view)
		
		#Title Button: No action bc title not editable in this view
		view_title = Title_Button(self.title, None, s_width, s_height)
		self.add_subview(view_title.view)
		
		#Add_Button - Action added later
		self.add_button = Add_Button(self.add_category, s_width, s_height)
		self.add_subview(self.add_button.view)
		
		#Remove_Button
		self.remove_button = Remove_Button(self.toggle_remove_mode, s_width, s_height)
		self.add_subview(self.remove_button.view)
		
		#Back_Button
		back_button = Back_Button(self.back_button_press, s_width, s_height)
		self.add_subview(back_button.view)
		
		#Search_Button - Action add later
		self.search_button = Search_Button(self.open_search, s_width, s_height)
		self.add_subview(self.search_button.view)
	
	
	def populate_view(self, params):
		self.category_previews = self.load_category_previews()
		for id in self.category_previews:
			self.scroll_view.view.add_subview(self.category_previews[id].view)
		
	
	#Get rid of everything so we can save some memory
	def depopulate_view(self):
		for id in self.category_previews:
			self.scroll_view.view.remove_subview(self.category_previews[id].view)
		if self.remove_mode:
			self.toggle_remove_mode(self.remove_button)
		#Zero out these values
		self.category_previews = {}
		self.remove_buttons = []
		self.remove_mode = False
		self.last_category_x = -1
		self.last_category_y = 0
		
	
	#Retrieve category data from database then create icons for them
	def load_category_previews(self):
		categories = self.model.categories
		#Creating Icons
		category_previews = {}
		for category in categories:
			category_previews[str(category[0])] = Preview(category, self.next_icon_frame, "background", self.open_category)
		return category_previews
	
	
	#cant remove a category preview from anywhere other than the category viewer so i dont need a function to do that.
	
	
	def add_preview(self, preview_id, params):
		if preview_id not in self.category_previews:
			self.category_previews[preview_id] = Preview(params, self.next_icon_frame, "background", self.open_category)
			self.scroll_view.view.add_subview(self.category_previews[preview_id].view)
		
		
	def edit_preview(self, preview_id, params):
		self.category_previews[preview_id].update(params)
		
	
	
	
	#Wrapper for calling depop and pop
	def refresh_icons(self):
		self.depopulate_view()
		self.populate_view()
		
	def add_category(self, sender):
		if not self.remove_mode:
			self.model.open_category(None, None)
			
	def open_category(self, sender):
		if not self.remove_mode:
			self.model.open_category(sender.name, None)
	
	#Called by remove button
	def toggle_remove_mode(self, sender):
		if not self.remove_mode:
			#Start remove mode
			self.remove_buttons = []
			buffer = s_width*.0125
			#Create remove buttons for all category icons
			for category_id in self.category_previews:
				frame = self.category_previews[category_id].view.frame
				name = category_id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.prompt_remove_category, name, center, s_width, s_height)
				self.scroll_view.view.add_subview(remove_button.view)
				self.remove_buttons.append(remove_button)
			self.remove_mode = True
			sender.background_color = "bbfad0"
		else:
			#End remove mode
			for button in self.remove_buttons:
				self.scroll_view.view.remove_subview(button.view)
			self.remove_mode = False
			sender.background_color = "f0fff5"
	
	#Generates frames for category icons
	def next_icon_frame(self):
		self.last_category_x+=1
		if self.last_category_x == 3:
			self.last_category_x = 0
			self.last_category_y += 1
		x = self.last_category_x
		y = self.last_category_y

		
		buffer = s_width/30
		starting_x = (buffer)+((s_width/3)*x)
		starting_y = ((s_height/5)*y)+(buffer)
		width = (s_width/3)-(2*buffer)
		height = (s_height/5)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		#If frame is now past content size of scroll view, increase content size
		if starting_y+height > self.scroll_view.view.content_size[1]:
			self.scroll_view.view.content_size = (s_width, starting_y+height+(2*buffer))
			
		return frame
	
	#Shows warning window to make sure user wants to delete category
	def prompt_remove_category(self, sender):
		category_previews = self.category_previews[sender.name]
		title = category_previews.title.text
		self.outfit_saver.nav.show_warning("Delete '"+title+"'?", "All items in this catgory will continue to exist", self.remove_category, self.cancel_remove, sender.name)
		
	#Handle cancel remove
	def cancel_remove(self, sender):
		self.outfit_saver.nav.hide_warning()
		
	#Handle confirm remove
	def remove_category(self, sender):
		category_id = sender.name
		x = len(self.remove_buttons)-1
		category_keys = list(self.category_previews.keys())
		#shift categories over
		while self.remove_buttons[x].view.name != category_id:
			self.remove_buttons[x].view.center = self.remove_buttons[x-1].view.center
			key = category_keys[x]
			next_key = category_keys[x-1]
			self.category_previews[key].view.center = self.category_previews[next_key].view.center
			
			x-=1
			
		self.scroll_view.view.remove_subview(self.remove_buttons[x].view)
		self.scroll_view.view.remove_subview(self.category_previews[category_id].view)
			
		self.remove_buttons.pop(x)
		del self.category_previews[category_id]
		
		self.model.remove_category(category_id)
		
		
		#update scrollview dimentions and preview location variables
		self.last_category_x-=1
		if self.last_category_x == -1:
			self.last_category_x = 2
			self.last_category_y -= 1
		x = self.last_category_x
		y = self.last_category_y

		
		buffer = s_width/30
		starting_x = (buffer)+((s_width/3)*x)
		starting_y = ((s_height/5)*y)+(buffer)
		width = (s_width/3)-(2*buffer)
		height = (s_height/5)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		#If frame is now past content size of scroll view, increase content size
		if starting_y+height+(2*buffer) < self.scroll_view.view.content_size[1]:
			self.scroll_view.view.content_size = (s_width, starting_y+height+(2*buffer))
		
		self.outfit_saver.nav.hide_warning()
		
		
	def back_button_press(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def open_search(self, sender):
		if not self.remove_mode:
			self.model.open_search()


##################################
#
# Category_View
#
##################################

class Category_View(Stackable_View_Template):
	def __init__(self, bg_color, Model_Class, outfit_saver):
		super().__init__(Model_Class, outfit_saver)
		self.remove_mode = False
		self.remove_buttons = []
		self.bg_image = None
		
		self.last_c1_y = const_buffer
		self.last_c2_y = const_buffer
		
		#prepare the view
		self.background_color = bg_color
		
		pattern_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(s_width/2, s_height/2))
		pattern_view.image = white_pattern
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.add_subview(pattern_view)
		
		self.image_view = ui.ImageView(height = s_height*.85, width = s_width, content_mode=ui.CONTENT_SCALE_ASPECT_FILL)
		self.image_view.center = (s_width/2, s_height*.575)
		self.add_subview(self.image_view)
		
		self.scroll_view = Std_Scroll_View(s_width, s_height)
		self.add_subview(self.scroll_view.view)
		
		#Title_Button
		self.title_button = Title_Button("", self.edit_title, s_width, s_height)
		self.add_subview(self.title_button.view)
		self.title_edit_field = Title_Edit_Field(self.title_button.view, self.change_title)
	
		#Add_Button
		self.add_button = Add_Button(self.add_clothing_unit, s_width, s_height)
		self.add_subview(self.add_button.view)
		
		#Remove_Button
		remove_button = Remove_Button(self.toggle_remove_mode, s_width, s_height)
		self.add_subview(remove_button.view)
		
		#Back_Button
		self.back_button = Back_Button(self.close_view, s_width, s_height)
		self.add_subview(self.back_button.view)
		
		#Image_Button
		self.image_button = Image_Button(self.change_background_image, s_width, s_height)
		self.add_subview(self.image_button.view)
	
					
	def populate_view(self, params):
		#get bg_image
		try:
			self.bg_image = ui.Image.named("../images/background_images/"+self.model.photo_path+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			self.image_view.image = self.bg_image
		except:
			pass
		
		self.title_button.view.title = self.model.name
		self.title_edit_field.text_field.text = self.model.name
		self.put_previews_on_view()
			
	def put_previews_on_view(self):
		#load previews
		preview_data = self.model.load_preview_data()
		self.previews = {}
		for data in preview_data:
			id = str(data[0])
			preview = Preview(data, self.next_preview_frame, self.model.image_type, self.open_clothing_unit)
			self.previews[id] = preview
			self.scroll_view.view.add_subview(preview.view)
			print("adding", id)
			
	
	def depopulate_view(self):
		self.remove_previews_from_view()
		self.image_view.image = None
		
	def remove_previews_from_view(self):
		for id in self.previews:
			self.scroll_view.view.remove_subview(self.previews[id].view)
	
		self.icons = {}
		self.last_c1_y = const_buffer
		self.last_c2_y = const_buffer
		
		
	def add_preview(self, preview_id, params):
		self.previews[preview_id] = Preview(params, self.next_preview_frame, self.model.image_type, self.open_clothing_unit)
		self.scroll_view.view.add_subview(self.previews[preview_id].view)
		
		#in case the category is not created yet try to add it
		self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, self.model.name, ""))
		
		
	def edit_preview(self, preview_id, params):
		self.previews[preview_id].update(params)
		
	
	def remove_preview(self, preview_id, params):
		if preview_id in self.previews:
			self.remove_clothing_unit_preview(preview_id)
		
		
	
	def next_preview_frame(self, image_ratio):
		#TODO i want to make it so the scroll view is scrollable when an icon is past the top of the add button
		
		width =(s_width/2)-(2*const_buffer)
		if image_ratio == 0:
			height = (s_height/5)-(2*const_buffer)
		else:
			height = width*image_ratio
		
		if self.last_c1_y <= self.last_c2_y:
			frame = (const_buffer, self.last_c1_y, width, height)
			self.last_c1_y+=(const_buffer+height)
			if self.last_c1_y > self.scroll_view.view.content_size[1]:
				self.scroll_view.view.content_size = (s_width, self.last_c1_y)
		else:
			frame = (const_buffer+(s_width/2), self.last_c2_y, width, height)
			self.last_c2_y+=(const_buffer+height)
			if self.last_c2_y > self.scroll_view.view.content_size[1]:
				self.scroll_view.view.content_size = (s_width, self.last_c2_y)
	
		return frame
		
	def open_clothing_unit(self, sender):
		if not self.remove_mode:
			self.model.open_clothing_unit(sender.name)
		
	def add_clothing_unit(self, sender):
		if not self.remove_mode:
			self.model.open_clothing_unit(None)
		
	def edit_title(self, sender):
		self.remove_subview(self.title_button.view)
		self.add_subview(self.title_edit_field.text_field)
		self.title_edit_field.text_field.begin_editing()
		
	def change_title(self, sender): 
		new_title = sender.text
		
		self.remove_subview(self.title_edit_field.text_field)
		self.add_subview(self.title_button.view)
		
		if self.title_button.view.title == new_title: 
			return 
			
		self.title_button.view.title = new_title
		
		
		need_append = self.model.id == None
		
		self.model.save_category(new_title, self.model.photo_path)
		
		#update preview on previous screen
		if need_append:
			self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, new_title, ""))
		else:
			self.outfit_saver.nav.edit_preview(self.view_index_stack[-1], self.model.id, (new_title, None))
		
	def change_background_image(self, sender):
		if not self.remove_mode:
			self.model.change_background_image()
		
	def choose_background_image(self, image, image_name):
		self.image_view.image = image
		self.bg_image = image
		
		need_append = self.model.id == None
		
		self.model.save_category(self.model.name, image_name)
		
		#update preview on previous screen
		if need_append:
			self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, self.model.name, image_name))
		else:
			self.outfit_saver.nav.edit_preview(self.view_index_stack[-1], self.model.id, (None, image_name))
		
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
		preview = self.previews[sender.name]
		title = preview.title.text
		self.outfit_saver.nav.show_warning("Delete '"+title+"'?", "This will not be a complete deletion but simply delete from the category", self.remove_clothing_unit, self.cancel_remove, sender.name)
		
	def cancel_remove(self, sender):
		self.outfit_saver.nav.hide_warning()
		
	def remove_clothing_unit(self, sender):
		unit_id = sender.name
		
		self.model.remove_clothing_unit(unit_id)
		self.remove_clothing_unit_preview(unit_id)
		
		
	def add_remove_buttons_to_view(self):
		self.remove_buttons = []
		buffer = s_width*.0125
		for preview_id in self.previews:
			frame = self.previews[preview_id].view.frame
			name = preview_id
			center = (frame[0]+buffer, frame[1]+buffer)
			remove_button = Small_Remove_Button(self.prompt_remove, name, center, s_width, s_height)
			self.scroll_view.view.add_subview(remove_button.view)
			self.remove_buttons.append(remove_button)
			
	def remove_remove_buttons_from_view(self):
		for button in self.remove_buttons:
			self.scroll_view.view.remove_subview(button.view)
			
			
	#TODO this should be rewritten
	def remove_clothing_unit_preview(self, id):
		self.remove_previews_from_view()
		self.remove_remove_buttons_from_view()

		self.put_previews_on_view()
		
		if self.remove_mode:
			self.add_remove_buttons_to_view()
			
		self.outfit_saver.nav.hide_warning()
		
		
	def close_view(self, sender):
		#make sure title editing is terminated properly
		self.title_edit_field.text_field.text = self.title_button.view.title
		self.title_edit_field.text_field.end_editing()
		
		self.outfit_saver.nav.pop_view()
		

##################################
#
# Clothing_Unit_View
#
##################################

class Clothing_Unit_View(Stackable_View_Template):
	def __init__(self, bg_color, Model_Class, outfit_saver):
		super().__init__(Model_Class, outfit_saver)
		
		#initialize variables for view management
		self.zero_out_variables()
								
		#Default background
		self.background_color = bg_color
		pattern_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(s_width/2, s_height/2))
		pattern_view.image = white_pattern
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.add_subview(pattern_view)
		
		self.background_view = ui.ImageView(frame = (0, s_height*.15, s_width, s_height*.85), content_mode=ui.CONTENT_SCALE_ASPECT_FILL)
		self.add_subview(self.background_view)
	
		#main scroll view
		self.main_scroll_view = ui.ScrollView()
		self.main_scroll_view.frame = (0, int(s_height*.15), s_width, int(s_height*.85))
		self.main_scroll_view.border_width = 2
		self.main_scroll_view.paging_enabled = True
		self.main_scroll_view.bounces = False
		self.main_scroll_view.delegate = ScrollViewDelegate(self)
		self.main_scroll_view.shows_vertical_scroll_indicator = False
		self.main_scroll_view.content_size = (s_width, (self.main_scroll_view.height*3))
		self.add_subview(self.main_scroll_view)
		
		#image scroll view
		self.image_scroll_view = ui.ScrollView()
		self.image_scroll_view.frame = (0, 0, s_width, s_height*.7)
		self.image_scroll_view.content_size = (s_width, s_height*.7)
		self.image_scroll_view.border_width = 2
		self.image_scroll_view.paging_enabled = True
		self.image_scroll_view.bounces = False
		self.main_scroll_view.add_subview(self.image_scroll_view)
		
		#link scroll view
		self.link_scroll_view = ui.ScrollView()
		self.link_scroll_view.frame = (0, s_height*.9, s_width, s_height*.425)
		self.link_scroll_view.content_size = (s_width, s_height*.425)
		self.link_scroll_view.border_width=2
		self.main_scroll_view.add_subview(self.link_scroll_view)
		
		#category scroll view
		self.category_scroll_view = ui.ScrollView()
		self.category_scroll_view.frame = (0, s_height*1.325, s_width, s_height*.3)
		self.category_scroll_view.content_size = (s_width, s_height*.3)
		self.category_scroll_view.border_width = 2
		self.main_scroll_view.add_subview(self.category_scroll_view)
		
		#Back_Button
		self.back_button = Back_Button(self.close_view, s_width, s_height)
		self.add_subview(self.back_button.view)
		
		#Title_Button
		self.title_button = Title_Button("", self.edit_title, s_width, s_height)
		self.add_subview(self.title_button.view)
		self.title_edit_field = Title_Edit_Field(self.title_button.view, self.set_title)
		
		#Remove_Button
		self.remove_button = Top_Right_Button(None, s_width, s_height, "../images/button_images/minus_icon.PNG")
		self.add_subview(self.remove_button.view)
					
		temp_view = ui.View(frame=(const_buffer, (s_height*1.75)+const_buffer, s_width-(2*const_buffer), (s_height*.8)-(2*const_buffer)), background_color="f0fff5", border_width=2)
		temp_view.corner_radius = temp_view.width/10
		self.note_view = ui.TextView(frame=(const_buffer, const_buffer, s_width-(4*const_buffer), (s_height*.8)-(4*const_buffer)), font=('<system>', 20), delegate=TextViewDelegate(self), background_color=None)
		temp_view.add_subview(self.note_view)
		self.main_scroll_view.add_subview(temp_view)
		
		#score slider
		temp_view = ui.View(frame=(const_buffer, s_height*.725, s_width-(2*const_buffer), s_height*.05), border_width=2, background_color="f0fff5")
		temp_view.corner_radius = temp_view.height/3
		self.main_scroll_view.add_subview(temp_view)
		self.slider = ui.Slider(frame=(s_width*.1, s_height*.7, s_width*.5, s_height*.1))
		self.main_scroll_view.add_subview(self.slider)
		self.score_label = ui.Label(frame=(s_width*.7, s_height*.7, s_width*.2, s_height*.1), text_color="black")
		self.main_scroll_view.add_subview(self.score_label)
		
		#down icon pg 1
		frame = (s_width*.3, s_height*.8, s_width*.4, s_height*.025)
		down_icon = self.create_scroll_icon(frame, False)
		self.main_scroll_view.add_subview(down_icon)
		
		#up icon pg 2
		frame = (s_width*.3, s_height*.8625, s_width*.4, s_height*.025)
		up_icon = self.create_scroll_icon(frame, True)
		self.main_scroll_view.add_subview(up_icon)
		
		#down icon pg 2
		frame = (s_width*.3, s_height*1.65, s_width*.4, s_height*.025)
		down_icon = self.create_scroll_icon(frame, False)
		self.main_scroll_view.add_subview(down_icon)
		
		#up icon pg 3
		frame = (s_width*.3, s_height*1.7125, s_width*.4, s_height*.025)
		up_icon = self.create_scroll_icon(frame, True)
		self.main_scroll_view.add_subview(up_icon)

	def zero_out_variables(self):
		#variables for placing icons on view
		self.last_image_x = -1
		self.last_link_x = 0
		self.last_link_y = -1
		self.last_category_y = -1
		
		#toggleable buttons based on whether or not remove mode is active
		self.remove_mode = False
		self.image_remove_buttons = []
		self.link_remove_buttons = []
		self.category_remove_buttons = []
		self.title_edit_mode = False
		
		#stores all data on screen
		self.image_views = {}
		self.link_previews = {}
		self.category_previews = {}

	#adds a clothing unit model to be show on the view
	@ui.in_background
	def populate_view(self, params):
		
		t1 = Thread(target=self.load_image_views)
		t1.start()
		
		t2 = Thread(target=self.load_link_previews)
		t2.start()
		
		self.main_scroll_view.content_offset = (0, 0)
		self.image_scroll_view.content_offset = (0, 0)
		
		#Category background - no category background if accessed from search view
		bg_image = self.outfit_saver.nav.get_cur_category(self.model.type).bg_image
		if bg_image != None:
			self.background_view.image = bg_image
		self.title_button.view.title = self.model.title
		self.title_edit_field.text_field.text = self.model.title
		self.remove_button.view.action = self.toggle_remove_mode
		self.slider.action = self.set_score
		self.note_view.text = self.model.note
		self.score_label.text = str(self.model.score)+"/10"
		self.slider.value = self.model.score/10
		
		self.load_category_previews()
		
		t1.join()
		t2.join()
		
	def depopulate_view(self):
		if self.remove_mode:
			self.toggle_remove_mode(None)
		
			
		for image in self.image_views:
			self.image_scroll_view.remove_subview(self.image_views[image])
			
		for category in self.category_previews:
			self.category_scroll_view.remove_subview(self.category_previews[category])
		
		for link in self.link_previews:
			self.link_scroll_view.remove_subview(self.link_previews[link])
		
		self.zero_out_variables()
		
	def prepare_for_open(self, params):
		self.main_scroll_view.content_offset = (0, 0)
		self.image_scroll_view.content_offset = (0, 0)
		
	#this is only called when a link is updated
	def edit_preview(self, preview_id, params):
		print("hi")
		print(params)
		link = self.link_previews[preview_id]
		
		if params[0] != None:
			link.title_view.text = params[0]
		
		if params[1] != None:
			print("editing crap")
			image_index = params[2]
			
			#-1 means we are adding the first image
			if image_index == -1:
				path = "../images/"+self.model.link_type+"_thumbnails/"+params[1]+".PNG"
				print(path)
				new_image = ui.Image.named(path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
				link.image_view.image = new_image
			
			#0 means we are removing the first image
			elif image_index == 0:
				if params[1] != ":)":
					path = "../images/"+self.model.link_type+"_thumbnails/"+params[1]+".PNG"
					print(path)
					new_image = ui.Image.named(path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
					link.image_view.image = new_image
				else:
					link.image_view.image = None
		
	
	def remove_preview(self, preview_id, params):
		if preview_id in self.link_previews:
			self.remove_link_preview(preview_id)
		
	
####################################################
####				Begin Image Preview Code 						####
	
	def load_image_views(self):
		image_ids = self.model.load_image_data()
		for entry in image_ids:
			image_id = str(entry[0])
			image = ui.Image.named("../images/"+self.model.type+"_images/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			
			frame = self.get_next_image_frame()
			self.image_views[image_id] = self.create_image_view(frame, image, image_id)
			self.image_scroll_view.add_subview(self.image_views[image_id])
		
		#handle including add images button
		if len(self.image_views) < 5:
			frame = self.get_next_image_frame()
			if len(self.image_views) == 0:
				self.image_views["0"] = self.create_add_icon(frame, """No {} images yet :(""".format(self.model.type), self.add_image, 25)
			else:
				self.image_views["0"] = self.create_add_icon(frame, "", self.add_image, 25)
			self.image_scroll_view.add_subview(self.image_views["0"])
			
	def create_image_view(self, frame, image, image_name):
		button = ui.Button(border_width=2, border_color = "black", frame=frame, background_color="f0fff5")
		button.corner_radius = button.width/10
		button.name = image_name
		button.image = image
		return button
		
	def choose_image(self, image, image_id):
		if image_id in self.image_views:
			self.show_temporary_warning("No adding the same image twice please", .5)
			return
		
		#add image to clothing unit view
		self.append_image_view(image, image_id)
		
		need_append = self.model.id == None
		
		self.model.save_image(image_id)
		
		#update preview on previous screen
		if need_append:
			self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, self.model.title))
		else:
			self.outfit_saver.nav.edit_preview(self.view_index_stack[-1], self.model.id, (None, image_id, (-1*len(self.image_views)+1)))
		
		#pop image selector view
		self.outfit_saver.nav.pop_view()
	
	def append_image_view(self, image, image_id):
		add_button = self.image_views["0"]
		frame = add_button.frame
		add_button.frame = self.get_next_image_frame()
		self.image_views[image_id] = self.create_image_view(frame, image, image_id)
		self.image_scroll_view.add_subview(self.image_views[image_id])
		
		#make sure add button is at the end
		del self.image_views["0"]
		self.image_views["0"] = add_button
		
		
		#If we are adding the first image, change the add button label to reflect that
		if len(self.image_views) == 2:
			add_button.label_view.text = ""
	
	def get_next_image_frame(self):
		self.last_image_x+=1
		x = self.last_image_x
		
		scroll_view_width = s_width
		scroll_view_height = s_height*.7
		
		buffer = s_width/30
		starting_x = (scroll_view_width*x)+(buffer)
		starting_y = (buffer)
		width = (s_width)-(2*buffer)
		height = (scroll_view_height)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		#by doing x < 5, we dont increase scrollview size if there are already 5 images
		if x < 5 and starting_x+width > self.image_scroll_view.content_size[1]:
			self.image_scroll_view.content_size = (starting_x+width+(buffer), scroll_view_height)

		return frame
	
	#opens image selector
	def add_image(self, sender):
		if not self.remove_mode:
			self.model.add_image()
	
	def remove_image(self, sender):
		image_id = sender.name
		
		self.model.remove_image(image_id)
		
		#removes undesired view and shifts all if necessary
		index = self.remove_icon(image_id, self.image_remove_buttons, self.image_views, self.image_scroll_view)
		
		# remove last frame
		self.last_image_x -= 1
		
		if len(self.image_views) == 1:
			self.image_views["0"].label_view.text = "No "+self.model.type+" images yet :("
		
		#this should always make it the right size even if we are removing a 5th image
		last_frame = self.image_views["0"].frame
		self.image_scroll_view.content_size = (last_frame[0]+last_frame[2]+const_buffer, self.image_scroll_view.content_size[1])
		
		
		#Have preview reflect change if it is still in memory
		
		#if there is new first image, pass the image id so that if the caller is a link preview it gets updated
		if index == 0 and len(self.image_views) > 1:
			replacement_id = list(self.image_views.keys())[0]
		else:
			replacement_id = ":)"
		self.outfit_saver.nav.edit_preview(self.view_index_stack[-1], self.model.id, (None, replacement_id, index))
		
		
####		End Image view Code 				####
####################################################

####################################################
####		Begin Link Preview Code 			####
		
	def load_link_previews(self):
		item_ids = self.model.load_link_data()
		
		for entry in item_ids:
			link_id = str(entry[0])
			link_name = entry[1]
			self.link_previews[link_id] = self.create_link_preview(self.get_next_link_frame(), link_id, link_name)
			self.link_scroll_view.add_subview(self.link_previews[link_id])

		#include add link button
		if len(item_ids) == 0:
			self.link_previews["0"] = self.create_add_icon(self.get_next_link_frame(),"No "+self.model.link_type+"s yet :(", self.add_link, 12)
		else:
			self.link_previews["0"] = self.create_add_icon(self.get_next_link_frame(),"", self.add_link, 12)
		self.link_scroll_view.add_subview(self.link_previews["0"])
		
	def create_link_preview(self, frame, link_id, link_name):
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
		button.title_view = title
		
		button.action = self.open_link
		
		image_ids = self.model.get_link_images(link_id)

		#only take the first one
		if len(image_ids) != 0:
			image_id = str(image_ids[0][0])
			image = ui.Image.named("../images/"+self.model.link_type+"_thumbnails/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		else:
			image = None
		image_view = ui.ImageView(content_mode=ui.CONTENT_SCALE_ASPECT_FILL, frame=(0,0,frame[2],frame[3]))
		image_view.image = image
		button.add_subview(image_view)
		button.image_view = image_view
		
		return button
		
	def choose_link(self, sender):
		link_id = sender.name
		title = sender.subviews[0].text
		
		if link_id in self.link_previews:
			self.show_temporary_warning("No adding the same link twice please", .5)
			return
		
		need_append = self.model.id == None
		
		#update model
		self.model.save_link(link_id)
			
		#add link to clothing unit view
		self.append_link_preview(link_id, title)
		
		#update previews on previous view
		if need_append:
			self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, self.model.name))
		
		#pop link selector view
		self.outfit_saver.nav.pop_view()
	
	
		
	def append_link_preview(self, link_id, link_title):
		#need this to keep "+" button at the end in view
		new_link = self.create_link_preview(self.link_previews["0"].frame, link_id, link_title)
		add_button = self.link_previews["0"]
		add_button.frame = self.get_next_link_frame()
		if len(self.link_previews) == 1:
			#need to remake if adding the first image
			add_button.label_view.text = "No outfit items yet :("
		
		self.link_previews[link_id] = new_link
		#to make sure the add button is at the end of the dictionary
		del self.link_previews["0"]
		self.link_previews["0"] = add_button
		
		self.link_scroll_view.add_subview(new_link)
		
	def get_next_link_frame(self):
		if self.last_link_y == 1:
			self.last_link_y = -1
			self.last_link_x += 1
			
		self.last_link_y+=1
		x = self.last_link_x
		y = self.last_link_y
		
		
		scroll_view_width = self.link_scroll_view.width
		scroll_view_height = self.link_scroll_view.height
		
		buffer = s_width/30
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
		
	def open_link(self, sender):
		if not self.remove_mode:
			self.outfit_saver.nav.push_view(self.model.link_type, sender.name, sender.name)
		
	def add_link(self, sender):
		if not self.remove_mode:
			self.model.add_link()
		
	def remove_link(self, sender):
		link_id = sender.name
		self.remove_link_preview(link_id)
		
	def remove_link_preview(self, link_id):
		#remove from model
		self.model.remove_link(link_id)
		
		self.remove_icon(link_id, self.link_remove_buttons, self.link_previews, self.link_scroll_view)
		
		if len(self.link_previews) == 1:
			 self.link_previews["0"].label_view.text = "No outfit items yet :("
		
		if self.last_link_y == 0:
			self.last_link_x -= 1
			self.last_link_y = 1
		else:
			self.last_link_y = 0
		buffer = s_width/30
		last_frame = self.link_previews["0"].frame
		self.link_scroll_view.content_size = (last_frame[0]+last_frame[2]+buffer, self.link_scroll_view.content_size[1])
	
	
####	End Link Icon Code 						####
####################################################

####################################################
####	Begin Category Icon Code 				####


	def load_category_previews(self):
		#the first category is implied
		self.category_previews = {}
		if self.model.id == None:
			category = self.outfit_saver.nav.get_cur_category(self.model.type).model
			self.category_previews[category.id] = self.create_category_preview(self.get_next_category_frame(), category.id, category.name, category.photo_path)
			self.category_scroll_view.add_subview(self.category_previews[category.id])
		else:
			data = self.model.load_all_category_data()
			self.category_previews = {}
			for category in data:
				category_id = str(category[0])
				self.category_previews[category_id] = self.create_category_preview(self.get_next_category_frame(), str(category[0]), str(category[1]), category[2])
				self.category_scroll_view.add_subview(self.category_previews[category_id])

		#get icon for adding a category
		category_id = "0"
		if len(self.category_previews) == 0:
			self.category_previews[category_id] = self.create_add_category_icon(self.get_next_category_frame(), "This {} is not in any categories :(".format(self.model.type))
		else:
			self.category_previews[category_id] = self.create_add_category_icon(self.get_next_category_frame(), "")
		self.category_scroll_view.add_subview(self.category_previews["0"])
		
	
	def choose_category(self, sender):
		category_id = sender.name
 
		if category_id in self.category_previews:
			self.show_temporary_warning("category already selected", .5)
			return
			
		need_append = self.model.id == None
			
		#update model
		self.model.save_category(category_id)
		
		#add link to clothing unit view
		self.append_category_preview(category_id)
		
		if need_append:
			self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, self.model.name))
		
		#pop link selector view
		self.outfit_saver.nav.pop_view()
		
		
	def append_category_preview(self, category_id):
		data = self.model.load_single_category_data(category_id)[0]
		
		add_button = self.category_previews["0"]
		del self.category_previews["0"]
		
		new_category = self.create_category_preview(add_button.frame, category_id, data[1], data[2])
		self.category_previews[category_id] = new_category
		self.category_scroll_view.add_subview(new_category)
		
		add_button.frame = self.get_next_category_frame()
		
		#if this was the first category, change the text on add button
		if len(self.category_previews) == 1:
			add_button.label_view.text = ""
			
		self.category_previews["0"] = add_button
	
		
	def get_next_category_frame(self):
		self.last_category_y += 1
		y = self.last_category_y
		
		width = s_width-(2*const_buffer)
		height = (s_height/10)
		starting_x = (const_buffer)
		starting_y = const_buffer+(height+const_buffer)*y
		
		frame=(starting_x, starting_y, width, height)
		
		if starting_y+height > self.category_scroll_view.content_size[1]:
			self.category_scroll_view.content_size = (s_width, starting_y+height+const_buffer)

		return frame
		
	def create_category_preview(self, frame, category_id, category_name, photo_path):
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
		
		button.label_view = ui.Label(frame = (frame[0], frame[0], frame[2]/3, frame[3]-(2*frame[0])))
		button.label_view.number_of_lines = 0
		button.label_view.line_break_mode = ui.LB_WORD_WRAP
		button.label_view.alignment = ui.ALIGN_LEFT
		button.label_view.text = title_text
		button.add_subview(button.label_view)
		
		image_view.image = image
		button.add_subview(image_view)
		return button
		
	def add_category(self, sender):
		if not self.remove_mode:
			self.model.add_category()
	
	def remove_category(self, sender):
		category_id = sender.name
		self.remove_icon(category_id, self.category_remove_buttons, self.category_previews, self.category_scroll_view)
		
		if len(self.category_previews) == 1:
			self.category_previews["0"].label_view.text = "This {} is not in any categories :(".format(self.model.type)
		
		self.last_category_y -= 1
		buffer = s_width/30
		last_frame = self.category_previews["0"].frame
		self.category_scroll_view.content_size = (self.category_scroll_view.content_size[0], last_frame[1]+last_frame[3]+buffer)
		
		self.model.remove_category(category_id)
		
		#remove self from category view if necessary

####	End Category Icon Code 					####
####################################################

	
	def create_add_icon(self, frame, title, action, font_size):
		button = ui.Button(frame=frame, background_color="f0fff5", border_width=2, action=action)
		button.corner_radius = button.width/10
		
		label = ui.Label(frame=(frame[2]/10, frame[2]/10, frame[2]-(frame[2]/5), frame[3]/5), text=title, font=("<system>", font_size), alignment=ui.ALIGN_CENTER, number_of_lines=0, line_break_mode=ui.LB_WORD_WRAP)
		button.add_subview(label)
		button.label_view = label
		
		image_view = ui.ImageView(image=add_icon_PNG, width=button.width*.375, height=button.width*.375)
		image_view.center = (button.width/2, button.height/2)
		button.add_subview(image_view)
		
		return button
		
		
	def toggle_remove_mode(self, sender):
		if self.model.id == None:
			return
		if self.remove_mode:
			self.remove_remove_buttons_from_view()
			self.remove_mode = False
			self.remove_button.view.background_color = "f0fff5"
		else:
			if self.title_edit_mode:
				self.title_edit_field.text_field.text = self.title_button.view.title
				self.title_edit_field.text_field.end_editing()
			self.add_remove_buttons_to_view()
			self.remove_mode = True
			self.remove_button.view.background_color = "bbfad0"
			
			
	def add_remove_buttons_to_view(self):		
		buffer = s_width*.0125
		#image icons
		for id in self.image_views:
			if id != "0":
				frame = self.image_views[id].frame
				name = id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.remove_image, name, center, s_width, s_height)
				self.image_scroll_view.add_subview(remove_button.view)
				self.image_remove_buttons.append(remove_button)
		for id in self.link_previews:
			if id != "0":
				frame = self.link_previews[id].frame
				name = id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.remove_link, name, center, s_width, s_height)
				self.link_scroll_view.add_subview(remove_button.view)
				self.link_remove_buttons.append(remove_button)
		for id in self.category_previews:
			if id != "0":
				frame = self.category_previews[id].frame
				name = id
				center = (frame[0]+buffer, frame[1]+buffer)
				remove_button = Small_Remove_Button(self.remove_category, name, center, s_width, s_height)
				self.category_scroll_view.add_subview(remove_button.view)
				self.category_remove_buttons.append(remove_button)
		
		#title view
		frame = self.title_button.view.frame
		name = "0"
		center = (frame[0]+buffer, frame[1]+buffer)
		remove_button = Small_Remove_Button(self.prompt_delete, name, center, s_width, s_height)
		self.add_subview(remove_button.view)
		self.unit_remove_button = remove_button
		
			
			
	def remove_remove_buttons_from_view(self):
		for button in self.image_remove_buttons:
			self.image_scroll_view.remove_subview(button.view)
		for button in self.link_remove_buttons:
			self.link_scroll_view.remove_subview(button.view)
		for button in self.category_remove_buttons:
			self.category_scroll_view.remove_subview(button.view)
		self.remove_subview(self.unit_remove_button.view)
		self.image_remove_buttons = []
		self.link_remove_buttons = []
		self.category_remove_buttons = []
		self.unit_remove_button = None
		
	def remove_icon(self, id, remove_buttons, icons, view):
		keys = list(icons.keys())
		x = len(list(icons.keys()))-2
		#first move the add button
		if "0" in icons:
			icons["0"].center = icons[keys[x]].center
		while keys[x] != id:
			#this is not true when removing from an opened preview
			if len(remove_buttons) > 0:
				remove_buttons[x].view.center = remove_buttons[x-1].view.center
			key = keys[x]
			next_key = keys[x-1]
			icons[key].center = icons[next_key].center
			
			x-=1
		
		if len(remove_buttons) > 0:
			view.remove_subview(remove_buttons[x].view)
			remove_buttons.pop(x)
		
		view.remove_subview(icons[id])
		del icons[id]
		
		return x
		
	def prompt_delete(self, sender):
		self.outfit_saver.nav.show_warning("Delete '"+self.model.title+"'?", "All data contained in this item and references to it will be deleted", self.delete, self.cancel_remove, self.model.id)
		
	def delete(self, sender):
		if self.model.id != None:
			self.model.delete()
		
		self.outfit_saver.nav.remove_preview(self.view_index_stack[-1], self.model.id, None)
		
		self.outfit_saver.nav.pop_view()
		
		
	def cancel_remove(self, sender):
		self.outfit_saver.nav.hide_warning()

	
	@ui.in_background
	def show_temporary_warning(self, message, num_secs):
		self.outfit_saver.nav.show_warning("", message, None, None, None)
		time.sleep(num_secs)
		self.outfit_saver.nav.hide_warning()
	
	#closes the top view, opens the next view
	def close_view(self, sender):
		#if edit title mode is on, we want to restore the title to what it originally was
		if self.title_edit_mode:
			self.title_edit_field.text_field.text = self.title_button.view.title
			self.title_edit_field.text_field.end_editing()
		
		self.outfit_saver.nav.pop_view()
		
	def put_icons_on_view(self, view, icons):
		for icon in icons:
			view.add_subview(icons[icon])
			
	def remove_icons_from_view(self, view):
		for subview in view.subviews:
			view.remove_subview(subview)
			
	def edit_title(self, sender):
		if not self.remove_mode:
			self.remove_subview(self.title_button.view)
			self.add_subview(self.title_edit_field.text_field)
			self.title_edit_mode = True
			self.title_edit_field.text_field.begin_editing()
			
	
	#this will only be called as an action from text view	
	def set_title(self, sender):
		if sender.text != self.title_button.view.title:
			title = sender.text
			self.title_button.view.title = title
			
			need_append = self.model.id == None
			
			self.model.save_title(title)
			
			#update preview on previous screen
			if need_append:
				self.outfit_saver.nav.add_preview(self.view_index_stack[-1], self.model.id, (self.model.id, self.model.title))
			else:
				self.outfit_saver.nav.edit_preview(self.view_index_stack[-1], self.model.id, (title, None))
		
		self.remove_subview(self.title_edit_field.text_field)
		self.add_subview(self.title_button.view)
		
		self.title_edit_mode = False
		
	def set_score(self, sender):
		new_score = round(sender.value * 10, 1)
		sender.value = new_score/10
		self.score_label.text = str(new_score)+"/10"
		self.model.save_score(new_score)
		
			
	def create_scroll_icon(self, frame, up_icon):
		if up_icon:
			image = up_icon_PNG
		else:
			image = down_icon_PNG
		icon = ui.ImageView(frame=frame)
		icon.image = image
		return icon



##################################
#
# Image_Selector_View
#
##################################

class Image_Selector_View(Stackable_View_Template):
	def __init__(self, Model, outfit_saver):
		super().__init__(Model, outfit_saver)
		
		self.zero_out_variables()
		
		pattern_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(s_width/2, s_height/2))
		pattern_view.image = white_pattern
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.add_subview(pattern_view)
		
		self.back_button = Back_Button(self.close_view, s_width, s_height)
		self.add_subview(self.back_button.view)
		
		self.title = Title_Button("", None, s_width, s_height)
		self.add_subview(self.title.view)
		
		self.add_button = Top_Right_Add_Button(self.toggle_add_options, s_width, s_height)
		self.add_subview(self.add_button.view)
		
		b_width = self.add_button.view.width
		b_height = self.add_button.view.height
		b_center = self.add_button.view.center
		
		self.add_options = ui.View(width=(1.5*b_width), height=(2.75*b_height), background_color="f0fff5", border_width=2)
		self.add_options.corner_radius = self.add_options.width/4
		self.add_options.center = (self.add_button.view.center[0], self.add_button.view.center[1]+(b_height*2))
		
		self.import_button = Import_Button(self.import_photo, s_width, s_height)
		self.import_button.view.center = (b_width*.75, b_width*.75)
		self.add_options.add_subview(self.import_button.view)
		
		self.camera_button = Camera_Button(self.take_photo, s_width, s_height)
		self.camera_button.view.center = (b_width*.75, b_width*2)
		self.add_options.add_subview(self.camera_button.view)
		
		frame=(s_width/5, s_height/3, s_width*(.6), s_height/5)
		self.importing_message = ui.View(frame=frame, border_width=2, background_color="orange")
		label = ui.Label(text="Importing image, \nplease wait...", frame=(const_buffer, const_buffer, frame[2]-(2*const_buffer), frame[3]-(2*const_buffer)), alignment=ui.ALIGN_CENTER, font=("<system-bold>", 20), number_of_lines=0, line_break_mode=ui.LB_WORD_WRAP)
		self.importing_message.corner_radius = self.importing_message.width/10
		self.importing_message.add_subview(label)
		
		self.scroll_view = ui.ScrollView()
		self.scroll_view.width = s_width
		self.scroll_view.height = s_height*.85
		self.scroll_view.content_size = (s_width, s_height*.5)
		self.scroll_view.center = (s_width/2, s_height*.575)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.add_subview(self.scroll_view)

	def zero_out_variables(self):
		self.add_options_visible = False
		self.warning_visible = False
		self.images = {}
		
		self.last_x = -1
		self.last_y = 0
		
	def toggle_add_options(self, sender):
		if self.add_options_visible:
			self.add_button.view.background_color = "f0fff5"
			self.remove_subview(self.add_options)
			self.add_options_visible = False
		else:
			self.add_button.view.background_color = "bbfad0"
			self.add_subview(self.add_options)
			self.add_options_visible = True
		
	def take_photo(self, sender):
		try:
			pil_img = photos.capture_image()
		except:
			return
		self.save_photo(pil_img)
		
	def import_photo(self, sender):
		self.album_picker = Album_Picker_View(self.choose_import, self.outfit_saver)
		self.add_subview(self.album_picker)

	@ui.in_background
	def choose_import(self, my_photo, valid_img):
		self.remove_subview(self.album_picker)
		self.album_picker = None
		#valid_img == False if back button was pressed
		if valid_img:
		#this works but it takes a long time
		#unfortunately converting it straight to PIL from the asset doesnt always work
			pil_img = Image.open(BytesIO(my_photo.get_ui_image().to_png()))
			self.save_photo(pil_img)
		
	@ui.in_background
	def save_photo(self, pil_img):
		if pil_img == None:
			return
		
		self.outfit_saver.nav.show_warning("", "Importing Photo, Please Wait", None, None, None)
		
		ui_img, image_id = self.model.save_image(pil_img)
		
		frame = self.get_next_frame()
		button = self.create_button(frame, ui_img, image_id)
		self.images[image_id] = button
		self.scroll_view.add_subview(button)
		
		self.toggle_add_options(None)
		self.outfit_saver.nav.hide_warning()
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
	def populate_view(self, params):
		self.zero_out_variables()
		type = self.model_stack[-1]
		self.return_function = params[0]
		self.selected_image = params[1]
		self.title.view.title = self.model.image_directory
		if type[0] == "o":
			self.background_color = "97C1B0"
		elif type[0] == "i":
			self.background_color = "DCBCDA"
		self.images = {}
		if self.model.have_null_image:
			frame = self.get_next_frame()
			image = ui.Image.named("../images/button_images/none_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			button = self.create_button(frame, None, "0")
			image_view = ui.ImageView(width=button.width*.75, height=button.width*.75, center=(button.width*.5, button.height*.5), image=image)
			button.add_subview(image_view)
			
			self.images["0"] = button
		
		image_ids = self.model.load_images()
		
		for entry in image_ids:
			try:
				image_id = str(entry[0])
				image = self.model.get_thumbnail(image_id)
					
				frame = self.get_next_frame()
				self.images[image_id] = self.create_button(frame, image, image_id)
			except:
				print("failed to open image:", image_id)
			
		
		for image_id in self.images:
			self.scroll_view.add_subview(self.images[image_id])
			
	def depopulate_view(self):
		for image_id in self.images:
			self.scroll_view.remove_subview(self.images[image_id])
			
	def prepare_for_open(self, params):
		if self.selected_image != "":
			self.return_function = params[0]
			self.images[self.selected_image].border_width = 1
			self.images[self.selected_image].border_color = "black"
			self.selected_image = params[1]
			self.images[self.selected_image].border_color = "bbfad0"
			self.images[self.selected_image].border_width = 5
		
		
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
		
		buffer = s_width/60
		starting_x = (buffer)+((s_width/6)*x)
		starting_y = ((s_height/10)*y)+(buffer)
		width = (s_width/6)-(2*buffer)
		height = (s_height/10)-(2*buffer)
		frame=(starting_x, starting_y, width, height)
		
		if starting_y+height > self.scroll_view.content_size[1]:
			self.scroll_view.content_size = (s_width, s_y+height+(2*buffer))
			
		return frame
		
	def select_image(self, sender):
		image_id = sender.name
		
		if self.add_options_visible:
			self.toggle_add_options(None)
		
		#"": this is the case where a null image is not selectable and image view closes on selection
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
			image = self.model.get_image(image_id)
		self.return_function(image, image_id)
	

class Album_Picker_View (ui.View):
	def __init__(self, return_function, outfit_saver):
		self.background_color = "white"
		self.width = s_width
		self.height = s_height
		self.return_function = return_function
		self.outfit_saver = outfit_saver
	
		self.add_subview(Back_Button(self.close_self, self.width, self.height).view)
		self.add_subview(Title_Button("Pick Album", None, self.width, self.height).view)
		
		self.b_buffer = self.width/30
		self.last_y = 0
		
		self.scroll_view = ui.ScrollView(frame=(0, self.height*.15, self.width, self.height*.85), content_size=(0,0))
		self.add_subview(self.scroll_view)
		albums = photos.get_smart_albums() + photos.get_albums()
		self.albums = albums
		for x in range(len(albums)):
			self.scroll_view.add_subview(self.create_album_button(albums[x], str(x)))
	
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
			self.return_function(my_photo, True)
		
	def close_self(self, sender):
		self.return_function(None, False)
		
		
class Warning_View(ui.View):
	def __init__(self, primary_message, secondary_message, yes_action, no_action, id_to_delete):
		super().__init__(frame=(s_width/5, s_height/3, (3*s_width)/5, s_height/3))
		
		self.corner_radius = self.width/10
		self.border_width = 2
		self.background_color = "f0fff5"
		
		buffer = const_buffer
		
		self.primary_text = ui.Label(frame=(buffer, buffer, (self.width)-(2*buffer), (self.height/3)-(2*buffer)), alignment=ui.ALIGN_CENTER, font=("<system-bold>", 15))
		self.primary_text.number_of_lines = 0
		self.primary_text.line_break_mode = ui.LB_WORD_WRAP
		self.primary_text.text = primary_message
		self.add_subview(self.primary_text)
		
		self.secondary_text = ui.Label(frame=(buffer, (self.height/3), (self.width)-(2*buffer), (self.height/3)), alignment=ui.ALIGN_CENTER, font=("<system>", 10))
		self.secondary_text.number_of_lines = 0
		self.secondary_text.line_break_mode = ui.LB_WORD_WRAP
		self.secondary_text.background_color = "orange"
		self.secondary_text.text = secondary_message
		self.add_subview(self.secondary_text)
		
		if (yes_action != None):
			if (no_action == None):
				#single center button
				self.yes_button = ui.Button(action=yes_action, frame=(self.width*.4, self.height*(3/4), self.width*.2, self.height*.15), border_width=2, tint_color="black", name=id_to_delete)
				self.yes_button.title="OK"
				self.yes_button.corner_radius = self.yes_button.height/3
				self.add_subview(self.yes_button)
			else:
				#have both buttons
				self.yes_button = ui.Button(action=yes_action, frame=(self.width*.2, self.height*(3/4), self.width*.2, self.height*.15), border_width=2, tint_color="black", name=id_to_delete)
				self.yes_button.title="YES"
				self.yes_button.corner_radius = self.yes_button.height/3
				self.add_subview(self.yes_button)
				
				self.no_button = ui.Button(action=no_action, frame=(self.width*.6, self.height*(3/4), self.width*.2, self.height*.15), border_width=2, tint_color="black", name=id_to_delete)
				self.no_button.title="NO"
				self.no_button.corner_radius = self.no_button.height/3
				self.add_subview(self.no_button)
				
				
	
class Search_View(Stackable_View_Template):
	def __init__(self, Model_Class, outfit_saver):
		super().__init__(Model_Class, outfit_saver)
		
		buffer = const_buffer
		
		#create pattern
		pattern_view = ui.ImageView(width=pattern_width, height=pattern_width, center=(s_width/2, s_height/2))
		pattern_view.image = white_pattern
		pattern_view.transform = ui.Transform.rotation(-rotation_angle)
		self.add_subview(pattern_view)
		
		#create back button
		self.back_button = Back_Button(self.close_view, s_width, s_height)
		self.add_subview(self.back_button.view)
		
		#create title
		self.title = Title_Button("", None, s_width, s_height)
		self.add_subview(self.title.view)
		
		#create search bar
		self.text_field = ui.TextField(frame=(s_width*.1, s_height*.1375, s_width*.8, s_height*.05), delegate=SearchTextFieldDelegate(self), bordered=True)
		self.add_subview(self.text_field)
		
		#create scroll view
		self.scroll_view = ui.ScrollView()
		self.scroll_view.content_size = (s_width, s_height*.5)
		self.scroll_view.frame = (0, s_height*.2, s_width, s_height*.8)
		self.scroll_view.shows_vertical_scroll_indicator = False
		self.scroll_view.border_width = 2
		self.add_subview(self.scroll_view)
		
		self.zero_out_variables()
			
	def zero_out_variables(self):
		self.last_c1_y = const_buffer
		self.last_c2_y = const_buffer
		self.last_c3_y = const_buffer
		self.scroll_view.content_size = (s_width, s_height*.5)
		self.icons = {}
		
	def prepare_for_open(self, params):
		self.search("")
	
	def populate_view(self, params):
		self.title.view.title = params[0]
		self.choose_icon = params[4]
		self.background_color = params[5]
		self.search("")
		
	def depopulate_view(self):
		self.remove_icons()
		
	def edit_preview(self, preview_id, params):
		self.search(self.text_field.text)
	
	def remove_preview(self, preview_id, params):
		self.search(self.text_field.text)
	
	def search(self, search_string):
		self.remove_icons()
		data = self.model.search(search_string)
		
		#assume icons are empty
		for entry in data:
			icon = self.create_icon(entry[0], entry[1], entry[2])
			self.icons[entry[0]] = icon
			self.scroll_view.add_subview(icon)
			
	def remove_icons(self):
		for icon in self.icons:
			self.scroll_view.remove_subview(self.icons[icon])
		self.zero_out_variables()
		
		
	def create_icon(self, id, image, name):
		#TODO rethink when titles are needed
		if image != None:
			image_ratio = image.size[1]/image.size[0]
			frame = self.get_next_frame(image_ratio)
		else:
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
		buffer = const_buffer
		
		width = (s_width/3)-(2*buffer)
		if image_ratio == 0:
			height = (s_height/5)-(2*buffer)
		else:
			height = width*image_ratio
		
		if self.last_c1_y <= self.last_c2_y and self.last_c1_y <= self.last_c3_y:
			frame = (buffer, self.last_c1_y, width, height)
			self.last_c1_y+=(buffer+height)
			if self.last_c1_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (s_width, self.last_c1_y)
		elif self.last_c2_y <= self.last_c3_y:
			frame = (buffer+(s_width/3), self.last_c2_y, width, height)
			self.last_c2_y+=(buffer+height)
			if self.last_c2_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (s_width, self.last_c2_y)
		else:
			frame = (buffer+((2*s_width)/3), self.last_c3_y, width, height)
			self.last_c3_y+=(buffer+height)
			if self.last_c3_y > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (s_width, self.last_c3_y)
		
		return frame
		
		
	def close_view(self, sender):
		self.outfit_saver.nav.pop_view()
		
		
			







class ScrollViewDelegate:
	def __init__(self, clothing_unit_view):
		self.clothing_unit_view = clothing_unit_view
		
	def scrollview_did_scroll(self, scrollview):
		if self.clothing_unit_view.note_view != None:
			self.clothing_unit_view.note_view.end_editing()
		
		
class TextViewDelegate:
	def __init__(self, clothing_unit_view):
		self.clothing_unit_view = clothing_unit_view
		
	def textview_did_end_editing(self, textview):
		self.clothing_unit_view.model.note = textview.text
		self.clothing_unit_view.model.save_note()
	
	
class SearchTextFieldDelegate (object):
	def __init__(self, search_view):
		self.search_view = search_view
	
	def textfield_did_change(self, textfield):
		self.search_view.search(textfield.text)

