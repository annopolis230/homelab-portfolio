#!/bin/bash

cd /home/minecraft
eula="/home/minecraft/eula.txt"

if [ ! -f "${eula}" ]; then
        echo "Creating eula file"
        echo 'eula=true' > "${eula}"
else
        echo "eula exists"
        grep -q 'eula=true' < "${eula}"

        if [ "${?}" -eq 0 ]; then
                echo "eula already true"
        else
                echo "setting eula to true"
                echo 'eula=true' > "${eula}"
        fi
fi

echo "Starting minecraft"
screen -L -Logfile '/home/minecraft/screen.log' -d -S minecraft -m bash -c "java -Xms5G -Xmx5G -XX:+UseG1GC -Dlog4j2.formatMsgNoLookups=true -jar server.jar"

exec tail -f /dev/null