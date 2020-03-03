#!/bin/bash
system=$(uname -a)
os_name=(${system// / })
if [[ ${os_name[0]} == "Linux" && ${os_name[2]} =~ "Microsoft" ]]
then
    $a export PULSE_SERVER=tcp:localhost
fi
source env/bin/activate

<<<<<<< HEAD
python3 wukong.py
=======
phddns start
>>>>>>> cdc3b8f67d0839db1ca879570415d970ebd6921f

