#!/bin/sh

# Script inspired from
# https://github.com/a-schild/zabbix-ipsec.git
# to check ipsec tunnels

# ------------------------------------------
IPV4_REGEX="(([0-9][0-9]?|[0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])\.){3}([0-9][0-9]?|[0-1][0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])"
IPSECBIN="/usr/local/sbin/ipsec"
IPSECCMD=$IPSECBIN
# ------------------------------------------

# Testing availability of $IPSECBIN

if [ $# -eq 0 ];
then
   echo UNKNOWN - missing Arguments. Run check_ipsec --help
   exit $STATE_UNKNOWN
fi

test -e $IPSECBIN
if [ $? -ne 0 ]; then
    echo CRITICAL - $IPSECBIN not exist
    exit $STATE_CRITICAL
else
    STRONG=`$IPSECBIN --version |grep strongSwan | wc -l`
fi

test_tunnel() {

    CONN="$1"
    if [ "$STRONG" -eq "1" ]; then
	#check if tunel exists
	ipsec statusall | grep -e "$CONN" > /dev/null 2>&1
	#Save the retuned status code
	tmp=$?
	#If tunnel exists
	if [ $tmp -eq 0 ]; then
		ipsec statusall | grep -e "$CONN" | grep -e "rekeying" > /dev/null 2>&1
		if [ $? -eq 0 ]; then
			ipsec statusall | grep -e "$CONN" | grep -v "rekeying" | grep -E "$IPV4_REGEX" > /dev/null 2>&1

			#If tunnel is up and match IP REGEX
			if [ $? -eq 0 ]; then
                    		#echo "Tunnel $CONN look ok"
                    		return 0
                	fi
            	else
                	#echo "Tunnel $CONN not ESTABLISHED"
               		return 1
            	fi
        fi
    fi

}

test_tunnel $1
echo $?
