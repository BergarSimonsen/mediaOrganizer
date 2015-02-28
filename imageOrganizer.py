import exifread
import os
import argparse

from os import listdir
from os.path import isfile, join

# Video metadata
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset
from hachoir_metadata import video

# Global variables
verbose       = False
separateVideo = False
duplicates    = True
dest          = ""
img           = []
vid           = []
src           = ""

# Default config file params
defaultDest   = 'destination="%s/images"' % os.getcwd()
defaultImages = 'imageTypes="JPG,JPEG"'
defaultVideos = 'videoTypes="AVI,MKV,MOV,MP4,MPEG,MPG,WMV"'

def printVerb(msg):
    if verbose: print msg

def absFile(f):
    return src[0] + "/" + f

def getSource(args):
    global src
    src = args['source']
    if src[0] == '.':
        return os.getcwd()
    else:
        return src[0]

def determineVerbose(args):
    global verbose
    verbose = args['v']

def separateVideo(args):
    global separateVideo
    separateVideo = args['s']

def determineDuplicates(args):
    global duplicates
    duplicates = not args['d']

def getImageDateTime(f):
    f1 = absFile(f)
    f = open(f1, 'rb')
    tags = exifread.process_file(f)

    try:
        date_taken = tags["Image DateTime"]
        x = str(date_taken)
        dt = x[0:4]
    except:
        print "Unable to extract metadata for file %s" % f1
        dt = "misc"
#        exit(1)

    return dt

def getVideoDateTime(filename): 
    dt = ""
    filename, realname = unicodeFilename(absFile(filename)), absFile(filename)
    parser = createParser(filename, realname)
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "Metadata extraction error: %s" % unicode(err)
        metadata = None
        if not metadata:
            print "Unable to extract metadata for file %s" % filename
#            exit(1)

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    for line in text:
        if line.startswith("- Creation date:"):
            dt = line.split()[3].split('-')[0]

    return dt

def readConfig(count = 1):
    printVerb("Reading config.")
    try:
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
    except:
        if count == 1:
            print "Config file could not be found. Creating default config file."
            makeConfig()
            readConfig(2)
        else:
            print "Error reading config file. Exiting."
            exit(1)
        

def makeConfig():
    try:
        conf = open("config.txt", "w")
        conf.write(defaultDest + "\n")
        conf.write(defaultImages + "\n")
        conf.write(defaultVideos + "\n")
        conf.close()
        print 'Config file %s created successfully' % ('"' + os.getcwd() + '/config.txt"')
    except:
        print "Could not create config file. Exiting."
        exit(1)

def fetchFiles(src):
    printVerb("Fetching files in %s" % src)
    files = [f for f in listdir(src[0]) if isfile(join(src[0],f))]
    if(len(files) > 0):
        images = [x for x in files if x.split('.')[1].upper() in img]
        videos = [x for x in files if x.split('.')[1].upper() in vid]
        # other  = [x for x in files if os.path.isfile(x) and not x.split('.')[1].upper() in vid and not x.split('.')[1].upper() in img]

    printVerb("Found %d files. %d images, %d videos" % ((len(images) + len(videos)), len(images), len(videos)))

    return (images, videos)

def parseDest(dest):
    if not os.path.exists(dest):
        printVerb("Destination dir does not exist, creating " + dest)
        os.makedirs(dest)

def writeAllFiles(images, videos):
    printVerb("Writing %d images..." % len(images))

    for img in images:
        printVerb("Fetching metadata for %s" % img)
        writeFile(img, True)

    printVerb("Done writing images.")
    printVerb("Writing %d videos" % len(videos))
    for vid in videos:
        printVerb("Fetching metadata for %s" % img)
        writeFile(vid, False)

    printVerb("Done writing %d files." % (len(images) + len(videos)))

def writeFile(f, isImg):
    if isImg:
        dt = getImageDateTime(f)
    else:
        dt = getVideoDateTime(f)

    di = dest + "/" + dt

    if not isImg and separateVideo:
        di = di + "/video"

    newFile = di + "/" + f
    if not os.path.exists(di):
        printVerb("Creating directory " + di)
        os.makedirs(di)
        
    printVerb("Writing file " + f)
    if os.path.isfile(newFile) and duplicates:
        newFile = fileExist(f, di, newFile)
        printVerb("Destination file exists, renaming to " + newFile.split('/')[-1])
    write(f, newFile)

def fileExist(f, di, nf):
    nf1 = nf
    f1 = f
    di1 = di

    count = 0
    while os.path.isfile(nf1):
        nf1 = nf
        f1 = f
        di1 = di

        tmp = f.split('.')
        f1 = tmp[0] + "_" + str(count) + "." + tmp[1]
        nf1 = di1 + "/" + f1
        count = count + 1
    return nf1

def write(f, newFile):
    fFull = absFile(f)
    with open(fFull, 'rb') as f1:
        data = f1.read()
    with open(newFile, 'wb') as f2:
        f2.write(data)
    

def main():
    parser = argparse.ArgumentParser(description='Source folder')
    parser.add_argument('source', metavar='Source Folder', nargs='+', help='Source folder')
    parser.add_argument('-v', action='store_true', required = False, help='Verbose')
    parser.add_argument('-s', action='store_true', required = False, help='Separate folder for videos')
    parser.add_argument('-d', action='store_true', required = False, help='Do not keep duplicates. Default is to keep duplicates.')
    args = vars(parser.parse_args())

    determineVerbose(args)
    separateVideo(args)
    determineDuplicates(args)
    readConfig()
    getSource(args)
    parseDest(dest)

    images, videos = fetchFiles(src)

    writeAllFiles(images, videos)

    printVerb("Finished writing files. Exiting.")

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




