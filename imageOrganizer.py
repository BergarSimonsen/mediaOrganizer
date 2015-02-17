import exifread
import os
import argparse

from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset
from hachoir_metadata import video

# Global variables
verbose = False
dest = ""
img = []
vid = []

def printVerb(msg):
    if verbose:
        print msg

def getSource(args):
    src = args['source']
    if src[0] == '.':
        return os.getcwd()
    else:
        return src[0]

def determineVerbose(args):
    global verbose
    verbose = args['v']

def getImageDateTime(f):
    f = open(f, 'rb')
    tags = exifread.process_file(f)

    try:
        date_taken = tags["Image DateTime"]
        x = str(date_taken)
        dt = x[0:4]
    except:
        print "Unable to extract metadata"
        exit(1)

    return dt

def getVideoDateTime(filename):    
    dt = ""
    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "Metadata extraction error: %s" % unicode(err)
        metadata = None
        if not metadata:
            print "Unable to extract metadata"
            exit(1)

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    for line in text:
        if line.startswith("- Creation date:"):
            dt = line.split()[3].split('-')[0]

    return dt

def readConfig():
    configFile = open('config.txt', 'r')

    global dest
    global img
    global vid

    tmp = configFile.readline()
    dest = tmp.split('\"')[1]
    tmp = configFile.readline()
    img = tmp.split('\"')[1].split(',')
    tmp = configFile.readline()
    vid = tmp.split('\"')[1].split(',')
    
    configFile.close()

def fetchFiles(src):
    files = os.listdir(src)
    if(len(files) > 0):
        images = [x for x in files if os.path.isfile(x) and x.split('.')[1].upper() in img]
        videos = [x for x in files if os.path.isfile(x) and x.split('.')[1].upper() in vid]
        other  = [x for x in files if os.path.isfile(x) and not x.split('.')[1].upper() in vid and not x.split('.')[1].upper() in img]

    return (images, videos)

def parseDest(dest):
    if not os.path.exists(dest):
        printVerb("Destination dir does not exist, creating " + dest)
        os.makedirs(dest)

def writeAllFiles(images, videos):
    printVerb("Writing %d images" % len(images))
    for img in images:
        writeImage(img)

    printVerb("Done writing images.")
    printVerb("Writing %d videos" % len(videos))
    for vid in videos:
        writeVideo(vid)

    printVerb("Done writing %d files." % (len(images) + len(videos)))

def writeImage(f):
    dt = getImageDateTime(f)
    di = dest + "/" + dt
    newFile = di + "/" + f
    if not os.path.exists(di):
        printVerb("Creating directory " + di)
        os.makedirs(di)
        
    printVerb("Writing file " + f)
    fileExist(f, di, newFile)
    if os.path.isfile(newFile):
        newFile = fileExist(f, di, newFile)
    printVerb("Destination file exists, renaming to " + newFile.split('/')[-1])
    write(f, newFile)

def writeVideo(f):
    dt = getVideoDateTime(f)
    di = dest + "/" + dt
    newFile = di + "/" + f
    if not os.path.exists(di):
        printVerb("Creating directory " + di)
        os.makedirs(di)
        
    printVerb("Writing file " + f)
    fileExist(f, di, newFile)
    if os.path.isfile(newFile):
        newFile = fileExist(f, di, newFile)
    printVerb("Destination file exists, renaming to " + newFile.split('/')[-1])
    write(f, newFile)    


def fileExist(f, di, nf):
    count = 0
    while os.path.isfile(nf):
        tmp = f.split('.')
        f = tmp[0] + "_" + str(count) + "." + tmp[1]
        nf = di + "/" + f
    return nf

def write(f, newFile):
    with open(f, 'rb') as f1:
        data = f1.read()
    with open(newFile, 'wb') as f2:
        f2.write(data)
    

def main():
    parser = argparse.ArgumentParser(description='Source folder')
    parser.add_argument('source', metavar='N', nargs='+', help='Source folder')
    parser.add_argument('-v', action='store_true', required = False)
    args = vars(parser.parse_args())

    determineVerbose(args)
    readConfig()
    src = getSource(args)
    parseDest(dest)
    images, videos = fetchFiles(src)

    writeAllFiles(images, videos)

#    writeFile(images[0])

#    print images
#    print videos

    
    '''
    print "img", img
    print "vid", vid
    print "dest", dest
    print "images", images
    print "videos", videos
    print "other", other
    '''

if __name__ == "__main__": main()









#    print makePrintable(line, charset)

#for img in images:
#    print img
#    print getDateTime(img)

#for vid in videos:
#    print vid
#    print getDateTime(vid)

#print "images: ", images
#print "videos: ", videos
#print "other: ", other


'''



if len(argv) != 2:
    print >>stderr, "usage: %s filename" % argv[0]
    exit(1)
filename = argv[1]

filename, realname = unicodeFilename(filename), filename
parser = createParser(filename, realname)
if not parser:
    print >>stderr, "Unable to parse file"
    exit(1)
try:
    metadata = extractMetadata(parser)
except HachoirError, err:
    print "Metadata extraction error: %s" % unicode(err)
    metadata = None
if not metadata:
    print "Unable to extract metadata"
    exit(1)

text = metadata.exportPlaintext()
charset = getTerminalCharset()
for line in text:
    print makePrintable(line, charset)
'''
#inlyfiles = [f for f in listdir(path) if isfile(join(path,f)]

# Open image file for reading (binary mode)
#f = open('vid.mov', 'rb')

# Return Exif tags
#tags = exifread.process_file(f)

# testing, print all tags
#for tag in tags.keys():
#    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
#        print "Key: %s, value %s" % (tag, tags[tag])

#for tag in tags.keys():
#    print "Key %s, Value %s" % (tag, tags[tag])

#date_taken = tags["Image DateTime"]
#print date_taken
#x = str(date_taken)
#dt = x[0:4]
#print dt




