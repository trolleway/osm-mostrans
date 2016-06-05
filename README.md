# openroutesmap
Generator of public transport map from OSM as a service

```
git clone --recursive https://github.com/trolleway/osm-mostrans.git
osm-mostrans
git submodule foreach git checkout master




sudo apt-get install postgresql postgresql-contrib postgis

sudo service postgresql restart


#Установить PostGIS:

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

sudo apt-get install software-properties-common python-software-properties
#append nextgis ppa, when it become okay
sudo apt-get install gdal-bin python-gdal

#edit main config here


sudo apt-get install python-psycopg2
sudo apt-get install python-pip
sudo apt-get install libpq-dev
sudo pip install -r requirements.txt

sudo nano /etc/postgresql/9.3/main/pg_hba.conf
#set local   all             all                                     peer to local   all             all                                     md5
sudo service postgresql restart


sudo -u postgres psql -d osmot -c "ALTER USER "gisuser" WITH PASSWORD 'localgisuserpassword'"
sudo -u postgres psql -d osmot -c "ALTER ROLE gisuser WITH login;"


#end

```


```



```
