import sqlite3
import photos
import ui
import math
import os

from outfit_category_viewer import Outfit_Category_Viewer
from item_category_viewer import Item_Category_Viewer
from clothing_unit import Clothing_Unit_View
from nav_view import Nav_View

class Outfit_Saver:
	def __init__(self):
		self.initialize_file_tree()
		self.initialize_database()

		
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
		#TODO does this need to be done every time?
		#TODO leaving outfit_category_viewer while in minus mode causes problems
		self.outfit_category_viewer.remove_category_icons_from_view()
		self.outfit_category_viewer.category_icons = self.outfit_category_viewer.load_category_icons()
		self.outfit_category_viewer.put_category_icons_on_view()
		
		self.nav.push_view(self.outfit_category_viewer.view)
		
	def open_item_category_viewer(self, sender):
		self.item_category_viewer.remove_category_icons_from_view()
		self.item_category_viewer.category_icons = self.item_category_viewer.load_category_icons()
		self.item_category_viewer.put_category_icons_on_view()
		
		self.nav.push_view(self.item_category_viewer.view)

				
outfit_saver = Outfit_Saver()
