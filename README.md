# openroutesmap
Generator of public transport map from OSM as a service

```
#if you want use upload atlases via REST api - install latest python, eq 2.7.12.
cd ~



sudo apt-get install git imagemagick osmctools postgresql postgresql-contrib postgis 
sudo apt-get install python-psycopg2 python-pip libpq-dev

sudo service postgresql restart

#Install PostGIS
sudo apt-cache search postgis
#В полученном списке найдите пакет, подходящий для вашей версии PostgreSQL, его имя должно иметь вид postgresql-{version}-postgis-{version} и установите его:

sudo apt-get install postgresql-9.3-postgis-2.1

sudo invoke-rc.d postgresql restart
sudo invoke-rc.d postgresql reload

sudo -u postgres psql 

CREATE ROLE gisuser  password 'localgisuserpassword';
ALTER ROLE gisuser WITH login;
\q

sudo -u postgres createdb -O gisuser --encoding=UTF8 osmot
sudo -u postgres psql -d osmot -c 'CREATE EXTENSION postgis;'

sudo -u postgres psql -d osmot -c 'ALTER TABLE geometry_columns OWNER TO gisuser;'
sudo -u postgres psql -d osmot -c 'ALTER TABLE spatial_ref_sys OWNER TO gisuser;'
sudo -u postgres psql -d osmot -c 'ALTER TABLE geography_columns OWNER TO gisuser;'

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
#fill passwords



sudo pip install -r requirements.txt

sudo nano /etc/postgresql/9.5/main/pg_hba.conf
#set local   all             all                                     peer to local   all             all                                     md5
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


#end

#run

~/osm-mostrans/env/bin/python update_dump.py
~/osm-mostrans/env/bin/python mostrans-trolleybus.py
```


```



```
