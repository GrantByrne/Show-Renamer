##  Title: Tv Show Manager
##  Created By: Grant Byrne
##  Purpose: This is a program which cleans up the filenames for television shows


#! /usr/bin/env python
import re
import glob
import os
from urllib2 import urlopen

####
# The Show Information Class
####
class Television:
    
    # Basically the Constructor
    def __init__(self, filename):
        self.filename = filename
        self.showName = "nothing"
        self.season = "nothing"
        self.episode = "nothing"
        self.episodeName = "nothing"
        self.fileExtension = "nothing"
        self.newFilename = "nothing"
        self.ready = False

    # Display All the Meaningful Data in a Clean Manner
    def display(self):
        print "Filename: " + self.filename
        print "Show Name: " + self.showName
        print "Season: " + self.season
        print "Episode: " + self.episode
        print "Episode Name: " + self.episodeName
        print "File Extension: " + self.fileExtension
        print "New Filename: " + self.newFilename
        if self.ready:
            print "Ready to write: Yes"
        else:
            print "Ready to write: No"

    # Determines whether the new show name is ready to be written
    # If it is ready to be written, change the variable to true
    # otherwise leave it as false
    def isItReady(self):
        if self.showName != "nothing":
            if self.season != "nothing":
                if self.episode != "nothing":
                    self.ready = True

    def createFilename(self):
        self.isItReady()
        
        if self.ready:
            self.newFilename = self.showName + " s" + self.season + "e" + self.episode

            if self.episodeName != "nothing" and self.showName != "Top Gear":
                self.newFilename += " - " + self.episodeName

            self.newFilename += self.fileExtension

    def rename(self):
        if self.ready:
            os.rename(self.filename, self.newFilename)

#finds the showname from the filename
#parameters: string of filename
#return: Name of the Show(string)

def findShowName(fileName):
    
    # takes in the list of shows from the show filename and puts it into a list to compare to
    shows = open("shows.txt", "r").read().split('\n')
    shows.pop()

    # set the default name of the show to "nothing"
    # if this gets returned, than the file should not be renamed
    # though as of right now, I think this whole thing generates an error
    foundShow = "nothing"

    # removes "." and "_" which might prevent 2+ word titles from being read
    lowerFilename = fileName.lower().replace('_', ' ').replace('.', ' ').replace("'", '')

    # I know this is push and shove programming, but I don't know a better way to do it
    # if the filename starts with "simpsons", then it adds the word "the " to the beginning
    if lowerFilename[0] == 's' and lowerFilename[1] == 'i' and lowerFilename[2] == 'm' and lowerFilename[3] == 'p' and lowerFilename[4] == 's' and lowerFilename[5] == 'o' and lowerFilename[6] == 'n':
        lowerFilename = "the " + lowerFilename

    # goes through the list of shows and fills in the show if it finds a match
    for show in shows:
        if lowerFilename.find(show.lower()) > -1:
            foundShow = show
        
    return foundShow

# Finds the Show Number from the filename
# parameters: name of the file
# return: string of the show num in the s##e## format
def findShowNum(fileName):
    
    ###
    # Clean up the filename to reduce false positives
    ###
    scrublist = ["1080p","720p","300mb","x264","."]
    for scrub in scrublist:
        lowerFilename = fileName.lower().replace(scrub," ")

    ###
    # This checks for the s##e## format
    ###
    p = re.compile('s(\d{1,2})e(\d{1,2})', re.IGNORECASE)
    res = p.findall(lowerFilename)

    if len(res) != 0:
        return "s" + res[0][0] + "e" + res[0][1]

    ###
    # Checks for an episode in the ##x## format
    # Note: does not accept #x## format
    ###
    p = re.compile('(\d{1,2})x(\d{1,2})', re.IGNORECASE)
    res = p.findall(lowerFilename)

    if len(res) != 0:
        return "s" + res[0][0] + "e" + res[0][1]

    ###
    # Checks for a show number in the ### format
    ###
    p = re.compile('(\d{4,4})', re.IGNORECASE)
    res = p.findall(lowerFilename)

    if len(res) != 0:
        return "s" + res[0][0] + res[0][1] + "e" + res[0][2] + res[0][3]

    ###
    # Checks for a show number in the ### format
    ###
    p = re.compile('(\d{3,3})', re.IGNORECASE)
    res = p.findall(lowerFilename)

    if len(res) != 0:
        return "s0" + res[0][0] + "e" + res[0][1] + res[0][2]
    
    return "nothing"

# Creates the URL to find the show information
# Parameters: takes in a string with the show name
# Return: string of the url for epguides.com

def generateUrl(showName):

    url = "http://epguides.com/" + showName.replace("The ", "").replace(' ','') + "/"

    return url

# Searches through an html file from epguides.com and finds the episode name
# Parameters: the html file, the formated episode number
def htmlSearch(htmlFile, epNum):

    epName = "nothing"

    # Searches the .html file for the episode information
    print "Searching with Value " + epNum
    
    found = int(htmlFile.find(epNum))

    if found > (-1):

        print "Found value of " + epNum
        print "Searching for '> found after " + epNum
        found = htmlFile.find("'>", found)

        if found > (-1):

            print "Found '> in this document"
            found2 = htmlFile.find("</a>", found)

            if found2 > (-1):

                epName = htmlFile[found+2:found2]

                #removes any html coding or special character that would cause problems when naming the file
                epName = epName.replace("&#039;","'").replace("&amp;","&").replace("?","").replace(":","").replace('"',"").replace('/',"")

    print "The Name of the show is: " + epName
    return epName


#Creates a string which formats the show num into something that can be search for on epguides.com
#parameters: the show number string
#return: string of the epguides.com search
def formatShowNumber(show):

    if show.season[0] != '0':
        episodeNum = show.season
    else:
        episodeNum = show.season[1]       

    episodeNum += "-" + show.episode
    
    return episodeNum

# Finds the Name of the Show on epguides.com
# parameters: list with the show names, numbers associated with each show
# return: list of the episode names
def findEpName(shows):

    for each in shows:
        each.display()
        print " "
    	
    # Starts the loop for going through the episodes
    x = 0
    while x < len(shows):
        
        # Figures out how many of the same show there are in the list to determine how many times to
        # search through the html file
        y = 0
        while x+y+1 < len(shows) and shows[x+y].showName == shows[x+y+1].showName:
            y += 1
        print "There are " + str(y) + " shows of the same name after this"

        #this downloads the html file for the website url
        data = urlopen(generateUrl(shows[x].showName)).read()

        z = 0
        while z <= y:
            print "show num: " + formatShowNumber(shows[x+z])
            shows[x+z].episodeName = htmlSearch(data, formatShowNumber(shows[x+z]))
            z += 1

        if y == 0:
            x += 1
        else:
            x += y

    return shows

######
# Actual Main Function
######

# Creates a list of all the video files in the directory
directory = glob.glob("*.avi") + glob.glob("*.ogm") + glob.glob("*.m4v") + glob.glob("*.mkv") + glob.glob("*.mp4")

# Creates a list to store all the show information
shows = list()

for each in directory:
    shows.append(Television(each))

for each in shows:

    # finds the show name
    each.showName = findShowName(each.filename)

    # finds the season and episode number
    something = findShowNum(each.filename)
    each.season = something[1:3]
    each.episode = something[4:6]

    # finds the file extension
    each.fileExtension = each.filename[len(each.filename)-4:len(each.filename)]

findEpName(shows)

for each in shows:
    each.createFilename()
    each.display()
    each.rename()
    print " "
