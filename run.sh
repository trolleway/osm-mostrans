 #!/bin/bash         

#TODO: Updatedump
#TODO: If update dump not working - run scripts with --download key 

#print  timestamp of run
timedatectl | grep Local >> cronruns.txt
cd ~/osm-mostrans
python update_dump.py
python mostrans-newbuses2016.py
python mostrans-bus.py
python mostrans-trolleybus.py
python mostrans-trolleybus-atlas.py
python mostrans-tram.py
python mostrans-tram-atlas.py
python mostrans-night.py
python mostrans-frequent.py
