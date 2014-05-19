

smtp_ip = "localhost"
smtp_port = 25
inbox_path = "/var/mail/"
	
def is_peer_able(peer): 
	return True

def is_sender_able(sender):
	return True

def is_recipient_able(addressee):
	return True

def incoming_data_manager_(peer, mailfrom, rcpttos, data):
	print "My action"

incoming_data_manager = incoming_data_manager_
