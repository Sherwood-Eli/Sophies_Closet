import sqlite3
import os
import math
from PIL import Image
import ui




	
		
class Image_Selector:
	def __init__(self, type):
		self.type = type
		# type possibilities:
		#	"oc": outfit category background
		#	"ic": item category background
		#	"outfit": outfit image
		#	"item": item image
		if type[1] == "c":
			self.image_directory = "background_images"
			self.thumbnail_directory = "background_thumbnails"
			self.have_null_image = True
		else:
			self.image_directory = type + "_images"
			self.thumbnail_directory = type + "_thumbnails"
			self.have_null_image = False
			
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
		
		return image_ids
	
	def save_image(self, pil_img):
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
		
		return ui_img, image_id
		
	def convert_to_thumbnail(self, image):
		image_ratio = image.size[1]/image.size[0]
		width = 256
		size = (width, int(width*image_ratio))
		return image.resize(size, Image.ANTIALIAS)
		
	def get_image(self, image_id):
		return ui.Image.named("../images/"+self.image_directory+"/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
		
	def get_thumbnail(self, image_id):
		return ui.Image.named("../images/"+self.thumbnail_directory+"/"+image_id+".PNG").with_rendering_mode(ui.RENDERING_MODE_ORIGINAL)
