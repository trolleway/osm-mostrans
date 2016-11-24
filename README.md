# openroutesmap
Generator of public transport map from OSM as a service

```
#This installation tested in fresh Ubuntu Server 16.04 LTS

git clone --recursive https://github.com/trolleway/osm-mostrans.git
cd osm-mostrans
sudo chmod 777 install.sh
sudo ./install.sh

sudo nano /etc/postgresql/9.5/main/pg_hba.conf
#замените peer на md5 


# If osmupdate or osmosis fails - add swap space, 
# https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-16-04
# adding swap at digitalocean is okay for rare use, such as OSM import procedures, according to https://www.digitalocean.com/community/tutorials/how-to-set-up-an-osrm-server-on-ubuntu-14-04


sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo cp /etc/fstab /etc/fstab.bak
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab


echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf

#run

~/osm-mostrans/env/bin/python update_dump.py
~/osm-mostrans/env/bin/python mostrans-trolleybus.py
```


```



```
