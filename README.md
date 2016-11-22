# openroutesmap
Generator of public transport map from OSM as a service

```
#This installation tested in fresh Ubuntu Server 16.04 LTS

git clone --recursive https://github.com/trolleway/osm-mostrans.git
cd osm-mostrans
sudo chmod 777 install.sh
sudo ./install.sh


# If osmupdate or osmosis fails - add swap space, see https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-ubuntu-14-04


#run

~/osm-mostrans/env/bin/python update_dump.py
~/osm-mostrans/env/bin/python mostrans-trolleybus.py
```


```



```
