#!/usr/bin/env python

import itertools
import re
import sys
import xml.etree.cElementTree as ET

IPSEC_CONF = '/var/etc/ipsec/ipsec.conf'
PFSENSE_CONF = 'config.xml'
ikeid = 'con29000'
remoteid = '10.225.53.12'
rtt_time_warn = 200
rtt_time_error = 300

tree = ET.parse(PFSENSE_CONF)
root = tree.getroot()

def findDescr(remoteid,ikeid):

        #Check if the parameter was sent
        if not remoteid:
                return "Not found"

	#create search string. We use the "..." after the search to return the parent element of the current element.
	#The reason for that is the remoteid is a sub element of phase2 element 
	search = "./ipsec/phase2/remoteid/[address='" + remoteid + "']..."

	for tunnel in root.findall(search):
		descr = tunnel.find('descr').text

		#If we have only one result, we are talking about the correct tunnel
		if len(root.findall(search)) == 1:
			return descr

		#otherwise, if we have more than 1, we have to confirm the remoteid and the ikeid 
		#Case the ikeIds are the same, we got it. Case not, we pass and wait for next interation
		else:
			#Get the ikeid of this element
			ikeidElement = tunnel.find('ikeid').text
			if ikeidElement == ikeid:
				return descr

	return "Not found"

#Function to set
def formatIkeId(ikeid):
	#Remove last 3 chars from ikeid. The first 2 are  the ikeid, the last 3 are the phase2 ids
	ikeid = ikeid[:-3]
	#Remove the first 3 (con)
	ikeid = ikeid[3:]
	#print "The correct ike id is " + ikeid
	return ikeid

#descr = findDescr(formatIkeId(ikeid))
descr = findDescr(remoteid,formatIkeId(ikeid))
print descr
