#!/usr/local/bin/python2.7

import itertools
import re
import sys
import xml.etree.cElementTree as ET

IPSEC_CONF = '/var/etc/ipsec/ipsec.conf'
PFSENSE_CONF = '/conf/config.xml'
rtt_time_warn = 200
rtt_time_error = 300

#Parse the XML
tree = ET.parse(PFSENSE_CONF)
root = tree.getroot()

#Function to find phase description by ikeid
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
    reg_rightsubnet = re.compile('.*rightsubnet =(.*).*')
    data = {}
    with open(IPSEC_CONF, 'r') as f:
        for key, group in itertools.groupby(f, lambda line: line.startswith('\n')):
            if not key:
                conn_info = list(group)
                conn_tmp = [m.group(1) for l in conn_info for m in [reg_conn.search(l)] if m]
                left_tmp = [m.group(1) for l in conn_info for m in [reg_left.search(l)] if m]
                right_tmp = [m.group(1) for l in conn_info for m in [reg_right.search(l)] if m]
                rightsubnet_tmp = [m.group(1) for l in conn_info for m in [reg_rightsubnet.search(l)] if m]
		if len(conn_tmp) > 0 :
			if len(rightsubnet_tmp):
				rightsubnet_tmp = rightsubnet_tmp[0].lstrip() #remore spaces
				rightsubnet_tmp = rightsubnet_tmp.split("/") #Split string to get only ip, without subnet mask)
				descr = findDescr(rightsubnet_tmp[0],formatIkeId(conn_tmp))
                        else:
				rightsubnet_tmp.append("Not found")
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
