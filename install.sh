#!/bin/bash

#create ubuntu user gisuser 
apt-get install -y software-properties-common
add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
apt-get update && apt-get install -y build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

cd /usr/src
wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
tar xzf Python-2.7.12.tgz
cd Python-2.7.12
./configure
make install
cd /home/trolleway

apt-get install -y git imagemagick osmctools postgresql postgresql-contrib postgis default-jre python-psycopg2 python-pip libpq-dev postgis
apt-get install -y 
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
