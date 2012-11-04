#!/usr/bin/env python

from parser import Parser
import re
import gtk
from os import walk, path
from cgi import escape


class Unbloat:

	def __init__(self):
		# Our window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.set_border_width(10)
		self.window.set_title("Unbloat")
		self.window.set_size_request(550, 450)
		self.window.set_icon_from_file('unbloat-titlebar.png')
		
		# Treview setup
		self.liststore = gtk.ListStore(str, str, str)
		treeview = gtk.TreeView(self.liststore)
		
		self.cell = gtk.CellRendererText()
		self.cell1 = gtk.CellRendererText()
		
		tvcolumn_line = gtk.TreeViewColumn('file', self.cell,  markup=0)
		tvcolumn_file = gtk.TreeViewColumn('line', self.cell,  markup=1)
		tvcolumn_str = gtk.TreeViewColumn('string', self.cell, markup=2)
		
		tvcolumn_str.set_expand(True)
		
		self.cell.set_property('xpad', 10)
		

		treeview.append_column(tvcolumn_line)
		treeview.append_column(tvcolumn_file)
		treeview.append_column(tvcolumn_str)

		# Scrolled window
		scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		scrolled_window.add_with_viewport(treeview)
		
		# FileChooserDialogs
		self.filechooser_dir = gtk.FileChooserDialog(
			title="Select root folder",
			action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
		)
		self.filechooser_dir.set_current_folder('/home/lyrae/Desktop/dt/html')
		self.filechooser_css = gtk.FileChooserDialog(
			title="Select CSS file",
			action=gtk.FILE_CHOOSER_ACTION_OPEN,
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
		)
		self.filechooser_css.set_uri('/home/lyrae/Desktop/dt/html/hi.css')
	
		
		# Filter for the dialogs
		filter = gtk.FileFilter()
		filter.set_name('css files')
		filter.add_pattern('*.css')
		self.filechooser_css.add_filter(filter)
		
		# Buttons
		self.button_go = gtk.Button('go!')
		self.button_apply = gtk.Button('Apply changes')
		self.button_dir = gtk.FileChooserButton(self.filechooser_dir)
		self.button_css = gtk.FileChooserButton(self.filechooser_css)
		
		# Hbox with file choosers
		self.hbox = gtk.HBox()
		self.hbox.pack_start(self.button_css)
		self.hbox.pack_start(self.button_dir)
		self.hbox.pack_start(self.button_go)
		
		# Holds the entire thing
		self.vbox = gtk.VBox()
		self.vbox.pack_start(self.hbox, expand=False)
		self.vbox.pack_start(scrolled_window)
		#self.vbox.pack_start(self.button_apply, expand=False)
   	
   		# Show window and everything in it
		self.window.add(self.vbox)
   		self.window.show_all()
   		
   		# Bind events
		self.button_go.connect("clicked", self.go)
	
	
	def go(self, e):
		self.liststore.clear()
		css_filename = self.filechooser_css.get_filename()
		html_dirname = self.filechooser_dir.get_filename()
		
		parser = Parser()
		
		# Scan css for selectors
		css = open(css_filename)		
		css_list = parser.parse_css(css.read())

		css_dict = {'class' : [], 'id' : []}
		for element in css_list:
			# First we search the string. If a '.' was found, it's a class, otherwise a '#' was found and it's an 'id'.
			# We then split the string at .|# and we'll have a list with 2 elements. we put them in tuples inside the
			# class dict ie. div#footer becomes ('div', footer') and we put that inside css_dict['id']
			if re.search('\.', element):
				type = 'class'
			else:
				type = 'id'
			
			split = re.split('\.|\#', element)
			css_dict[type].append( (split[0], split[1]) )
								
			


		# scan HTML files for tags/match/w.e
		# Since we're already traversing directories, search and store all images found in imgs[]
		imgs = []	# These are the actual image files found (ie, header.jpg, logo.png, etc)
		img_srcs = [] # The name of images found in the html <img src tag.
		# Types of files to scan
		filetypes = ('php', 'html', 'xhtml') # Add more to suit your needs :)
		
		# Image files extensions
		imgtypes = ('jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff')
		
		html_dict = {'class' : [], 'id' : []}
		for dirname, dirnames, filenames in walk(html_dirname):
			for filename in filenames:
				ext = filename.split('.')[-1].lower()
				if ext in filetypes:
					html = open(path.join(dirname, filename))
					
					# parse_html returns a tuple. first element is a list of all matched tags.
					# second element is a list of all images found in <img src=...' />
					# we loop through the elements/image names found in that list and and append it to
					# img_srcs[] so we can later compare img_srcs against imgs
					html_parse_result = parser.parse_html(html.read(), filename)
					html_list = html_parse_result[0]
					for image_name in html_parse_result[1]:
						img_srcs.append(image_name)

					# html_list is now a list, which holds list(s). example:
					# [ [2, hi.php, div, id, contact_form], [5, hi.php, div, class, wrapper] ].
					# those were all the elements found in filename. We now check the 4th element of each list
					# inside html_list, which will be either 'id' or 'class' and insert the list into the appropiate
					# dictionary key
	
					
					for i in html_list:
						type = i[3] # either 'class' or 'id'
						html_dict[type].append(i)

				elif ext in imgtypes:
					# File is an image. add it to imgs[]
					imgs.append(filename)


					
		self.compare(css_dict, html_dict, css_filename, imgs, img_srcs)
		
		
	def compare(self, css_dict, html_dict, css_filename, imgs, img_srcs):
		print imgs
		print img_srcs
		keys = ('class', 'id')
		for k in keys:

			for element in css_dict[k]:
				found = 0
				# remember: tuple[0] = html element(div, span, etc). tuple[1] = class or id of the element
				css_class = element[1]
				css_html_tag = element[0]
			
				#print 'we will now search HTML tuples for ', css_class , '... '
				# [line #, filename, html tag, 'class', 'wrapper', 'begin']
				for i in html_dict[k]:					
					html_tag = i[2]
					#print 'Searching ', i, ' for ', css_class , '... ',
					if css_class in i:
						found = 1
						#print 'Ok. we found ', css_class, ' in this tuple - ', i
						# Ok so there's a match. Say the css tuple is ('div', 'wrap'). This mean's the css file has a
						# selector like div.test {..}. If we're here, then 'wrap' was found inside an html tuple. However,
						# because the css's tuple's first element has a value, 'div', we check this html tuple (i) for a
						# value in position 0 as well. If it's 'div', then it's a match! Another scenario is if the css tuple
						# does not have a value in position 0, ie ('', 'wrap'). This means that the css selector was in
						# the form of .wrap { ... }, which means .wap may be applied to anything.	In such case,
						# we don't need to check the html tuple's first element
						if css_html_tag:
							# css's tuple first value is not ''.... so we also gotta check html's tuple first element.
							if not css_html_tag == html_tag:
								found = 0
								#print '! first element didnt match.. thus, not yet found.'

						if found == 1:
							# Found. Stop searching for this element, on to the next.
							break
				
			
				if found == 0:
					# the css selector is not being applied to any HTML tag.
					# So now it's time to show results on the GUI.
					# Were we searching for a class or id?
					if k == 'class':
						symbol = '.'
					else:
						symbol = '#'
					gui_string = css_html_tag + symbol + css_class
					if css_html_tag == '':
						output = 'The css %s <b>%s</b> was not found on any HTML tag' % (k, css_class)
					else:
						output = 'The css %s <b>%s</b> was not found on any %s tag' % (k, css_class, css_html_tag)
					self.liststore.append( ['<span foreground="#EE70C6">' + path.basename(css_filename) + '</span>', 'x', gui_string] )
					self.liststore.append( ['', '', output] )
		
			# Ok, we just looked at every element in the css dictionary and tried to find it in the html dictionary.
			# If an element wasn't found, then there's a selector in the css file (ie, .wrapper) that is not being applied
			# on any html tag. Now we reverse. We find all css classes and id's being applied to html tags, and see
			# if there is an equivalent in the css dictionary. This is to see for example, if <div class='wrapper', has 
			# a '.wrapper {}' in the css file.
			css_lists = css_dict[k]
			html_lists = html_dict[k]

			if k == 'id':
				symbol = '#'
			else:
				symbol = '.'	
				
			for list in html_lists:
				for i in list[4:]:
					f = 0
					output = ''	
					for tuple in css_lists:
										
						if i == tuple[1]:							
							f = 1
							# Pretend we have this css lists and tuples: [ ('p', 'wrapper'), ('div', 'wrapper') ]
							# and this html list: [ [0, 'index.html', 'div', 'class', 'wrapper'] ].
							# And that the loop is searching for 'wrapper' from the html list, in the css tuples.
							# Here, it will find wrapper in the first tuple, ('p', wrapper'). However, the tuple has a
							# value in its first element, an html tag of 'p', which means the css selector was
							# p.wrapper{..}. So we check our html list's 3rd element, which is an html tag. In this
							# case, it's a 'div'. We would report to the GUI here that 'wrapper' is being applied to a
							# 'p' tag and not 'div', but that's not true. It is also being a applied to a div (as you can 
							# see in the second tuple), the loop just hasn't gotten there yet. So we wanna make
							# sure ('div', 'wrapper') doesn't exist befoe reporting to the GUI.						
							if tuple[0] and not tuple[0] == list[2]:									
									tuple_to_find = (list[2], i)
									if not tuple_to_find in css_lists:
										f = 0
										output = "%s <b>%s</b> was <b>found in a &lt;%s&gt; </b> tag, but it's not\
										defined anywhere in\nthe css. This means you should have either	%s%s%s{..}\
										or %s%s{..}"\
										% (k, escape(tuple[1]), list[2], list[2], escape(symbol), tuple[1], escape(symbol), tuple[1])
						
							
					
					if f == 0:
						if not output or not css_lists:
							output = "%s  <b>%s is not defined</b> in the css file." % (k, i)

						self.liststore.append( ['<span foreground="blue">'+list[1]+'</span>', list[0]+1, i] )

						self.liststore.append( ['', '', output] )
					

		
		# Now, we search images. We only do it one-way. We check to see if elements from imgs[] are found in
		# img_srcs[]. If not, then the image is not being used in any <img src=.. />, aka wasting space on server :)
		for img in imgs:
			if img not in img_srcs:
				output = "<b>%s</b> is not being used in any &lt;img /&gt; tag." % img
				self.liststore.append( ['<span color="#164F05">' + img + '</span>', 'x', output] )
		
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False
	
	

def main():
	gtk.main()
	return 0

if __name__ == "__main__":
	hello = Unbloat()
	main()

