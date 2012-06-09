karotz-cctv
===========

Transform your karotz in real CCTV system


2 parts needed:

kzphoto   : the launcher
upload.cgi: the web page (which will receive the photo from karotz)
karotz.py : improved version of pykarotz library 


1 mkdir /home/karotz/
2 chown www-data:www-data /home/karotz
3 edit kzphoto to match your needs
4 add kzphoto <url> to your crontab
5 <url> must match upload.cgi,and be publically accessible
