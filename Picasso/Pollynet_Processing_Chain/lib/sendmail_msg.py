import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

def sendmail_msg(sender, recipient, subject, body, file=None):
	'''
	send email from sender to recipient.

	Parameters
	----------
	sender: string
		email account of the sender.
	recipient: list
		email account of the recipient.
	subject: string
		subject of the email.
	body: string
		body of the email.
	file: string
		attachments
	Notes
	-----
	In the rsd.tropos.de server, port 465 for connecting the gmail smtp server could be blocked by the administrator. Therefore, only the smtp.tropos.de sending server came to my mind to realize the task. However, authentication login is quite tricky for MS Exchange sending server. As a compromise, only this local email server was achieved regardless of the login.
	'''

	msg = MIMEMultipart()
	msg['From'] = sender
	msg['To'] = recipient
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))
	
	for f in file or []:
		with open(f, "rb") as fid:
			part = MIMEApplication(fid.read(), Name=basename(f))
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		msg.attach(part)	

	text = msg.as_string()
	s = smtplib.SMTP('smtp.tropos.de')
	s.sendmail('zhenping@tropos.de', recipient, text)
	s.quit

def main():
	sendmail_msg('zhenping@rsd.tropos.de', ['zhenping@tropos.de'], 'test message', 'hallo')

if __name__ == '__main__':
	sendmail_msg(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
