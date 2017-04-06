#!/bin/bash

# conveyor-speed=58mm/s

run_blue_stone () { 
    echo "lightbarrier1=on"
    sleep .45
    echo "lightbarrier1=off"
    sleep 1.33
    echo "color=blue"
    sleep 1.56
    echo "lightbarrier2=on"
    sleep .45
    echo "lightbarrier2=off"
    sleep .24
    echo "valve1=on"
    sleep .3
    echo "valve1=off"
}

run_red_stone () { 
    echo "lightbarrier1=on"
    sleep .45
    echo "lightbarrier1=off"
    sleep 1.33
    echo "color=red"
    sleep 1.56
    echo "lightbarrier2=on"
    sleep .45
    echo "lightbarrier2=off"
    sleep 1.42
    echo "valve2=on"
    sleep .3
    echo "valve2=off"
}

run_white_stone () {
    echo "lightbarrier1=on"
    sleep .45
    echo "lightbarrier1=off"
    sleep 1.33
    echo "color=white"
    sleep 1.56
    echo "lightbarrier2=on"
    sleep .45
    echo "lightbarrier2=off"
    sleep 2.19
    echo "valve3=on"
    sleep .3
    echo "valve3=off"
}


echo "Waiting 10 secs before we begin with the first stone..." >&2
sleep 10
echo "...and here we go..." >&2

run_blue_stone &
sleep 10
run_red_stone &
sleep 10
run_white_stone &
sleep 10

echo "done" >&2
