#!/bin/bash
source /etc/default/rclocalvars

for IFACE in $WLAN $INET $LAN; do 
    $TC qdisc show dev $IFACE | grep -q "qdisc pfifo_fast 0"  
    [ "$?" -gt "0" ] && $TC qdisc del dev $IFACE root; sleep 1
    #$TC qdisc del root dev $IFACE
done
if [ "$1" == "limit" ]; then
    # Por defecto todo mundo cae en la categoria 10, escepto las IPs privilegiadas.
    $TC qdisc add dev $WLAN root handle 1: htb default 11
    $TC class add dev $WLAN parent 1: classid 1:10 htb rate ${DMINSPEED}kbit ceil ${DMINSPEED}kbit burst 15k prio 40
    #$TC class add dev $WLAN parent 1: classid 1:11 htb rate ${UMINSPEED}kbit ceil ${UMINSPEED}kbit burst 5k prio 40
    $TC class add dev $WLAN parent 1: classid 1:20 htb rate ${DMEDSPEED}kbit ceil ${DMEDSPEED}kbit burst 15k prio 20
    $TC class add dev $WLAN parent 1: classid 1:22 htb rate ${DMEDSPEED}kbit ceil ${DMEDSPEED}kbit burst 15k prio 22
    #$TC class add dev $WLAN parent 1: classid 1:21 htb rate ${UMEDSPEED}kbit ceil ${UMEDSPEED}kbit burst 15k prio 23
    $TC class add dev $WLAN parent 1: classid 1:30 htb rate ${DTOPSPEED}kbit ceil ${DTOPSPEED}kbit burst 15k prio 50
    #$TC class add dev $WLAN parent 1: classid 1:31 htb rate ${UTOPSPEED}kbit ceil ${UTOPSPEED}kbit burst 15k prio 50
    $TC class add dev $WLAN parent 1: classid 1:40 htb rate ${DMEDSPEED}kbit ceil ${DMEDSPEED}kbit burst 15k prio 100
    #$TC class add dev $WLAN parent 1: classid 1:41 htb rate ${UMEDSPEED}kbit ceil ${UMEDSPEED}kbit burst 15k prio 100
    $TC qdisc add dev $WLAN parent 1:40 handle 40: sfq perturb 5
    #$TC qdisc add dev $WLAN parent 1:41 handle 41: sfq perturb 5
    $TC qdisc add dev $WLAN parent 1:30 handle 30: sfq perturb 5
    #$TC qdisc add dev $WLAN parent 1:31 handle 31: sfq perturb 5
    $TC qdisc add dev $WLAN parent 1:10 handle 10: sfq perturb 5
    #$TC qdisc add dev $WLAN parent 1:11 handle 11: sfq perturb 5
    $TC qdisc add dev $WLAN parent 1:20 handle 20: sfq perturb 5
    #$TC qdisc add dev $WLAN parent 1:21 handle 21: sfq perturb 5
    FILTER="$TC filter add dev $WLAN protocol ip parent 1: prio 1 u32 match ip"

    # Apple TV
    $FILTER dst 192.168.2.111 flowid 1:40
    #$FILTER src 192.168.2.111 flowid 1:41
    # PS3
    $FILTER dst 192.168.2.110 flowid 1:20

    # Impresora
        $FILTER dst 192.168.2.21 flowid 1:30
        #$FILTER src 192.168.2.21 flowid 1:10
    # Jonny
    for i in 0 1; do 
        $FILTER dst 192.168.2.14$i flowid 1:22
        #$FILTER src 192.168.2.14$i flowid 1:11
    done
    # Marco
    for i in 1 2 3 4; do 
        $FILTER dst 192.168.2.15$i flowid 1:30
        #$FILTER src 192.168.2.15$i flowid 1:11
    done
    #Laptop de cristina
    $FILTER dst 192.168.2.169/32 flowid 1:30
    $FILTER dst 192.168.2.160/32 flowid 1:30
    #$FILTER src 192.168.2.169/32 flowid 1:11
    
    # Cristina
    for i in 1 2 3 4 5 6 7 8 9; do 
        $FILTER dst 192.168.2.16$i/32 flowid 1:10
        #$FILTER src 192.168.2.16$i/32 flowid 1:11
    done
    # Sofia
    for i in 0; do 
        $FILTER dst 192.168.2.17$i/32 flowid 1:20
        #$FILTER src 192.168.2.17$i/32 flowid 1:21
    done
    echo "TC limit..."
elif [ "x$1" == "xnotc" ]; then
    for IFACE in $WLAN $INET $LAN; do 
        $TC qdisc del root dev $IFACE
        $TC qdisc add root dev $IFACE pfifo
    done
    echo "No TC"
else
    echo "TC Fair for all"
    $TC qdisc add dev $WLAN root sfq perturb 5
fi


