import smtplib
msg = "From: <sfss@paulus-teamer.ml>\r\nTo: %s\r\nSubject: %s\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: quoted-printable\r\n\r\n%s"

def send_mail(to, subj, mesg):
	server = smtplib.SMTP('smtp.web-utils.ml', 25)
	server.connect("smtp.web-utils.ml", 587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login('sfss@web-utils.ml', 'QsbPu7N0kJ4ijyEf')
	server.set_debuglevel(1)
	#print(msg % (to, subj, mesg))
	server.sendmail('sfss@web-utils.ml', to, msg % (to, subj, mesg))
	server.quit()
#TODO: chk for exploit