##
##  Agisoft Automatic Processing Script   
##  Release 1.0 - 20 April 2016           
##  Written/Assembled by richard@3dmij.nl 
##  For more info: www.pi3dscan.com  
##
##  Copyright 2016 - Richard Garsthagen
##  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
##  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
##  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
##  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
##  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
##  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##
import PhotoScan
import math
import os
import time
import json
import urllib.request
import zipfile
import requests

##########################################
##                                      ##
##   Configure your variables           ##
##                                      ##
##########################################

MonitorDirectory = "c:\\monitor\\"
RunOnce = 0    # 1= Run Once  0=Keep scanning for new tasks

# Agisoft processing settings
MaskTolerence = 10
keypointLimit=10000 
tiepointLimit=50000
removecomponentsmax = 10000  # remove smaller mesh components
smoothmodellevel = 1        # set to 0 to disable smoothing, max is 3

#  Floormate marker definition  
#
#   py
#   
#   |
#   |
#   |
#   
#   p0 ------------ px

p0 = "target 3"   
px = "target 4"
py = "target 1"

distancepx = 0.7		# Change values is you are not using the A1 floormat posted 
distancepy = 0.4		# on www.pi3dscan.com

boxwidth = 1.2  		# Region with in meters
boxdepth = 1  			# Region depth in meters
boxheight = 2.240		# Region height, middle point is fixed based on your center targets

# Center targets
c1target = "target 21"	# 2 targets on the left side of scanner, middle height
c2target = "target 22"
c3target = "target 6"		# 2 targets on the right side of scanner, middle height
c4target = "target 7"

# Your Sketchfab settings
# ENABLE / DESCRIPTION can be overwritten by JSON file
SKETCHFAB_ENABLE = 0  	   # 0=Disable file zipping and sketchfab upload, 1=Enable zipping and sketchfab upload
SKETCHFAB_DOMAIN = 'sketchfab.com'
SKETCHFAB_API_URL = 'https://api.{}/v2/models'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_MODEL_URL = 'https://{}/models/'.format(SKETCHFAB_DOMAIN)
SKETCHFAB_API_TOKEN = "xxxx"  #  !! IMPORTANT : Set to your own Sketchfav API 
SKETCHFAB_DESCRIPTION = "Created by xxxxxx"		# Set your default description
SKETCHFAB_PASSWORD = ""  			# requires a pro account
SKETCHFAB_PRIVATE = 1  				# requires a pro account
SKETCHFAB_TAGS = "character" 	# space-separated list of tags

##########################################
##                                      ##
##   End of variables                   ##
##                                      ##
##########################################


def log(msg):
	print (msg)
	logfile = open(MonitorDirectory + "Process_log.txt", "a")
	logfile.write(time.strftime("%H:%M:%S") + msg + "\n")
	logfile.close()
		
def list_files(path):
    # returns a list of names (with extension, without full path) of all files 
    # in folder path
    files = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            files.append(name)
    return files 

def upload(data, files):
	log ("Uploading to setchfab...")
	try:
		r = requests.post(SKETCHFAB_API_URL, data=data, files=files, verify=False)
	except requests.exceptions.RequestException as e:
		log ("Upload error occured")
		return

	result = r.json()

	if r.status_code != requests.codes.created:
		log ("Upload failed with error")
		return

	model_uid = result['uid']
	model_url = SKETCHFAB_MODEL_URL + model_uid
	log ("Upload successful. Your model is being processed.")
	log ("Once the processing is done, the model will be available at: " + model_url )
	return model_url


