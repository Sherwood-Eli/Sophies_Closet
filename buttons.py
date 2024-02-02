import ui

class Add_Button:
	def __init__(self, action, outfit_saver):
		s_width = outfit_saver.screen_width
		s_height = outfit_saver.screen_height
		image = ui.Image.named("images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		image_view = ui.ImageView(image=image)
		image_view.width=(s_width*.10)
		image_view.height = image_view.width
		image_view.center = ((s_width*.075), (s_width*.075))
		self.button = ui.Button(action = action, background_color="f0fff5")
		self.button.width=(s_width*.15)
		self.button.height = self.button.width
		self.button.corner_radius = self.button.width/2
		self.button.center = (outfit_saver.screen_width*.5, outfit_saver.screen_height*.9)
		self.button.border_width = 2
		self.button.add_subview(image_view)
		
class Back_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("images/button_images/back_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(image=image, action = action, border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width/10, s_height/10)
		
class Image_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("images/button_images/image_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(image=image, action = action, background_color = "white", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		
class Import_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("images/button_images/import_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(image=image, action = action, background_color = "white", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		
class Title_Button:
	def __init__(self, title, action, s_width, s_height):
		self.button = ui.Button(action=action, width=(s_width*(3/5)), height=(s_width/10), font = ('<system-bold>', 20), border_width=2)
		self.button.title = title
		self.button.center = (s_width/2, s_height/10)
		self.button.corner_radius = (s_width/30)
		self.button.tint_color = "black"
		
class Title_Edit_Field:
	def __init__(self, title, action):
		self.text_field = ui.TextField(action=action, font=title.font, width=title.width, height=title.height)
		self.bordered = True
		#self.border_width = title.border_width
		self.text_field.alignment = ui.ALIGN_CENTER
		self.text_field.text = title.title
		self.text_field.center = title.center
		#self.text_field.corner_radius = title.corner_radius
		
		
		
		
		
		
		
		
class Cancel_Button:
	def __init__(self, action, s_width, s_height):
		self.button = ui.Button(width=(s_width/5), height=(s_height/20), center=(s_width/3, s_height*(9/10)), action=action)
		self.button.title="CANCEL"
	
class Save_Button:
	def __init__(self, action, s_width, s_height):
		self.button = ui.Button(width=(s_width/5), height=(s_height/20), center=(s_width*(2/3), s_height*(9/10)), action=action)
		self.button.title="SAVE"
