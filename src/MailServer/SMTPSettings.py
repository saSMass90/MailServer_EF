

class SMTPSettings:
	smtp_ip = "mail.masstests.com"
	smtp_port = 25
	inbox_path = "/var/mail2/"

	
	@staticmethod
	def is_peer_able(peer): 
		return True
	
	@staticmethod
	def is_sender_able(sender):
		return True

	@staticmethod
	def is_recipient_able(addressee):
		return True

	@staticmethod
	def incoming_data_manager_(peer, mailfrom, rcpttos, data):
		print "My action"

	incoming_data_manager = None
