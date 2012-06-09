#!/usr/bin/python
# karotz module
from __future__ import division
import sys
import time
import karotz as kz

import Image
import ImageChops
import math, operator

import cgi, os
import cgitb; cgitb.enable()

# Import smtplib for the actual sending function
import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

import logging

#####################################################

STORAGE_DIR = '/home/karotz/'



#####################################################


# log
logger      = logging.getLogger('karotz')
hdlr        = logging.FileHandler('/var/log/karotz/cam.log')
formatter   = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
#logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)
# /log



# compares 2 pictures file, and returns a number
# we can consider pictures a the same < 50
def comparepic(file1, file2):
    im1 = Image.open(file1)
    im2 = Image.open(file2)
    logger.info('comparing...')
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value*((idx%256)**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    logger.info('rms: '+str(rms))
    return rms



# sends email to 'emailto', with file in 'attach'
def sendmail(subject,preamble,me,emailto,image):
    logger.info('Sending email to '+emailto+'...')
    COMMASPACE = ', '
    # Create the container (outer) email message.
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = me
    #msg['To'] = COMMASPACE.join(emailto)
    msg['To'] = emailto
    msg.preamble = preamble
    
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    msgText = MIMEText('Somebody @ home')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText('<b>HOME INTRUSION !</b> <br><img src="cid:image1"><br><a href="http://ks.baqs.net/cgi/karotz/snapshotlist.cgi">Full Picture List</a>', 'html')
    msgAlternative.attach(msgText)


    # Assume we know that the image files are all in PNG format
    # for file in pngfiles:
    # Open the files in binary mode.  Let the MIMEImage class automatically
    # guess the specific image type.
    fp = open(image, 'rb')
    img = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    img.add_header('Content-ID', '<image1>')
    msg.attach(img)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, emailto, msg.as_string())
    s.quit()





#	diff = comparepic(Image.open(STORAGE_DIR+"/last.jpg"),Image.open(STORAGE_DIR  + 'snapshot_2012_06_09_00_11_50.jpg') )
#	logger.info('diff:'+str(diff))
#	
#   sendmail('HOME INTRUSION','find picture attach','karotz@baqs.net','pierre@ourdouille.fr', STORAGE_DIR  + 'last.jpg')
#   logger.info('sendmail ')


form        = cgi.FieldStorage()
if form.has_key('sendfile'):
    sendfile    = form['sendfile']
    logger.info('Got a file...')

    if sendfile.file:
        logger.info('Got a file... yes')
        name = os.path.basename(sendfile.filename)
        open(STORAGE_DIR  + name, 'wb').write(sendfile.file.read())
        logger.info('File written into '+STORAGE_DIR  + name)

        # compare picture with last picture
        diff = comparepic(STORAGE_DIR+"/last.jpg",STORAGE_DIR  + name)
        #diff = 10.1

        # if change, send an alert email
        if diff > 50:
            # send email
            logger.warning('HOME INTRUSION !')
            sendmail('HOME INTRUSION','find picture attach','karotz@baqs.net','pierre@ourdouille.fr', STORAGE_DIR  + name)
            logger.info("/bin/cp "+STORAGE_DIR+name+" "+STORAGE_DIR+"/last.jpg")
            os.system("/bin/cp "+STORAGE_DIR+name+" "+STORAGE_DIR+"/last.jpg")
        else:
            logger.info('diff is less than 50, we do nothing')
            # if no change, then 
            # save as last
            # os.system("ln -sf "+STORAGE_DIR+name+" "+STORAGE_DIR+"/last.jpg")
            # remove last and replace by new one
            logger.info("/bin/mv "+STORAGE_DIR+name+" "+STORAGE_DIR+"/last.jpg")
            os.system("/bin/mv "+STORAGE_DIR+name+" "+STORAGE_DIR+"/last.jpg")

      # # take photo (will call me back :) )
      # settings = {}
      # settings['apikey']      = "1f224ded-ab7e-4d67-8589-819be67e3df9"
      # settings['installid']   = "f3376ae5-0d44-4370-bce6-391c0c004d95"
      # settings['secret']      = "6836a483-67c1-4d44-bcae-f0ab7ab545f7"


      # k = kz.Karotz(settings=settings)

      # #k = kz.Karotz()
      # request_uri = os.environ.get('REQUEST_URI', '')
      # server_name = os.environ.get('SERVER_NAME', '')
      # url = 'http'+server_name+request_uri
      # k.webcam.photo(url)
      # k.stop()

      # wait 30s
      # time.sleep(5)
    else:
        logger.error('Derp... could you try that again please?')
        message = "Derp... could you try that again please?"
else:
    # maybe it's callback
    data = sys.stdin.read()
    logger.info(data)

    logger.error('Please provide a sendfile')
    message = "Please provide a sendfile"

print """\
Content-Type: text/html\n
<html><body>
<p>%s</p>
</body></html>
""" % (message,)


