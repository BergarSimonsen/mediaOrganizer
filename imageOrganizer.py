import exifread
import os
import argparse

parser = argparse.ArgumentParser(description='Source folder')
parser.add_argument('source', metavar='N', nargs='+', help='Source folder')
args = vars(parser.parse_args())


def getSource(args):
    src = args['source']
    if src[0] == '.':
        return os.getcwd()
    else:
        return src[0]

#inlyfiles = [f for f in listdir(path) if isfile(join(path,f)]

# Open image file for reading (binary mode)
f = open('vid.mov', 'rb')

# Return Exif tags
tags = exifread.process_file(f)

# testing, print all tags
#for tag in tags.keys():
#    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
#        print "Key: %s, value %s" % (tag, tags[tag])

for tag in tags.keys():
    print "Key %s, Value %s" % (tag, tags[tag])

#date_taken = tags["Image DateTime"]
#print date_taken
#x = str(date_taken)
#dt = x[0:4]
#print dt

def getDateTime(f):
    f = open(f, 'rb')
    tags = exifread.process_file(f)

    date_taken = tags["Image DateTime"]
    x = str(date_taken)
    dt = x[0:4]

    return dt



def readConfig():
    '''
    read the config file, return tuple of configs
    destination, supported image types, supported video types
    '''
    
    configFile = open('config.txt', 'r')

    dest = ''
    img = []
    vid = []

    tmp = configFile.readline()
    dest = tmp.split('\"')[1]
    tmp = configFile.readline()
    img = tmp.split('\"')[1].split(',')
    tmp = configFile.readline()
    vid = tmp.split('\"')[1].split(',')
    
    configFile.close()
        
    return dest, img, vid

def parseDest(dest):
    if not os.path.exists(dest):
        print "Destination dir does not exist, creating ", dest
        os.makedirs(dest)

dest, img, vid = readConfig()

src = getSource(args)

parseDest(dest)

files = os.listdir(src)

if(len(files) > 0):
    images = [x for x in files if os.path.isfile(x) and x.split('.')[1] in img]
    videos = [x for x in files if os.path.isfile(x) and x.split('.')[1] in vid]
    other  = [x for x in files if os.path.isfile(x) and not x.split('.')[1] in vid and not x.split('.')[1] in img]

for img in images:
    print img
    print getDateTime(img)

#for vid in videos:
#    print vid
#    print getDateTime(vid)

#print "images: ", images
#print "videos: ", videos
#print "other: ", other





