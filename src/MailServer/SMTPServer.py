
import os
import sys
import asyncore
import smtpd
import random
import md5
import imp
import traceback
from datetime import date

SMTPSettings = None

#from SMTPSettings import SMTPSettings

class EazySMTPServer(smtpd.SMTPServer):

	def process_message(self, peer, mailfrom, rcpttos, data):
		print "Peer: ", peer
		print "Mail from: ", mailfrom
		print "Rcpt to: ", rcpttos
		print "Data: ", data

		if not SMTPSettings.is_peer_able(peer):
			return '502 Error: {} not allowed to send mail'.format(peer) 
		
		if not SMTPSettings.is_sender_able(mailfrom):
			return '502 Error: <{}> is not a valid mail'.format(mailfrom)  
		
		if not	SMTPSettings.is_recipient_able(rcpttos):
			return '502 Error: <{}> is not a valid recipient'.format(rcpttos) 
		
		if not SMTPSettings.incoming_data_manager is None:
			SMTPSettings.incoming_data_manager(peer, mailfrom, rcpttos, data)
		else:
			for recipient in rcpttos:
				rcpt_path = SMTPSettings.inbox_path
				rcpt_path += recipient
				rcpt_path += SMTPSettings.inbox_path[-1]
				if not os.path.exists(rcpt_path):
	    				os.makedirs(rcpt_path)

				mail_name =  recipient
				mail_name +=  date.today().strftime('%Y%m%d')
				rcpt_path += mail_name

				mail = open(rcpt_path, "a" if os.path.isfile(rcpt_path) else "w")
				mail.write(data)
				mail.close()

def load_module(code_path):
    try:
        try:
            code_dir = os.path.dirname(code_path)
            code_file = os.path.basename(code_path)

            fin = open(code_path, 'rb')

            return  imp.load_source(md5.new(code_path).hexdigest(), code_path, fin)
        finally:
            try: fin.close()
            except: pass
    except ImportError, x:
        traceback.print_exc(file = sys.stderr)
        raise
    except:
        traceback.print_exc(file = sys.stderr)
        raise

def raise_server():
	print 'Loading SMTPSettings'
	global SMTPSettings 
	SMTPSettings = load_module('SMTPSettings.py')
	
	print "Starting SMTP server"
	print "IP: ", SMTPSettings.smtp_ip
	print "Port: ", SMTPSettings.smtp_port

	try:
		if not os.path.exists(SMTPSettings.inbox_path):
			print "Create path for the mail inbox: ", SMTPSettings.inbox_path
    			os.makedirs(SMTPSettings.inbox_path)

		return EazySMTPServer((SMTPSettings.smtp_ip, SMTPSettings.smtp_port), None)
	except:
		exception = sys.exc_info()[0]
		print "Error: ", exception
		return None

if __name__ == "__main__":
	raise_server()
	asyncore.loop()
