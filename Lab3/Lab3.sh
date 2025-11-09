#!/bin/bash
task="repeater.py"
cur_dir=$(pwd)
	
execute_task(){ 
	if [ -x "$cur_dir/$task" ]; then
		for ((port = 62000; port < 62010; port++))
		do		
			nohup $cur_dir/$task $port >/dev/null 2>&1 &
		done
	else 
		echo "File \"$task\" is not executable!"
	fi
}
	
if [ -z $1 ]; then
	echo "Usage: $0 start/stop"	
elif [ $1 = "start" ]; then
	execute_task
elif [ $1 = "stop" ]; then
	pkill -f $cur_dir/$task
fi

