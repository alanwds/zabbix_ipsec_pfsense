#!/usr/bin/env python
#For PF use /usr/local/bin/python2.7

import itertools
import re
import sys
from xml.dom import minidom

IPSEC_CONF = '/var/etc/ipsec/ipsec.conf'
PFSENSE_CONF = 'config.xml'
rtt_time_warn = 200
rtt_time_error = 300

import itertools
import re
import sys
from xml.dom import minidom

IPSEC_CONF = '/var/etc/ipsec/ipsec.conf'
PFSENSE_CONF = '/conf/config.xml'
rtt_time_warn = 200
rtt_time_error = 300

#Function to find phase description by ikeid
def findDescr(ikeid):

	#Check if the parameter was sent
	if not ikeid:
		return "Not found"
        #init a counter
        counter = 0
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

#Function to set correct format on ikeId. Recives conIDXXX, return ID
def formatIkeId(ikeid):
	
	#Convert list  into a string
	ikeid = ikeid[0]

	#If ikeid has 8 or more positions, get the position 3 and 4
	if len(ikeid) >= 8:
		ikeid = ikeid[3] + ikeid[4]
	else:
		#Else, get only the position 3. That is because some ikeids are small
		ikeid = ikeid[3]
        #print "The correct ike id is ", ikeid
        return ikeid

def parseConf():
    reg_conn = re.compile('^conn\s((?!%default).*)')
    reg_left = re.compile('.*leftid =(.*).*')
    reg_right = re.compile('.*rightid =(.*).*')
    data = {}
    with open(IPSEC_CONF, 'r') as f:
        for key, group in itertools.groupby(f, lambda line: line.startswith('\n')):
            if not key:
                conn_info = list(group)
                conn_tmp = [m.group(1) for l in conn_info for m in [reg_conn.search(l)] if m]
                left_tmp = [m.group(1) for l in conn_info for m in [reg_left.search(l)] if m]
                right_tmp = [m.group(1) for l in conn_info for m in [reg_right.search(l)] if m]
		if len(conn_tmp) > 0 :
			descr = findDescr(formatIkeId(conn_tmp))
		else:
			descr = "Not found"
                if conn_tmp and left_tmp and right_tmp:
                    data[conn_tmp[0]] = [left_tmp[0], right_tmp[0], descr]
        return data

def getTemplate():
    template = """
        {{ "{{#TUNNEL}}":"{0}","{{#TARGETIP}}":"{1}","{{#SOURCEIP}}":"{2}","{{#DESCRIPTION}}":"{3}" }}"""

    return template

def getPayload():
    final_conf = """{{
    "data":[{0}
    ]
}}"""

    conf = ''
    data = parseConf().items()
    for key,value in data:
        tmp_conf = getTemplate().format(
            key,
            value[1],
            value[0],
            value[2],
            rtt_time_warn,
            rtt_time_error
        )
        if len(data) > 1:
            conf += '%s,' % (tmp_conf)
        else:
            conf = tmp_conf
    if conf[-1] == ',':
        conf=conf[:-1]
    return final_conf.format(conf)

if __name__ == "__main__":
    ret = getPayload()
    sys.exit(ret)
