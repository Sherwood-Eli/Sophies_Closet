import ui

class Warning_View(ui.View):
	def __init__(self, primary_message, secondary_message, yes_action, no_action, id_to_delete, outfit_saver):
		self.outfit_saver = outfit_saver
		
		s_width = outfit_saver.screen_width
		s_height = outfit_saver.screen_height
		
		super().__init__(frame=(s_width/5, s_height/3, (3*s_width)/5, s_height/3))
		
		self.corner_radius = self.width/10
		self.border_width = 2
		self.background_color = "f0fff5"
		
		buffer = s_width/20
		
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
		
		self.yes_button = ui.Button(action=yes_action, frame=(self.width*.2, self.height*(3/4), self.width*.2, self.height*.15), border_width=2, tint_color="black", name=id_to_delete)
		self.yes_button.title="YES"
		self.yes_button.corner_radius = self.yes_button.height/3
		self.add_subview(self.yes_button)
		
		self.no_button = ui.Button(action=no_action, frame=(self.width*.6, self.height*(3/4), self.width*.2, self.height*.15), border_width=2, tint_color="black", name=id_to_delete)
		self.no_button.title="NO"
		self.no_button.corner_radius = self.no_button.height/3
		self.add_subview(self.no_button)
