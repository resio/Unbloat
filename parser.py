import re
from os import walk, path
class Parser(object):
			
	def parse_css(self, css_file):
		''' Scan css file for selectors '''
		#TODO re-do this method so it returns a list like ['line #', 'filename', 'class|id', 'wrapper']
		# To do that we'll need to split the css content on the newlines.
		# and then use regexp to match:
		# 1. div.something { .. } span#hello { ... }   (2 selectors on same line)
		# 2. div.something, span#hello, .selector { }
		# 3. .selector { }
		# 4 ul.something li.something { ..
		# 5 div.something { ... } span#hello {...} .selector {
		#
		# }   
		# perhaps make a regexp for each and use a bunch of if's?

		# Replace everything inside { } and /* */ with ''
		selectors = re.sub('{[^}]+}|/\*[^*/]+\*/', '', css_file)

		css = re.findall('[a-z]*[\.?\#][a-z0-9-]+', selectors)
		
		# Now all that's left are the selectors.
		# They can be in the following format combos:
		# - div#wrapper, .something { }
		# - h3.something { }
		# - .some_class { }
		# - #some-ID { }
		# This regexp gets them all.
		return css
	#<img\s.*src\s*=\s*[\'?\"]*
	def parse_html(self, html_content, filename):
		''' Scan html file for class or ID tags '''
		
		# Append all lists to this list, then return this list to unbloat.py
		return_list = []
	
		# We also scan for <img? tags and get their src
		#img_srcs = re.findall('<img\s.*src\s*=\s*[\'?\"]*([(?:\w/)]+\.[\w]+)', html_content)
		img_srcs = re.findall('(?!<img\s*.+)[^/]+[\w]+[.]{1}[\w]+', html_content)

		html_line = html_content.split("\n")

		for line in range(len(html_line)):			
			# Scan the HTML line for any html element that has class= or id=. After scanned, if anything
			# found, it will look like ['<div class='wrapper'], or ['<div class='wrapper', <p class='intro'] if
			# more than one element was found in a line.
			scan = re.findall('<[^>]+(?:class|id)[\s?]*=\s*[\'"]?[\w\s-]+', html_line[line])
			
			# We break each element of scan down even more. The elements inside 'scan' are in this
			# format: ['<div class='wrapper'], and we want the elements in this format: ['class', 'wrapper']
			if scan:
				for html in scan:
					#print "HTML ---> ", html
					# Grab the HTML tag (div, span, p, h3, etc). Will be needed later.
					html_tag = re.findall('<([a-z0-9]+)', html)[0]
					#print "Our HTML tag is " + html_tag
					# Now format '<div class='wrapper'> into ['class', 'wrapper']
					properties = re.findall('((?:class|id)+)\s*=\s*[\'"](\s*[\w|\s-]+)', html)
					#print "Our properties are: ", properties
				
					# So 'properties' is a list with tuple(s) inside it. One tuple for 'class' and one tuple for 'id'.
					# So we could have something like [ ('class', 'wrapper sidebar'), ('id', 'contact') ]. This means
					# that the HTML tag was <div class="wrapper sidebar" id='contact'>. However, notice that
					# in the first tuple, there's a space separating the two classes 'wrapper' and 'sidebar'. We must
					# search each tuple's second element (we skip the first because it's either 'class' or 'id') and
					# split it at that space, so that we get something like [('class', 'wrapper', 'sidebar')]
					for tuple in properties:

						# The list that will be returned to unbloat.py. Actually, it's appened to return_list, and then
						# return_list is returned to unbloat.py. This list should be in this format:
						# [line #, 'class', 'property1', 'property2'...propertyN]. So for example, if we found
						# an html tag like this: <div class="wrapper sidebar" id='contact'>, final_list should be returned
						# like this [2, 'div', 'class', 'wrapper', 'sidebar'], and the next one would be 
						# [2, 'div', 'id', ''contact'], where '2' here is the line #. Then on neat.py, we insert the filename
						# right after the line #, so that we have [2, 'index.html, 'div', 'id', ''contact'],
						final_list = []
			
						# 'tuple' is in this format: ('class', 'wrapper') where first element is always either 'class' or 'id'. So 
						# we don't do anything with that first element. The second element, however, may be 1 or more
						# words separated by spaces, ie ('class', 'wrapper sidebar'). So we check each tuple's second
						# element for spaces, and if found, split() at every space.
						if re.search('\s', tuple[1]):
							# A space was found in the second element, 'wrapper begin'
							split = tuple[1].split() 
							# we now have ['wrapper', 'sidebar']
							for e in split:
								# Append 'wrapper' and 'sidebar' to list
								final_list.append(e)
						else:
							# No spaces were found, so no need to break it up. just append element into list
							final_list.append(tuple[1])
				
						# Now, we insert the first item in 'tuple' (in this case, 'class') into the list, so that we have
						# ['class', 'wrapper', 'sidebar']
						final_list.insert(0, tuple[0])
			
						# Append line #, filename, htmltag so that we return the final_list in this format:
						# [line #, filename, html tag, 'class', 'wrapper', 'begin']. We can't return final_list now because
						# that would exit the function, and only 1 list would be returned. So we store all lists inside
						# return_list and once the loop is complete, return return_list, which contains a bunch of lists
						# inside it.
						final_list.insert(0, html_tag)
						final_list.insert(0, filename)
						final_list.insert(0, line)
						return_list.append(final_list)
		return (return_list, img_srcs)


