#! /usr/bin/env python

# Libraries
import smtplib
import smtpd
import asyncore
import email
import sys
import httplib, urllib
import re
from email.mime.text import MIMEText
from email.parser import HeaderParser


print 'Starting custom mail server'

###########
###########
# Email Tools
###########
###########

class EmailUtils:
    email_pattern = re.compile('([a-zA-Z0-9])+([a-zA-Z0-9\._-])*@([a-zA-Z0-9_-])+([a-zA-Z0-9\._-]+)+')
    @staticmethod
    def forward_message(data, redirectto):
        from_adr='redirect@myserver.com'
#      Forward a message (we change the From tag in the email headers wich I guess is not perfect, I'm not an email expert)
        msg=email.message_from_string(data)
        try:
            msg.add_header('Resent-from', from_adr);
#            msg.replace_header('Subject', '[DI] '  + msg['subject'])
        except KeyError:
            pass
#      Note we are usng port 6625 here as we've changed the Postfix port
        s = smtplib.SMTP('localhost','6625')
        s.sendmail(from_adr, redirectto, msg.as_string())
        s.quit()
        return

    @staticmethod
    def text_message(mfrom,to,topic,body):
#      Send an email with a simple text message
        msg=MIMEText(body);
        msg['Subject'] = topic
        msg['From'] = mfrom
        msg['To'] = to 
#      Note we are usng port 6625 here as we've changed the Postfix port
        s = smtplib.SMTP('localhost','6625')
        s.sendmail(mfrom, to, msg.as_string())
        s.quit()
        return


################
################
# WebService Tools
################
################

class WebServiceUtils:
    @staticmethod
    def newsletter(subscribe,email,source):
#      A method to call your newsletter webservice
#      This must be adapted to your needs
        params = urllib.urlencode({'subscribe': subscribe, 'email': email, 'source': source})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("www.myserver.com")
        conn.request("POST", "/newsletter/subscribe.php", params, headers)
        response = conn.getresponse()
        print response.status, response.reason, response.read()
        conn.close()
        return


##########################################################
# Send an email to yourself to be notified of the email server being started
##########################################################
EmailUtils.text_message('auto@myserver.com','myaddress@gmail.com','mail server started','automatic email');


#############
#############
# SMTP SERVER
#############
#############

class CustomSMTPServer(smtpd.SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):
        print 'Receiving message from:', peer
        print 'Message addressed from:', mailfrom
        print 'Message addressed to  :', rcpttos
        print 'Message length        :', len(data)
        print data
#      Flush the output buffered (handy with the nohup launch)
        sys.stdout.flush()
#      Analyze data headers
        parser = HeaderParser()
        msg = parser.parsestr(data)
        subject=''
        try:
            subject=msg['Subject']
            subject=subject.lower()
        except:
            print "Subject error:", sys.exc_info()[0]
        print 'Message subject       :', subject

#      Determine action (0 : nothing to do, 1 : unsubscribe, 2 subscribe)
#      We will determine the action to do with the receivers of the message
#      But that could be done also with the Subject of the email (and anything else you can imagine)
        action=0
#      Unsubscribe action, parse receivers and look for 'unsubscribe' in the email address
        if (action==0):
            for to in rcpttos:
                if (to.find('unsubscribe')>=0):
                    action=1
#      Subscribe action, parse receivers and look for 'subscribe' in the email address
        if (action==0):
            for to in rcpttos:
                if (to.find('subscribe')>=0):
                    action=2

        if (action==1):
            print 'Unsubscribe';
            WebServiceUtils.newsletter(0,mailfrom,'secret')
        elif (action==2):
            print 'Subscribe';
            WebServiceUtils.newsletter(1,mailfrom,'secret')
        else:
            EmailUtils.forward_message(data, 'mass90.mass@gmail.com')

#      Flush the output buffered (handy with the nohup launch)
        sys.stdout.flush()
        return

# Replace with the IP of your server
server = CustomSMTPServer(('107.170.144.43', 25), None)

# Wait for incoming emails
asyncore.loop()
