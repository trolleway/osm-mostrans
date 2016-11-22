#!/bin/bash

#create ubuntu user gisuser 
apt-get install -y software-properties-common
apt-get update && apt-get install -y  build-essential \
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
postgresql-9.5-postgis-2.2 \
software-properties-common \
python-software-properties

apt-get upgrade  -y libproj-dev

service postgresql restart

#Install PostGIS
apt-get install -y  postgis
#В полученном списке найдите пакет, подходящий для вашей версии PostgreSQL, его имя должно иметь вид postgresql-{version}-postgis-{version} и установите его:

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

#PostGIS появились в базе:

pip install --upgrade pip



# install new version of GDAL


sudo apt-add-repository -y ppa:nextgis/ppa
sudo apt-get update
sudo apt-get install -y osm2pgsql \
gdal-bin \
python-gdal

#check that gdal version >= 2
gdalinfo --version 
