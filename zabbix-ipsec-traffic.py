#!/usr/bin/env python

import itertools
import re
import sys
from xml.dom import minidom

IPSEC_CONF = '/var/etc/ipsec/ipsec.conf'
PFSENSE_CONF = 'config.xml'
ikeid = 'con27000'
rtt_time_warn = 200
rtt_time_error = 300

def findDescr(ikeid):

        #Check if the parameter was sent
        if not ikeid:
                return "Not found"

	#init a counter
	counter = 0
	notFound = "No description"
	#parse xml file
	xmldoc = minidom.parse(PFSENSE_CONF)
	#Get all elements and save as a dictionary
	phase2list = xmldoc.getElementsByTagName('ipsec')

	#run the dic and find the description by ikeid
	for node in phase2list:
		#descrList=node.getElementsByTagName('descr')
		ikeIdList=node.getElementsByTagName('ikeid')	
		for i in ikeIdList:
			#if not empty
                        size = len(i.childNodes[0].nodeValue)
                        if size > 0:
				if i.childNodes[0].nodeValue == ikeid:
					#print i.childNodes[0].nodeValue
					#print node.getElementsByTagName('descr')[counter].firstChild.nodeValue 
					return node.getElementsByTagName('descr')[counter].firstChild.nodeValue
				counter += 1
	return notFound 

#Function to set
def formatIkeId(ikeid):
	#Remove last 3 chars from ikeid. The first 2 are  the ikeid, the last 3 are the phase2 ids
	ikeid = ikeid[:-3]
	#Remove the first 3 (con)
	ikeid = ikeid[3:]
	print "The correct ike id is " + ikeid
	return ikeid

descr = findDescr(formatIkeId(ikeid))
print descr














3
