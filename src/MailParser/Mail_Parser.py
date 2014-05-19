"""E-Mail parser for files written with MIME specs.  
   @version: 0.1"""

import re
from cStringIO import StringIO

class Mail:
	"""E-Mail Abstraction to analyze and represent the information contained in a mail input file.""" 

	
	mime_version = None #:MIME Version of the mail. Return None if version not found.
	attachments = [] #:All the contents attachments in the mail.
	
	regex_content_type = re.compile("Content-Type: ([a-zA-Z/]+);?")#:Regular expresion to search the content type in the attachment header.
	regex_mime_version = re.compile("MIME-Version: *([0-9]+[.0-9]*)")#:Regular expresion to search the MIME version of the mail.
	regex_boundary = re.compile("boundary=\"?([a-z0-9A-Z-_]+)\"?")#:Regular expresion to search the boundaries in the attachment header.
	regex_boundary_end = re.compile("(--[-_]*[a-z0-9A-Z]+[a-z0-9A-Z-_]+--)")#:Regular expresion to know if a boundary is of type end.
	regex_boundary_begin = re.compile("(--[-_]*[a-z0-9A-Z]+[a-z0-9A-Z-_]+)")#:Regular expresion to know if a boundary is of type begin.
	regex_charset = re.compile("charset=\"?([a-zA-Z-0-9]+)\"?[;]?")#:Regular expresion to search the charset in the attachment header.
	regex_filename = re.compile("filename=\"([a-zA-Z-_.0-9 ]+)\"[;]?")#:Regular expresion to search the filename in the attachment header.
	regex_name = re.compile("name=\"?([a-zA-Z-_.0-9 ]+)\"?[;]?")#:Regular expresion to search the name in the attachment header.
	regex_encoding = re.compile("Content-Transfer-Encoding: ([a-zA-Z/0-9-_]+[;]*);?")#:Regular expresion to search the encoding in the attachment header.

	class Attachment:
		"""Content abstraction that represent the content and data of a mail attachment.""" 
		content_type = None#:Respresent the value of Content-Type.
		charset = None#:Respresent the value of charset.
		name = None#:Respresent the value of name.
		file_name = None#:Respresent the value of filename.
		content_transfer_encoding = None#:Respresent the value of Content-Transfer-Encoding.
		content_disposition = None#:Respresent the value of Content-Disposition.
		content = None#:Content of the attachment.

	def __init__ (self, mail_data):
		"""Constructor that analyzes email content and renders it in the Mail object.
			@param mail_data: Mail to parse
   			@type mail_data: str or file""" 
		
		EOF = None
		mail_line = None
		mail_size = None

		input_type = type(mail_data)
		if input_type is str:
			mail_data = StringIO(mail_data)
			EOF = lambda: True if mail_line == "" else False

		elif input_type is file:
			import os
			mail_size = os.path.getsize (mail_data.name) 
			EOF = lambda: True if mail_data.tell() >= mail_size else False

		else:
			raise "Error: Wrong input type"
		
		last_boundary_type = "none"
		

		while not EOF():

			mail_line = mail_data.readline()

			if self.mime_version is None:	
				self.mime_version = self.get_info(self.regex_mime_version, mail_line)

			if last_boundary_type == "begin":
				while mail_line != "\n" and not EOF():

					content_type = self.get_info(self.regex_content_type, mail_line)
					if content_type == "multipart/alternative" or content_type == "multipart/mixed":
						break
					
					attachment = self.Attachment()
					attachment.content = StringIO()	
					attachment_parsed = False
					while not attachment_parsed:
						if attachment.charset is None:
							attachment.charset = self.get_info(self.regex_charset, mail_line)

						if attachment.file_name is None:
							attachment.file_name = self.get_info(self.regex_filename, mail_line)	

						if attachment.name is None:
							attachment.name = self.get_info(self.regex_name, mail_line)	
	
						if attachment.content_transfer_encoding is None:
							attachment.content_transfer_encoding = self.get_info(self.regex_encoding, mail_line)		
						
						if mail_line == "\n":
							last_boundary_type = "none"
							while last_boundary_type == "none":
								mail_line = mail_data.readline()
								last_boundary_type = self.get_boundary_type(mail_line)
								if last_boundary_type == "none":
									attachment.content.write(mail_line) 

							attachment_parsed = True
							self.attachments.append(attachment)

						if not attachment_parsed:
							mail_line = mail_data.readline()
					
					mail_line = mail_data.readline()



			last_boundary_type = self.get_boundary_type(mail_line)
			
		
		mail_data.close()
		

	@staticmethod
	def get_info(regex, mail_line):
		"""Get the info returned in a regular expresion search.
			@param regex: Regular expresion compile
    			@type regex: re
			@param mail_line: mail_line to analize to search the info
			@type mail_line: str""" 
		info = regex.search(mail_line) 
		return info.groups()[0] if info != None else None 
	
	@classmethod
	def get_boundary_type(self, data):
		"""Analize a boundarie and return the its type.
			@param data: Regular expresion compile
    			@type data: re"""
		boundary = self.regex_boundary_end.search(data)
		if boundary != None:
			return "end"

		boundary = self.regex_boundary_begin.search(data)
		if boundary != None:
			return "begin"

		return "none"
	
if __name__ == "__main__":
	
	import sys
	if len(sys.argv) != 2:
		print "Arguments invalid:\nExpected: python Mail_Server.py [File path]"
	else:
		mail = open(sys.argv[1], "r")
		mail_data = mail.read()
		print "Mail to parse: ", mail.name
		print "Size: ", len(mail_data)
		mail_info = Mail(mail_data)

		print "Mail info"
		print "Mime version: ", mail_info.mime_version
		print "\n"
		for attach in mail_info.attachments:
			print "File name: ", attach.file_name
			print "Name: ", attach.name
			print "Charset: ", attach.charset
			print "Encode name: ", attach.content_transfer_encoding
			print "Content: ", len(attach.content.getvalue())
			print "\n"

			if not (attach.file_name is None):
				f = open(attach.file_name, 'w')
				f.write(attach.content.getvalue().decode('base64','strict'))

			if not (attach.name is None):
				f = open(attach.name, 'w')
				f.write(attach.content.getvalue().decode('base64','strict'))
