#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse


def download_osm():
    import urllib
    urllib.urlretrieve ('''http://overpass-api.de/api/interpreter?data=[out:xml]
[timeout:120]
;
(
  relation
    ["ref"="309"]
    ["payment:troika"="yes"]
    (55.597747184319935,37.354888916015625,55.94458588614092,38.06350708007812);
  relation
    ["ref"="346"]
    ["payment:troika"="yes"]
    (55.597747184319935,37.354888916015625,55.94458588614092,38.06350708007812);

  relation
    ["ref"="361"]
    ["payment:troika"="yes"]
    (55.597747184319935,37.354888916015625,55.94458588614092,38.06350708007812);
);
out meta;
>;
out meta qt;''', "data.osm")



'''


  relation
    ["ref"="432"]
    ["payment:troika"="yes"]
    (55.597747184319935,37.354888916015625,55.94458588614092,38.06350708007812);
  relation
    ["ref"="483"]
    ["payment:troika"="yes"]
    (55.597747184319935,37.354888916015625,55.94458588614092,38.06350708007812);
  relation
    ["ref"="540"]
    ["payment:troika"="yes"]
    (55.597747184319935,37.354888916015625,55.94458588614092,38.06350708007812);
'''


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='',
            formatter_class=PrettyFormatter)
    parser.add_argument('--download', dest='download', action='store_true')
    parser.add_argument('--no-download', dest='download', action='store_false')
    parser.set_defaults(download=True)

    parser.epilog = \
        '''Samples:
%(prog)s --download
%(prog)s --no-download

''' \
        % {'prog': parser.prog}
    return parser




def cleardb(host,dbname,user,password):
    ConnectionString="dbname=" + dbname + " user="+ user + " host=" + host + " password=" + password

    try:

        conn = psycopg2.connect(ConnectionString)
    except:
        print 'I am unable to connect to the database                  ' 
        print ConnectionString
        return 0
    cur = conn.cursor()
    sql ='''
    DROP TABLE IF EXISTS planet_osm_buildings     CASCADE;
    DROP TABLE IF EXISTS planet_osm_line         CASCADE;
    DROP TABLE IF EXISTS planet_osm_nodes         CASCADE;
    DROP TABLE IF EXISTS planet_osm_point         CASCADE;
    DROP TABLE IF EXISTS planet_osm_polygon     CASCADE;
    DROP TABLE IF EXISTS planet_osm_rels         CASCADE;
    DROP TABLE IF EXISTS planet_osm_roads         CASCADE;
    DROP TABLE IF EXISTS planet_osm_ways         CASCADE;
    DROP TABLE IF EXISTS route_line_labels         CASCADE;
    DROP TABLE IF EXISTS routes_with_refs         CASCADE;
    DROP TABLE IF EXISTS terminals             CASCADE;
    DROP TABLE IF EXISTS terminals_export         CASCADE;
    '''

    cur.execute(sql)
    conn.commit()

def importdb(host,dbname,user,password):
    os.system('''
    osm2pgsql --create --slim -E 3857 --database '''+dbname+''' --username '''+user+'''  data.osm
    ''')

def process(host,dbname,user,password):
    
        cmd='''python osmot/osmot.py -hs localhost -d '''+dbname+''' -u '''+user+''' -p '''+password+'''
    '''
        print cmd
        os.system(cmd)

def postgis2geojson(host,dbname,user,password,table):
    if os.path.exists(table+'.geojson'):
        os.remove(table+'.geojson')

    cmd='''
ogr2ogr -f GeoJSON '''+table+'''.geojson  -nlt PROMOTE_TO_MULTI -nlt MULTIPOINT \
  "PG:host='''+host+''' dbname='''+dbname+''' user='''+user+''' password='''+password+'''" "'''+table+'''"
    '''
    print cmd
    os.system(cmd)




if __name__ == '__main__':


        host=config.host
        dbname=config.dbname
        user=config.user
        password=config.password

        parser = argparser_prepare()
        args = parser.parse_args()

        is_download = args.download
        is_download = True
        if is_download == True:
            print "downloading"
            download_osm()

        cleardb(host,dbname,user,password)
        importdb(host,dbname,user,password)
        process(host,dbname,user,password) 
        postgis2geojson(host,dbname,user,password,'terminals_export')
        postgis2geojson(host,dbname,user,password,'routes_with_refs')

        os.system('python update_ngw_from_geojson.py  --ngw_url '+config.ngw_url+' --ngw_resource_id 94 --ngw_login '+config.ngw_login+' --ngw_password '+config.ngw_password+' --check_field road_id --filename routes_with_refs.geojson')
        os.system('python update_ngw_from_geojson.py  --ngw_url '+config.ngw_url+' --ngw_resource_id 95 --ngw_login '+config.ngw_login+' --ngw_password '+config.ngw_password+' --check_field terminal_id --filename terminals_export.geojson')
    