def processscan(scanfile):
	configfile= MonitorDirectory + scanfile
	log("JSON file: " + configfile)
	config = json.loads(open(configfile).read())
	scanid = config["scanid"]
	normaldir = config["normaldir"]
	projectdir = config["projectdir"]
	savedir = config["savedir"]
	
	try:
		SKETCHFAB_ENABLE = config["SKETCHFAB_ENABLE"]
		log("Taking JSON setting for sketchfab enable")
	except:
		log("Taking default sketchfab setting from main script")

	try:
		SKETCHFAB_DESCRIPTION = config["SKETCHFAB_DESCRIPTION"]
		log("Taking JSON setting for sketchfab description")
	except:
		log("Taking sketchfab description from main script")
	
  # STEP 1 - Load Images
	doc = PhotoScan.app.document
	doc.clear()
	chunk = doc.addChunk()
	photos = os.listdir(normaldir) # Get the photos filenames
	photos = [os.path.join(normaldir,p) for p in photos] # Make them into a full path
	log( "Found {} photos in {}".format(len(photos), normaldir))
	if not chunk.addPhotos(photos):
		log( "ERROR: Failed to add photos: " + str(photos))

  # STEP 2 - Detect Markers
	log ("Dectecting markers on non-projected images")
	chunk.detectMarkers(PhotoScan.TargetType.CircularTarget12bit, 50)
	
  # STEP 3 - Create auto mask, if empty directory is specified in JSON file
	try:
		emptydir = config["emptydir"]
		log("Mask directory found, going to create auto mask")
	except:
		emptydir = ""
		log("No mask directory set, no auto making will take place")
	if (emptydir != ""):
		log ("Creating auto mask based on non-projected images")
		maskpath = emptydir + "{filename}.jpg"
		chunk.importMasks(maskpath, method='background', tolerance=MaskTolerence)

  # STEP 4 - Change images to projection images
	log("Switching to projection images")
	for i in range(len(chunk.cameras)):
		camera = chunk.cameras[i]
		photo = camera.photo.copy()
		photo.path = projectdir + camera.label
		camera.photo = photo

  # STEP 5 - Align Images
	chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy,preselection=PhotoScan.NoPreselection, filter_mask=True, keypoint_limit=keypointLimit, tiepoint_limit=tiepointLimit)
	chunk.alignCameras()


  # STEP 6 - Create Auto Bounding box
	mp0 = 0
	mpy = 0
	mpx = 0
	fp0 = 0
	fpy = 0
	fpx = 0
	#setting for Y up, Z forward -> needed for mixamo/unity
	vector0 = PhotoScan.Vector((0,0,0))
	vectorY = PhotoScan.Vector((0,0,distancepy))   # Specify Y Distance
	vectorX = PhotoScan.Vector((distancepx,0,0))   # Specify X Distance
	c1 = 0
	c2 = 0
	c3 = 0
	c4 = 0
	c = 0

	for m in chunk.markers:
		if m.label == c1target:
			log ("Center 1 point found")
			c1 = c
		if m.label == c2target:
			log ("Center 2 point found")
			c2 = c
		if m.label == c3target:
			log ("Center 3 point found")
			c3 = c
		if m.label == c4target:
			log ("Center 4 point found")
			c4 = c
		if m.label == p0: 
			mp0 = c
			fp0 = 1
			m.reference.location = vector0
			m.reference.enabled = 1
			log ("Found floormat center point")
		if m.label == py: 
			mpy = c
			fpy = 1
			m.reference.location = vectorY
			m.reference.enabled = 1
			log ("found floormat Y point")
		if m.label == px: 
			mpx = c
			fpx = 1
			m.reference.location = vectorX
			m.reference.enabled = 1
			log ("found floormat X point")
		c = c + 1  
  
	if fp0 and fpx and fpy:
		log ("Found all markers")
		chunk.updateTransform()
	else:
		log ("Error: not all markers found")

	newregion = chunk.region

	T = chunk.transform.matrix
	v_t = T * PhotoScan.Vector( [0,0,0,1] )
	m = PhotoScan.Matrix().diag([1,1,1,1])	

	m = m * T
	s = math.sqrt(m[0,0] ** 2 + m[0,1] ** 2 + m[0,2] ** 2) #scale factor
	R = PhotoScan.Matrix( [[m[0,0],m[0,1],m[0,2]], [m[1,0],m[1,1],m[1,2]], [m[2,0],m[2,1],m[2,2]]])
	R = R * (1. / s)
	newregion.rot = R.t()

 	# Calculate center point of the bounding box, by taking the average of 2 left and 2 right markers 
	mx = (chunk.markers[c1].position + chunk.markers[c2].position + chunk.markers[c3].position + chunk.markers[c4].position) / 4

	mx = PhotoScan.Vector([mx[0], mx[1], mx[2]])
	newregion.center = mx

	dist = chunk.markers[mp0].position - chunk.markers[mpy].position
	dist = dist.norm()

	ratio = dist / distancepy

	newregion.size = PhotoScan.Vector([boxwidth* ratio, boxheight* ratio, boxdepth * ratio])

	chunk.region = newregion
	chunk.updateTransform()

	log("Bounding box should be aligned now")

  # STEP 7 - Create Dense Cloud 
	chunk.buildDenseCloud(quality=PhotoScan.HighQuality, filter=PhotoScan.AggressiveFiltering)

  # STEP 8 - Create MESH
	chunk.buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation,  face_count = PhotoScan.HighFaceCount)

	# STEP 9 - Switch projection images back to normal images
	for i in range(len(chunk.cameras)):
		camera = chunk.cameras[i]
		photo = camera.photo.copy()
		photo.path = normaldir + camera.label
		camera.photo = photo

	# STEP 10 - Do some basic clean up operations
	try:
		chunk.model.removeComponents(removecomponentsmax)
	except:
		log("Error Removing small components")
	try:
		chunk.model.fixTopology()
	except:
		log("Error Fix topology")
	try:
		chunk.model.closeHoles(100)
	except:
		log("Error closing holes")
	try:
		if smoothmodellevel > 1:
			chunk.smoothModel(smoothmodellevel)
	except:
		log("Error smoothing model")

	# STEP 11 - Create UVmap and Texture
	chunk.buildUV(mapping=PhotoScan.GenericMapping)
	chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=8196)

	# STEP 12 - Save files
	doc.save(savedir + scanid + ".psz")
	modelpath = savedir + scanid + ".obj"
	chunk.exportModel(modelpath, binary=True, precision=6, texture_format="jpg", texture=True, normals=True, colors= True, cameras=False, format="obj")

	# STEP 13 - Zip files
	if SKETCHFAB_ENABLE:
		log("Zipping files to upload to sketchfab")
		zf = zipfile.ZipFile(savedir + scanid + ".zip", mode="w")
		try:
			zf.write(savedir + scanid + ".mtl")
			zf.write(savedir + scanid + ".obj")
			zf.write(savedir + scanid + ".jpg")
		finally:
			zf.close()
		zip_file = savedir + scanid + ".zip"

		# STEP 14 - Upload to sketchfab
		data = {
			'token': SKETCHFAB_API_TOKEN,
			'name': scanid,
			'description': SKETCHFAB_DESCRIPTION,
			'tags': SKETCHFAB_TAGS,
			'private': SKETCHFAB_PRIVATE,
			'password': SKETCHFAB_PASSWORD
		}

		f = open(zip_file, 'rb')
		files  = {
			'modelFile': f
		}
		
		try:
			log("Uploading.. agisoft will pretend to hang while uploading, please wait")
			PhotoScan.app.update()
			model_url = upload(data, files)
			sfile = open(savedir + scanid + "_sketchfabURL.txt", "w")
			sfile.write(model_url)
			sfile.close()
			log("Uploaded to Sketchfab")
		finally:
			f.close()
			
	log("==============================================================================")
	log(" Completeted processing: " + scanid)
	log("==============================================================================")

log("Starting automatic processing engine")
PhotoScan.app.update()

L=0
while (L<1):
	print("Checking for new tasks..")
	PhotoScan.app.update()
	lst = list_files(MonitorDirectory)
	for f in lst:
		if f.endswith(".json", 0, len(f)):
			#try:
			log ("Found: " + f)
			processscan(f)
			#except:
			#	log ("General error processing scan: " + f)
			taskfile = MonitorDirectory +  f
			os.rename(taskfile, taskfile + ".done")
	time.sleep(5)
	PhotoScan.app.update()
	L=L+RunOnce
	 
	 
log("The End") 


