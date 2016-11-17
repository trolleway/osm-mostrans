#!/bin/bash

sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update && apt-get install -y build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

cd /usr/src
sudo wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
sudo tar xzf Python-2.7.12.tgz
cd Python-2.7.12
sudo ./configure
sudo make install
cd ~

sudo apt-get install -y git imagemagick osmctools postgresql postgresql-contrib postgis default-jre
sudo apt-get install -y python-psycopg2 python-pip libpq-dev 
sudo apt-get upgrade  -y libproj-dev

sudo service postgresql restart

#Install PostGIS
sudo apt-get install -y postgis
#В полученном списке найдите пакет, подходящий для вашей версии PostgreSQL, его имя должно иметь вид postgresql-{version}-postgis-{version} и установите его:

sudo apt-get install postgis

sudo invoke-rc.d postgresql restart
sudo invoke-rc.d postgresql reload

su postgres 
psql -c "CREATE gisuser WITH PASSWORD 'localgisuserpassword';"
psql -c "ALTER ROLE gisuser WITH login;"


sudo -u postgres createdb -O gisuser --encoding=UTF8 osmot
sudo -u postgres psql -d osmot -c 'CREATE EXTENSION postgis;'

sudo -u postgres psql -d osmot -c 'ALTER TABLE geometry_columns OWNER TO gisuser;'
sudo -u postgres psql -d osmot -c 'ALTER TABLE spatial_ref_sys OWNER TO gisuser;'
sudo -u postgres psql -d osmot -c 'ALTER TABLE geography_columns OWNER TO gisuser;'

su gisuser
#После этих операций будут созданы БД PostgreSQL с установленным в ней PostGIS и пользователь БД, который станет ее владельцем, а также таблиц geometry_columns, georgaphy_columns, spatial_ref_sys.

#Убедитесь, что функции PostGIS появились в базе:

psql -h localhost -d osmot -U gisuser -c "SELECT PostGIS_Full_Version();"
sudo apt-get install osm2pgsql

# install new version of GDAL

sudo apt-get install software-properties-common python-software-properties
sudo apt-add-repository ppa:nextgis/ppa
sudo apt-get update
sudo apt-get install gdal-bin python-gdal

#check that gdal version >= 2
gdalinfo --version 

#Python won't see psycopg2, so we should use virtualenv
sudo apt-get install virtualenv

cd ~
mkdir osm-mostrans
cd osm-mostrans
git clone --recursive https://github.com/trolleway/osm-mostrans.git
virtualenv --no-site-packages env
env/bin/pip install psycopg2



#? cd osm-mostrans
#? git submodule foreach git checkout master

mv config.example.py config.py
nano config.py
#fill passwords here
#create password file for osm2pgsql here
touch ~/.pgpass

echo "127.0.0.1:5432:osmot:gisuser:localgisuserpassword" > ~/.pgpass
chmod 700 ~/.pgpass

sudo pip install -r requirements.txt

sudo nano /etc/postgresql/9.5/main/pg_hba.conf
#set local   all             all                                     peer to local   all             all                                     trust
sudo service postgresql restart


sudo -u postgres psql -d osmot -c "ALTER USER "gisuser" WITH PASSWORD 'localgisuserpassword'"
sudo -u postgres psql -d osmot -c "ALTER ROLE gisuser WITH login;"

# install new osmosis from binary

cd ~
wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
mkdir osmosis
mv osmosis-latest.tgz osmosis
cd osmosis
tar xvfz osmosis-latest.tgz
rm osmosis-latest.tgz
chmod a+x bin/osmosis
bin/osmosis

# If osmupdate or osmosis fails - add swap space, see https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-ubuntu-14-04

#tune java and osmosis
To change the amount of memory allocated to Osmosis, edit the ~/.osmosis file and set the JAVACMD_OPTIONS parameter with the memory arguments. For example, to allocate 2GB RAM to the Osmosis, process, use the following entry:

JAVACMD_OPTIONS=-Xmx2G
(This may be a good quick fix to try if you're getting "java.lang.OutOfMemoryError: Java heap space")

#install osgeo for python
