import sqlite3
import photos
import ui
import math
import os

from views import Nav_View


#Optimization Wish-List
#	- make a Constants object that I can use to access constants throughout the app, helpful for reducing string dependence

class Outfit_Saver:
	def __init__(self):
		self.initialize_file_tree()
		self.initialize_database()
		
		self.nav = Nav_View(self)
		
		#deployment mode:
		self.nav.alpha = 0.0  # Set initial alpha to 0
		def animation():
			self.nav.alpha = 1.0
		
		self.nav.present("fullscreen", hide_title_bar=True, animated=False)
		#self.nav.present("fullscreen")
		ui.animate(animation, duration=1.0)

		
	def initialize_file_tree(self):
		os.chdir("..")
		
		directory_path = "db"
		try:
			os.makedirs(directory_path)
		except FileExistsError:
			pass
		except Exception as e:
			print(f"Error creating directory: {e}")
		
		os.chdir("images")
		image_directories = ["outfit_images", "outfit_thumbnails", "item_thumbnails", "item_images", "background_images", "background_thumbnails"]
		for directory_path in image_directories:
			try:
				os.makedirs(directory_path)
			except FileExistsError:
				pass
			except Exception as e:
				print(f"Error creating directory: {e}")
		
		
		os.chdir("../src")
		
		
	def initialize_database(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='item_images'")
		table_exists = cursor.fetchone()
		
		if table_exists:
			return
		
		#create outfits table
		sql = '''
		CREATE TABLE "outfits" (
			"outfit_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"outfit_name"	TEXT,
			"outfit_score" INTEGER,
			"outfit_note" TEXT
		)
		'''
		cursor.execute(sql)
		
		#create items table
		sql = '''
		CREATE TABLE "items" (
			"item_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"item_name"	TEXT,
			"item_score" INTEGER,
			"item_note" TEXT
		)
		'''
		cursor.execute(sql)

		#create outfit_categories table
		sql = '''
		CREATE TABLE "outfit_categories" (
			"category_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"category_name"	TEXT,
			"photo_path"	TEXT
		)
		'''
		cursor.execute(sql)
		
		#create item_categories table
		sql = '''
		CREATE TABLE "item_categories" (
			"category_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"category_name"	TEXT,
			"photo_path"	TEXT
			)
		'''
		cursor.execute(sql)
		
		#create outfit_items table
		sql = '''
		CREATE TABLE "outfit_items" (
			"outfit_id"	INTEGER,
			"item_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#create category_outfits table
		sql = '''
		CREATE TABLE "category_outfits" (
			"category_id"	INTEGER,
			"outfit_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#create category_items table
		sql = '''
		CREATE TABLE "category_items" (
			"category_id"	INTEGER,
			"item_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#TODO the image dorextory column will take up a lot of space for no reason
		
		#create images table
		sql = '''
		CREATE TABLE "images" (
			"image_id"	INTEGER PRIMARY KEY AUTOINCREMENT,
			"image_directory"	TEXT
			)
		'''
		cursor.execute(sql)
		
		#create outfit_images table
		sql = '''
		CREATE TABLE "outfit_images" (
			"outfit_image_id"	INTEGER,
			"outfit_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		#create item_images table
		sql = '''
		CREATE TABLE "item_images" (
			"item_image_id"	INTEGER,
			"item_id"	INTEGER
			)
		'''
		cursor.execute(sql)
		
		conn.close()
		
	def open_outfit_category_viewer(self, sender):
		#By creating this every time, it reduces memory usage but increases load up time each time
		self.nav.push_view("outfit_category_viewer", "", "")
		
	def open_item_category_viewer(self, sender):
		#By creating this every time, it reduces memory usage but increases load up time each time
		self.nav.push_view("item_category_viewer", "", "")

				
outfit_saver = Outfit_Saver()
