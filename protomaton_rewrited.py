#!/usr/bin/env ipython

#-----------------------------------------------------------#
#		Protomaton v1 remastered                    #
#               Rewrited by Alexis AGGERY                   #
#-----------------------------------------------------------#

# importing libs
import os # used for os interaction
import sys # used to allow GPIO control
import picamera # used to control and get camera output
import time # used to get current time
import RPi.GPIO as GPIO # used to add GPIO easy control function
import twitter as tw # used to post photos on twitter
import cups # used to control the printers
from PIL import Image, ImageDraw, ImageFont # used to rendre stuff on image
import io # used to drw on the taken pic befor saving it
import pygame # used to create a drawable window

#-----------------------------------------------------------#
# 			VARS SETUP     			    #
#
pin_button_pic = 17
pin_button_stop = 23

on_screen_text = "Urban Move mentoring"

screen_w = 1280
screen_h = 1024

picam_w = 3280
picam_h = 2464

photo_dir = "/home/pi/Desktop/protomaton/photos/"

pic_ratio = 14.8/10.0

# setting up font
pygame.font.init()
fontused = pygame.font.SysFont("monospace", 30)
txt_font = ImageFont.truetype('/usr/share/fonts/truetype/digital/digital-7.ttf', 100)
# pre render
message = fontused.render("Photo prise, patientez...", 1, (255, 255, 255))

stream = io.BytesIO() # generating pic buffer

#-----------------------------------------------------------#

# calculating resolution
ratio_screen = float(screen_w)/float(screen_h)
ratio_cam = float(picam_w)/float(picam_h)

if ( pic_ratio < ratio_screen ):
	preview_w = int( float(screen_h) * pic_ratio )
	preview_h = screen_h
else :
	preview_w = screen_w
	preview_h = int( float(screen_w) / pic_ratio )
	
if ( pic_ratio < ratio_cam ):
	width = int( float(picam_h) * pic_ratio )
	height = picam_h
else :
	width = picam_w
	height = int( float(picam_w) / pic_ratio )
	
	
# setting up GPIO
#		MODES : BOARD use pysical numbering
#               BCM use virtual numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, GPIO.HIGH)

GPIO.setup(pin_button_pic, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_button_stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)



#--------------- setting up printer --------------
printer_conn = cups.Connection()
printers = printer_conn.getPrinters()
printer_name = printers.keys()[0]



#--------- setting up camera --------------

# preview_hFlip "True" or "False" defines if the preview is flipped or not, picture taken will not be flipped
preview_hFlip = False
camera = picamera.PiCamera()
camera.hflip = preview_hFlip
camera.resolution = (preview_w, preview_h)

camera.sharpness = 0
camera.contrast = 0
camera.brightness = 50
camera.saturation = 0
camera.iso = 100
camera.video_stabilization = False
camera.exposure_compensation = 0
camera.exposure_mode = 'auto'
camera.meter_mode = 'average'
camera.awb_mode = 'auto'
#camera.awb_mode = 'off'
#camera.awb_gains = (0.8,2.6)
camera.image_effect = 'none'

##'none'
##'negative'
##'solarize'
##'sketch'
##'denoise'
##'emboss'
##'oilpaint'
##'hatch'
##'gpen'
##'pastel'
##'watercolor'
##'film'
##'blur'
##'saturation'
##'colorswap'
##'washedout'
##'posterise'
##'colorpoint'
##'colorbalance'
##'cartoon'

camera.color_effects = None
camera.rotation = 0
camera.vflip = False
camera.zoom = (0.0, 0.0, 1.0, 1.0)



def countDown(): # draw count down on screen
	camera.annotate_background = picamera.Color('black')
    	camera.annotate_foreground = picamera.Color('white')
    	camera.annotate_text_size = 100
    	camera.annotate_text = '3'
    	time.sleep(1)
    	camera.annotate_text = '2'
    	time.sleep(1)
    	camera.annotate_text = '1'
    	time.sleep(1)
    	camera.annotate_text = ''
	

def takePhoto():
	screen.blit( message, ( ( screen_w - message.get_rect().width ) / 2, ( screen_h - message.get_rect().height ) / 2) )
	pygame.display.flip()
	
	countDown()
	
	camera.stop_preview()
	camera.hflip = False
	camera.resolution = (width, height)
	stream = io.BytesIO()
	current_time = time.strftime("%d %m %Y")
	file_name = time.strftime("%Y%m%d-%H%M%S")
	print "filename : " + file_name
	camera.capture( stream, format='jpeg' )
	stream.seek(0)
	photo_final = Image.open( stream )
	photo_final = photo_final.convert( 'RGBA' )
	stream.flush()
	txt_layer = Image.new( 'RGBA', photo_final.size, ( 255, 255, 255, 0 ) )
	draw = ImageDraw.Draw( txt_layer )
	draw.text( ( width - 550, height - 250 ), current_time[:8] + current_time[10:], font=txt_font, fill=( 255, 60, 0, 150 ) )
	draw.text( (200, height - 250 ), on_screen_text, font=txt_font, fill=( 255, 60, 0, 150 ) )
	out = Image.alpha_composite( photo_final, txt_layer )
	out.save( photo_dir + file_name + ".jpg", "JPEG" )
	printer_conn.printFile( printer_name, photo_dir + file_name + ".jpg", "RPI Printing photo ...", {} )
	display_img = pygame.image.load( photo_dir + file_name + ".jpg" )
	display_img = pygame.transform.scale( display_img, ( preview_w, preview_h ) )
	
	if ( pic_ratio < ratio_screen ):
		screen.blit( display_img, ( ( screen_w - display_img.get_rect().width ) / 2, 0 ) )
	else :
		screen.blit( display_img, ( 0, ( screen_h - display_img.get_rect().height ) / 2 ) )
		
	pygame.display.flip()
	time.sleep(5)
	
	# blank out screen
	screen.fill( ( 0, 0, 0 ) )
	pygame.display.flip()
	
	camera.hflip = preview_hFlip
	camera.resolution = ( preview_w, preview_h )
	camera.start_preview()



def Stop():
	camera.stop_preview()
	camera.close()
	pygame.quit()
	GPIO.cleanup()
	stream.close()
	
	
	
def Photo():
	takePhoto()
	
	
	
pygame.display.init()
screen = pygame.display.set_mode( ( screen_w, screen_h ), pygame.FULLSCREEN )
pygame.mouse.set_visible( False )
camera.start_preview()

while True:
	if (GPIO.input(pin_button_pic) == False):
		Photo()
	elif (GPIO.input(pin_button_stop) == False):
		Stop()
