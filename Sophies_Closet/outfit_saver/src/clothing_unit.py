import ui
import sqlite3
import math
import os
from threading import Thread

#for testing:
import time

from buttons import  *

class Clothing_Unit:
	def __init__(self, model_id, view, outfit_saver):
		self.id = model_id
		self.view = view
		self.outfit_saver = outfit_saver
		self.category = self.outfit_saver.nav.get_cur_category(self.type).model
		
		self.title, self.score, self.note = self.get_sql_data()

	#Called from:
	#	Clothing_Unit_View.load_view
	#pwd when called: ~
	def load_image_data(self):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT {}_image_id
		FROM "{}_images"
		WHERE {}_id="{}"
		'''.format(self.type, self.type, self.type, self.id)
		cursor.execute(sql)
		image_ids = cursor.fetchall()
		
		return image_ids
		
	
	#Called from:
	#	Image_Selector.return_function
	#pwd when called: ~
	def save_image(self, image_name):
		if self.id == None:
			self.create()
		
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
	

	
		
	####		End Image View Code 					####
	####################################################

	####################################################
	####	Begin Link Preview Code 					####

	#Called from:
	#	Image_Selector.return_function
	#pwd when called: ~
	def load_link_data(self):
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
		
		return item_ids
		
		
	
	def save_link(self, link_id):
		if self.id == None:
			self.create()
		
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
	
	def get_link_images(self, link_id):
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
		
		return image_ids
	
	
		

		

	####	End Link Icon Code 						####
	####################################################

	####################################################
	####	Begin Category Icon Code 				####

	def load_all_category_data(self):
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
		data = cursor.fetchall()
		conn.close()
		
		return data
		
	def load_single_category_data(self, category_id):
		conn = sqlite3.connect('../db/outfit_saver.db')
		cursor = conn.cursor()
		
		sql = '''
		SELECT category_id, category_name, photo_path
		FROM "{}_categories"
		WHERE category_id="{}"
		'''.format(self.type, category_id)
		cursor.execute(sql)
		data = cursor.fetchall()
		conn.close()
		
		return data
		
	def save_category(self, category_id):
		if self.id == None:
			self.create()
		
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

		

	####	End Category Icon Code 					####
	####################################################
		
		
	
		
		
	
		
	
			
	
		
	
	
		
	
		
		

