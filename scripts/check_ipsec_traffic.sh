#!/bin/sh
#Expect conxxxxx [bytesIn,bytesOut,pktsIn,pktsOut]
# ------------------------------------------
IPSECBIN="/usr/local/sbin/ipsec"
IPSECCMD=$IPSECBIN
# ------------------------------------------

# Testing availability of $IPSECBIN

if [ $# -eq 0 ];
then
   echo UNKNOWN - missing Arguments. Run check_ipsec_traffic --help
   exit $STATE_UNKNOWN
fi

test -e $IPSECBIN
if [ $? -ne 0 ]; then
    echo CRITICAL - $IPSECBIN not exist
    exit $STATE_CRITICAL
else
    STRONG=`$IPSECBIN --version |grep strongSwan | wc -l`
fi

getTraffic() {

    CONN="$1"
    METRIC="$2"

    if [ "$STRONG" -eq "1" ]; then
	#check if tunel exists
	ipsec status | grep -e "$CONN" > /dev/null 2>&1
	#Save the retuned status code
	tmp=$?
	#If tunnel exists
	if [ $tmp -eq 0 ]; then
		ipsec status | grep -e "$CONN" | grep -e "ESTABLISHED" > /dev/null 2>&1
		if [ $? -eq 0 ]; then
			ipsec statusall | grep -e "$CONN" | grep -v "ESTABLISHED" | grep -E "$IPV4_REGEX" | grep -e "bytes" | grep -e "pkts" > /dev/null 2>&1

			#If tunnel is up and match IP REGEX
			if [ $? -eq 0 ]; then
				case $METRIC in
					bytesIn)
						bytesIn=$(ipsec statusall | grep -e "$CONN{" | grep bytes_i | awk -F" " {'print $3'} | tail -1)
						echo $bytesIn
						;;
					bytesOut)
						bytesOut=$(ipsec statusall | grep -e "$CONN{" | grep bytes_i | awk -F" " {'print $9'} | tail -1)
						echo $bytesOut
						;;
					pktsIn)
						pktsIn=$(ipsec statusall | grep -e "$CONN{" | grep bytes_i | awk -F" " {'print $5'} | sed s/\(// | tail -1) 
						echo $pktsIn
						;;
					pktsOut)
						pktsOut=$(ipsec statusall | grep -e "$CONN{" | grep bytes_i | awk -F" " {'print $11'} | sed s/\(// | tail -1) 
						echo $pktsOut
						;;
						
					*)
						echo "Undefined. Parameter $METRIC in not allowed"
						;;
				esac
                    		#echo "Tunnel $CONN look ok"
                    		return 0
			else
				echo 0
                	fi
            	else
                	#echo "Tunnel $CONN not ESTABLISHED"
			echo 0
               		return 1
            	fi
        fi
    fi

}

getTraffic $1 $2
