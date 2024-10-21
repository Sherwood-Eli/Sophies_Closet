import ui

class Add_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		image_view = ui.ImageView(image=image)
		image_view.width=(s_width*.10)
		image_view.height = image_view.width
		image_view.center = ((s_width*.075), (s_width*.075))
		self.view = ui.Button(action = action, background_color="f0fff5")
		self.view.width=(s_width*.15)
		self.view.height = self.view.width
		self.view.corner_radius = self.view.width/2
		self.view.center = (s_width*.5, s_height*.9)
		self.view.border_width = 2
		self.view.add_subview(image_view)
		
class Remove_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/minus_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		image_view = ui.ImageView(image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.width=(s_width*.05)
		image_view.height = image_view.width
		image_view.center = ((s_width*.05), (s_width*.05))
		self.view = ui.Button(action = action, background_color="f0fff5")
		self.view.width=(s_width*.1)
		self.view.height = self.view.width
		self.view.corner_radius = self.view.width/2
		self.view.center = (s_width*.5, s_height*.96)
		self.view.name = "f"
		self.view.border_width = 2
		self.view.add_subview(image_view)
		
class Small_Remove_Button:
	def __init__(self, action, name, center, outfit_saver):
		s_width = outfit_saver.screen_width
		s_height = outfit_saver.screen_height
		image = ui.Image.named("../images/button_images/minus_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		image_view = ui.ImageView(image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.width=(s_width*.0375)
		image_view.height = image_view.width
		image_view.center = ((s_width*.0375), (s_width*.0375))
		self.button = ui.Button(action = action, background_color="bbfad0")
		self.button.width=(s_width*.075)
		self.button.height = self.button.width
		self.button.corner_radius = self.button.width/2
		self.button.center = center
		self.button.name = name
		self.button.border_width = 2
		self.button.add_subview(image_view)
		
class Back_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/back_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.view = ui.Button(action = action, border_color = "black", border_width = 2, background_color="f0fff5")
		self.view.width=(s_width/10)
		self.view.height=(s_width/10)
		self.view.corner_radius = self.view.width/3
		self.view.center = (s_width/10, s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.view.add_subview(image_view)
		
class Outfit_Remove_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/search_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(image=image, action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		
class Search_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/search_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.view = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.view.width=(s_width/10)
		self.view.height=(s_width/10)
		self.view.corner_radius = self.view.width/3
		self.view.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image)
		image_view.center = (s_width/20, s_width/20)
		self.view.add_subview(image_view)
		
class Image_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/image_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Top_Right_Add_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/add_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Top_Right_Button:
	def __init__(self, action, s_width, s_height, photo_path):
		image = ui.Image.named(photo_path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Top_Left_Button:
	def __init__(self, action, s_width, s_height, photo_path):
		image = ui.Image.named(photo_path).with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, border_color = "black", border_width = 2, background_color="f0fff5")
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width/10, s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Top_Right_Remove_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/minus_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Import_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/import_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Camera_Button:
	def __init__(self, action, s_width, s_height):
		image = ui.Image.named("../images/button_images/camera_icon.PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		self.button = ui.Button(action = action, background_color="f0fff5", border_color = "black", border_width = 2)
		self.button.width=(s_width/10)
		self.button.height=(s_width/10)
		self.button.corner_radius = self.button.width/3
		self.button.center = (s_width*(9/10), s_height/10)
		image_view = ui.ImageView(width=s_width/13, height=s_width/13, image=image, content_mode=ui.CONTENT_SCALE_ASPECT_FIT)
		image_view.center = (s_width/20, s_width/20)
		self.button.add_subview(image_view)
		
class Title_Button:
	def __init__(self, title, action, s_width, s_height):
		self.view = ui.Button(action=action, width=(s_width*(3/5)), height=(s_width/10), font = ('<system-bold>', 20), border_width=2, background_color="f0fff5")
		self.view.title = title
		self.view.center = (s_width/2, s_height/10)
		self.view.corner_radius = (s_width/30)
		self.view.tint_color = "black"
		
class Title_Edit_Field:
	def __init__(self, title, action):
		self.text_field = ui.TextField(action=action, font=title.font, width=title.width, height=title.height, background_color="f0fff5")
		self.bordered = True
		#self.border_width = title.border_width
		self.text_field.alignment = ui.ALIGN_CENTER
		self.text_field.text = title.title
		self.text_field.center = title.center
		#self.text_field.corner_radius = title.corner_radius
		
class Std_Scroll_View:
	def __init__(self, s_width, s_height)
		self.view.width = s_width
		self.view.height = s_height*.85
		self.view.content_size = (s_width, s_height*.5)
		self.view.center = (s_width/2, s_height*.575)
		self.view.shows_vertical_scroll_indicator = False
