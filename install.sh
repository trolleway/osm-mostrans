#!/bin/bash

#create ubuntu user gisuser 
apt-get update  -y
apt-get upgrade -y
apt-get install -y  build-essential \
checkinstall \
libreadline-gplv2-dev \
libncursesw5-dev \
libssl-dev \
libsqlite3-dev \
tk-dev \
libgdbm-dev \
libc6-dev \
libbz2-dev \
git \
python \
imagemagick \
osmctools \
postgresql \
postgresql-contrib \
default-jre \
python-pip \
libpq-dev \
software-properties-common \
osm2pgsql

#найдите пакет postgis, подходящий для вашей версии PostgreSQL, его имя должно иметь вид postgresql-{version}-postgis-{version} и установите его:
apt-get install -y postgresql-10-postgis-2.4 

apt-get upgrade  -y libproj-dev

service postgresql restart

#Install PostGIS
apt-get install -y  postgis

invoke-rc.d postgresql restart
invoke-rc.d postgresql reload


sudo -u postgres psql -d postgres -c "CREATE ROLE gisuser WITH PASSWORD 'localgisuserpassword';"
sudo -u postgres psql -d postgres -c "ALTER ROLE gisuser WITH login;"

sudo -u postgres createdb -O gisuser --encoding=UTF8 osmot
sudo -u postgres psql -d osmot -c 'CREATE EXTENSION postgis;'

sudo -u postgres psql -d osmot -c 'ALTER TABLE geometry_columns OWNER TO gisuser;'
sudo -u postgres psql -d osmot -c 'ALTER TABLE spatial_ref_sys OWNER TO gisuser;'
sudo -u postgres psql -d osmot -c 'ALTER TABLE geography_columns OWNER TO gisuser;'


#После этих операций будут созданы БД PostgreSQL с установленным в ней PostGIS и пользователь БД, который станет ее владельцем, а также таблиц geometry_columns, georgaphy_columns, spatial_ref_sys.


pip install --upgrade pip




#sudo apt-add-repository -y ppa:nextgis/ppa
#sudo apt-get update  -y
#sudo apt-get install -y gdal-bin \
#python-gdal \
#python-psycopg2

#check that gdal version >= 2
gdalinfo --version 


service postgresql restart

#create password file for osm2pgsql 
cd ~
touch .pgpass
echo "localhost:5432:osmot:gisuser:localgisuserpassword" > .pgpass
chmod 0600 .pgpass
cd osm-mostrans


#compile osmosis
cd ~
wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
mkdir osmosis
mv osmosis-latest.tgz osmosis
cd osmosis
tar xvfz osmosis-latest.tgz
rm osmosis-latest.tgz
chmod a+x bin/osmosis

#tune java 
cd ~
touch .osmosis
echo "JAVACMD_OPTIONS=-Xmx2G" > .osmosis
chmod 666 .osmosis
cd osm-mostrans

