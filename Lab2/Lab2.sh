#!/bin/bash
tasks=("test.py" "Task1/Task1.py" "Task2/Task2.py" "Task3/Task3.py" "Task4/Task4.py")
cur_dir=$(pwd)
	
execute_all_tasks(){ 
   for task in ${tasks[@]}; do
		if [ -x "$cur_dir/$task" ]; then
			eval $(printf "$1" "$cur_dir/$task")
		else 
			echo "File \"$task\" is not executable!"
		fi
	done 
}
	
if [ -z $1 ]; then
	echo "Usage: $0 start/stop"	
elif [ $1 = "start" ]; then
	execute_all_tasks "nohup %s >/dev/null 2>&1 &"
elif [ $1 = "stop" ]; then
	execute_all_tasks "pkill -f %s"
fi

