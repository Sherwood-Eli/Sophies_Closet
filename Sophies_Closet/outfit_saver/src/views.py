import ui
import time
import gc

from buttons import Add_Button, Back_Button, Search_Button, Remove_Button, Small_Remove_Button, Title_Button
from icon import Icon
from warning_view import Warning_View

class Nav_View(ui.View):
	#Reusable images
	pattern_image = ui.Image.named("../images/button_images/white_pattern.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	self.add_icon_PNG =  ui.Image.named("../images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	self.down_icon_PNG = ui.Image.named("../images/button_images/down_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	self.up_icon_PNG =  ui.Image.named("../images/button_images/up_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
	panel_image = ui.Image.named("../images/button_images/white_panel.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)

	#Reusable values
	s_width, s_height = ui.get_screen_size()
	buffer = s_width/30
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
	
	
	def __init__(self, outfit_saver):
		self.outfit_saver = outfit_saver
		
		self.view_stack = []
		self.duration = 0.35
		
		#initialize other views:
		self.root_view = Root_View()
		self.all_views = {}
		self.all_views["outfit_category_viewer"] = Category_Viewer_View("97C1B0", "OUTFIT_CATEGORIES", Outfit_Category_Viewer, outfit_saver)
		self.all_views["item_category_viewer"] = Category_Viewer_View("DCBCDA", "ITEM_CATEGORIES", Item_Category_Viewer, outfit_saver)
		self.all_views["outfit_category"] = Category_Viewer_View(self)
		self.all_views["item_category"] = Category_Viewer_View(self)
		self.all_views["outfit"] = Clothing_Unit_View("97C1B0", self.outfit_saver)
		self.all_views["item"] = Clothing_Unit_View("DCBCDA" , self.outfit_saver)

		self.add_subview(self.root_view)
			
	#returns the index of the newly pushed view
	def push_view(self, view_type, model_id):
		#get view
		cur_view = self.all_views[view_type]
		#pushes model to view and populates necessary stuff for viewing
		cur_view.push_model(model_id)
		
		#start populating rest of stuff with different thread
		cur_view.populate_view()
		
		#Show view
		if len(cur_view.model_stack) == 1:
			#this means view is not actually in stack yet so need to add to subview
			self.add_subview(cur_view)
		else:
			#this means view is already presented so we just need to bring to front
			cur_view.bring_to_front()
		
		#Add new view+model pairing to nav_view view stack
		self.view_stack.append(view_type)
		
	def pop_view():
		#pop view+model pairing from nav_view view stack
		popped_view = self.all_views[self.view_stack.pop(-1)]
		
		#get and prepare new cur view, if any
		if len(self.view_stack) != 0:
			cur_view = self.all_views[self.view_stack[-1]]
			
			#Starts full population with new model
			cur_view.populate_view()
			
			#animate popped view close, revealing cur_view on top
			cur_view.bring_to_front()
			popped_view.bring_to_front()
			popped_view.send_to_back()
		
		#pops model from popped view and does initial steps for new model at top of model stack
		popped_view.pop_model()
		
		#removes popped view if no more models left
		if len(cur_view.model_stack) == 0:
			self.remove_subview(popped_view)
		
		

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
			button_width = (self.screen_width-(2*buffer))
			button_height = (self.screen_height/2)-((3*buffer)+(buffer/2))
			
			#initialize "outfits" button
			outfit_button_frame = (buffer, 3*buffer, button_width, button_height)
			self.outfits_button = ui.Button(frame=outfit_button_frame, border_width=2, border_color="black", background_color="97C1B0", action=outfit_saver.open_outfit_category_viewer)
			button_pattern_view = ui.ImageView(width=width, height=width, center=(button_width/2, button_height/2))
			button_pattern_view.image = button_pattern_image
			button_pattern_view.transform = ui.Transform.rotation(-rotation_angle)
			self.outfits_button.add_subview(button_pattern_view)
			panel_view = ui.ImageView(frame=((3*buffer), (2*outfit_button_frame[3]/5), outfit_button_frame[2]-(6*buffer), outfit_button_frame[3]/5))
			panel_view.image = panel_image
			self.outfits_button.add_subview(panel_view)
			title_view = ui.ImageView(frame=(0, 2*buffer/3, outfit_button_frame[2]-(6*buffer), (outfit_button_frame[3]/5)-(buffer)), content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
			title_image = ui.Image.named("../images/button_images/text_outfits_purple.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			title_view.image = title_image
			panel_view.add_subview(title_view)
			
			self.view.add_subview(self.outfits_button)
			
			
			#initialize "clothing items" button
			item_button_frame = (buffer, (self.screen_height/2)+(buffer/2), button_width, button_height)
			self.items_button = ui.Button(frame=item_button_frame, border_width=2, border_color="black", background_color="DCBCDA", action=outfit_saver.open_item_category_viewer)
			button_pattern_view = ui.ImageView(width=width, height=width, center=(button_width/2, button_height/2))
			button_pattern_view.image = button_pattern_image
			button_pattern_view.transform = ui.Transform.rotation(-rotation_angle)
			self.items_button.add_subview(button_pattern_view)
			panel_view = ui.ImageView(frame=((3*buffer), (2*outfit_button_frame[3]/5), outfit_button_frame[2]-(6*buffer), outfit_button_frame[3]/5))
			panel_view.image = panel_image
			self.items_button.add_subview(panel_view)
			title_view = ui.ImageView(frame=(0, 2*buffer/3, outfit_button_frame[2]-(6*buffer), (outfit_button_frame[3]/5)-(buffer)), content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
			title_image = ui.Image.named("../images/button_images/text_clothingitems_purple.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
			title_view.image = title_image
			panel_view.add_subview(title_view)
			
			self.view.add_subview(self.items_button)
			

##################################
#
# Category_Viewer_View
#
##################################

	class Category_Viewer_View(ui.View):
		def __init__(self, background_color, title, Model, outfit_saver):
			self.outfit_saver = outfit_saver
			self.Model = Model
			self.background_color = background_color
			self.title = title
			
			self.model_stack = []
			
			self.category_icons = {}
			self.remove_buttons = []
			self.remove_mode = False
			self.last_category_x = -1
			self.last_category_y = 0

				
			#Create background image
			image_view = ui.ImageView(width=width, height=width, center=(s_width/2, s_height/2))
			image_view.image = pattern_image
			image_view.transform = ui.Transform.rotation(-rotation_angle)
			self.add_subview(image_view)
			
			#Scroll View
			self.scroll_view = Std_Scroll_View(s_width, s_height)
			self.add_subview(self.scroll_view.view)
			
			#Title Button: No action bc title not editable in this view
			view_title = Title_Button(self.title, None, s_width, s_height)
			self.add_subview(view_title.view)
			
			#Add_Button - Action added later
			self.add_button = Add_Button(None, s_width, s_height)
			self.add_subview(add_button.view)
			
			#Remove_Button
			self.remove_button = Remove_Button(self.toggle_remove_mode, s_width, s_height)
			self.add_subview(remove_button.view)
			
			#Back_Button
			back_button = Back_Button(self.back_button_press, s_width, s_height)
			self.add_subview(back_button.view)
			
			#Search_Button - Action add later
			self.search_button = Search_Button(None, s_width, s_height)
			self.add_subview(search_button.view)
			
		def push_model(model_id):
			#push model_id to model_stack
			self.model_stack.append(model_id)
			
			#get rid of old model stuff if exists
			if len(model_stack != 1):
				self.depopulate_view()
			
			#create model
			self.model = self.Model(model_id, self, self.outfit_saver)
			
			#reroute actions to go to new model
			self.add_button.view.action = model.add_category
			self.search_button.view.action = model.add_category
			
			
		def pop_model():
			self.model_stack.pop(-1)
			
			#get rid of old model stuff
			self.depopulate_view()
			
			#prepare next model if exists
			if len(self.model_stack) != 0:
				self.model = self.Model(self.model_stack[-1], self, self.outfit_saver)
			
				#reroute actions to go to new model
				self.add_button.view.action = model.add_category
				self.search_button.view.action = model.add_category
		
		
		def populate_view():
			self.category_icons = self.model.load_category_icons()
			for id in self.category_icons:
				self.scroll_view.add_subview(self.category_icons[id].button)
			
		
		#Get rid of everything so we can save some memory
		def depopulate_view(self):
			for id in self.category_icons:
				self.scroll_view.remove_subview(self.category_icons[id].button)
			if self.remove_mode:
				self.toggle_remove_mode(self.remove_button)
			#Zero out these values
			self.category_icons = {}
			self.remove_buttons = []
			self.remove_mode = False
			self.last_category_x = -1
			self.last_category_y = 0
			
		
		#Retrieve category data from database then create icons for them
		def load_category_icons(self):
			categories = self.model.load_categories()
			#Creating Icons
			category_icons = {}
			for category in categories:
				category_icons[str(category[0])] = Icon(category, self.next_icon_frame, this.image_directory, self.open_category)
			return category_icons
		
		#Wrapper for calling depop and pop
		def refresh_icons(self):
			self.depopulate_view()
			self.populate_view()
		
		#Called by remove button
		def toggle_remove_mode(self, sender):
			if not self.remove_mode:
				#Start remove mode
				self.remove_buttons = []
				buffer = self.outfit_saver.screen_width*.0125
				#Create remove buttons for all category icons
				for category_id in self.category_icons:
					frame = self.category_icons[category_id].button.frame
					name = category_id
					center = (frame[0]+buffer, frame[1]+buffer)
					remove_button = Small_Remove_Button(self.prompt_remove_category, name, center, self.outfit_saver)
					self.scroll_view.add_subview(remove_button.button)
					self.remove_buttons.append(remove_button)
				self.remove_mode = True
				sender.background_color = "bbfad0"
			else:
				#End remove mode
				for button in self.remove_buttons:
					self.scroll_view.remove_subview(button.button)
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
			if starting_y+height > self.scroll_view.content_size[1]:
				self.scroll_view.content_size = (screen_width, starting_y+height+(2*buffer))
				
			return frame
		
		#Shows warning window to make sure user wants to delete category
		def prompt_remove_category(self, sender):
			category_icon = self.category_icons[sender.name]
			title = category_icon.title.text
			self.warning_view = Warning_View("Delete '"+title+"'?", "All items in this catgory will continue to exist", self.remove_category, self.cancel_remove, sender.name, self.outfit_saver)
			self.add_subview(self.warning_view)
			
		#Handle cancel remove
		def cancel_remove(self, sender):
			self.remove_subview(self.warning_view)
			self.warning_view = None
			
		#Handle confirm remove
		def remove_category_from_view(category_id)
			x = len(self.remove_buttons)-1
			category_keys = list(self.category_icons.keys())
			while self.remove_buttons[x].button.name != category_id:
				self.remove_buttons[x].button.center = self.remove_buttons[x-1].button.center
				key = category_keys[x]
				next_key = category_keys[x-1]
				self.category_icons[key].button.center = self.category_icons[next_key].button.center
				
				x-=1
				
			self.scroll_view.remove_subview(self.remove_buttons[x].button)
			self.scroll_view.remove_subview(self.category_icons[category_id].button)
				
			self.remove_buttons.pop(x)
			del self.category_icons[category_id]
			
			self.view.remove_subview(self.warning_view)
			
			self.warning_view = None
			
#WHERE I LEFT OFF:
# I need to figure out how everything is working together still
# I have my views, you should be able to call from the model to push a specific view with certain parameters
# The model is going to have to call some functions in the view and vice versa
# Maybe I should make it so the model pushes to stack, then the view handles everything, including button actions
# its the views job to inform the model of changes and will only move forward if model is updated properly


##################################
#
# Category_View
#
##################################

	class Category_View(ui.View):
		def __init__(self):
			self.model_stack = []



##################################
#
# Clothing_Unit_View
#
##################################

	class Clothing_Unit_View(ui.View):
		def __init__(self, background_color, outfit_saver):
			#variables for placing icons on view
			self.last_image_x = -1
			self.last_link_x = 0
			self.last_link_y = -1
			self.last_category_y = -1
			
			#toggleable buttons based on whether or not remove mode is active
			self.image_remove_buttons = []
			self.link_remove_buttons = []
			self.category_remove_buttons = []
			self.unit_remove_button = None
			
			#list to keep track of model stack
			self.model_stack = []
			self.outfit_saver = outfit_saver
									
			#Default background
			pattern_view = ui.ImageView(width=self.outfit_saver.pattern_width, height=self.outfit_saver.pattern_width, center=(s_width/2, s_height/2))
			pattern_view.image = pattern_image
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
			self.back_button = Top_Left_Button(self.close_view, s_width, s_height, "../images/button_images/back_icon.PNG")
			self.add_subview(self.back_button.button)
			
			#Title_Button
			self.title_button = Title_Button("", self.edit_title, s_width, s_height)
			self.add_subview(self.title_button.button)
			self.title_edit_field = Title_Edit_Field(self.title_button.button, None)
			
			#Remove_Button
			self.remove_button = Top_Right_Button(None, s_width, s_height, "../images/button_images/minus_icon.PNG")
			self.add_subview(self.remove_button.button)
						
			temp_view = ui.View(frame=(buffer, (s_height*1.75)+buffer, s_width-(2*buffer), (s_height*.8)-(2*buffer)), background_color="f0fff5", border_width=2)
			temp_view.corner_radius = temp_view.width/10
			self.note_view = ui.TextView(frame=(buffer, buffer, s_width-(4*buffer), (s_height*.8)-(4*buffer)), font=('<system>', 20), delegate=TextViewDelegate(self), background_color=None)
			temp_view.add_subview(self.note_view)
			self.main_scroll_view.add_subview(temp_view)
			
			#score slider
			temp_view = ui.View(frame=(buffer, s_height*.725, s_width-(2*buffer), s_height*.05), border_width=2, background_color="f0fff5")
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

		#adds a clothing unit model to be show on the view
		@ui.in_background
		def load_view(self, model=None):
			self.remove_icons_from_view(self.image_scroll_view)
			self.remove_icons_from_view(self.link_scroll_view)
			self.remove_icons_from_view(self.category_scroll_view)
			if model == None:
				model = self.models[-1]
			else:
				self.models.append(model)
			model.view = self
			self.model = model
			
			t1 = Thread(target=model.load_image_icons)
			t1.start()
			
			t2 = Thread(target=model.load_link_icons)
			t2.start()
			
			#Category background - no category background if accessed from search view
			if model.caller_type != "s":
				self.background_view.image = model.category.bg_image
			self.title_button.button.title = model.title
			self.remove_button.button.action = model.toggle_remove
			self.title_edit_field.text_field = model.set_title
			self.slider.action = model.set_score
			self.note_view.text = model.note
			self.score_label.text = str(model.score)+"/10"
			self.slider.value = model.score/10
			
			model.load_category_icons()
			
			t1.join()
			t2.join()
		
		#closes the top view, opens the next view
		def close_view(self, sender):
			self.models.pop(-1)
			if len(self.models) == 0:
				self.outfit_saver.nav.pop_view()
			else:
				self.outfit_saver.nav.pop_view(rm_subview=False)
				self.load_view()
			
		def put_icons_on_view(self, view, icons):
			for icon in icons:
				view.add_subview(icons[icon])
				
		def remove_icons_from_view(self, view):
			for subview in view.subviews:
				view.remove_subview(subview)
				
		def edit_title(self, sender):
			if not self.model.remove_mode:
				self.remove_subview(self.title_button.button)
				self.add_subview(self.title_edit_field.text_field)
				self.title_edit_field.text_field.begin_editing()
				
		def create_scroll_icon(self, frame, up_icon):
			if up_icon:
				image = self.up_icon_PNG
			else:
				image = self.down_icon_PNG
			icon = ui.ImageView(frame=frame)
			icon.image = image
			return icon



##################################
#
# Image_Selector_View
#
##################################

	class Image_Selector_View(ui.View):
		def __init__(self):
			


