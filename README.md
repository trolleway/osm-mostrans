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


#end






добавляем функции postgresql

-- Function: unnest_rel_members_ways(anyarray)

-- DROP FUNCTION unnest_rel_members_ways(anyarray);

CREATE OR REPLACE FUNCTION unnest_rel_members_ways(anyarray)
  RETURNS SETOF anyelement AS
$BODY$SELECT substring($1[i] from E'w(\\d+)') FROM
generate_series(array_lower($1,1),array_upper($1,1)) i WHERE 
$1[i] LIKE 'w%' /*only ways*/
AND /*exclude platforms*/
($1[i+1] ='' 
OR $1[i+1] IN ('forward','backward','highway')
)
;$BODY$
  LANGUAGE sql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION unnest_rel_members_ways(anyarray)
  OWNER TO postgres;
GRANT EXECUTE ON FUNCTION unnest_rel_members_ways(anyarray) TO public;
GRANT EXECUTE ON FUNCTION unnest_rel_members_ways(anyarray) TO postgres;
GRANT EXECUTE ON FUNCTION unnest_rel_members_ways(anyarray) TO "osmot users";






gdal_translate -of "GTIFF" -outsize 1000 1000  -projwin  4143247 7497160 4190083 7468902   ngw.xml test.tiff
gdal_translate -of "GTIFF" -outsize 1000 1000  -projwin  4131491 7550235 4253599 7468050   ngw.xml test.tiff
gdal_translate -of "GTIFF" -outsize 1000 1000  -projwin  4010164 7630600 4498594 7301859   wmsosmot.xml test.tiff


Скрипт берёт из базы охват, и выкачивает его по оверпасу
Дропает схему
импортирует маршруты в базу
Запускает осмот
возможно копирует в постоянную схему
генерирует картинку через веб
постит картинку



```


```
#for remote access to postgresql
sudo nano /etc/postgresql/9.3/main/postgresql.conf
#to
#listen_addresses='*'

sudo nano /etc/postgresql/9.3/main/pg_hba.conf
#and add
#
#host all all * md5


```
