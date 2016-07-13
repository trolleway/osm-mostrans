#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse



def download_osm_dump():
    os.system('wget -N http://data.gis-lab.info/osm_dump/dump/latest/RU-MOW.osm.pbf')

    import json
    import pprint
    pp=pprint.PrettyPrinter(indent=2)

    refs=[]

    with open('cfg/moscow_newmodel_bus_routes_2016.json') as data_file:    
        data = json.load(data_file)

    for batches in data['dataset'].values():
        for batch in batches:
            for ref in batch['ref']:
                refs.append(ref)

    refsString=','.join(refs)
    

    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-pbf RU-MOW.osm.pbf \
  --tf accept-relations route=bus \
  --used-way --used-node \
  --write-pbf routes.osm.pbf
'''
    os.system(cmd)

    cmd='''
~/osmosis/bin/osmosis \
  -q  \
  --read-pbf routes.osm.pbf \
  --tf accept-relations ref="'''+refsString.encode("UTF-8")+'''" \
  --used-way --used-node \
  --write-pbf routes2.osm.pbf
    '''
    #print cmd
    #quit()
    os.system(cmd)

    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-pbf routes2.osm.pbf \
  --tf accept-relations "payment:troika=yes" \
  --used-way --used-node \
  --write-pbf routesFinal.osm.pbf
    '''
    os.system(cmd)

def download_osm_overpass():
    import urllib
    def makeOverpassQuery(currentmap):
        data=  {'data':  '''
[out:xml][timeout:65];(relation["route"="tram"]["payment:troika"="yes"](44,27,61,63););out meta;>;out meta qt;'''}
        print 'new '+urllib.unquote(urllib.urlencode(data)).decode('utf8')
        #return  'http://overpass.osm.rambler.ru/cgi/interpreter?'+urllib.urlencode(data)
        return  'http://overpass-api.de/api/interpreter?'+urllib.urlencode(data)
    
    #Make overpass-api query
    overpass_query=makeOverpassQuery(currentmap={})
    #print overpass_query
            
    #Do overpass query
    osmFileHandler='data.osm'

    urllib.urlretrieve(overpass_query,osmFileHandler)
    

    import json
    import pprint
    pp=pprint.PrettyPrinter(indent=2)

    refs=[]


    

    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-xml data.osm \
  --tf accept-relations route=tram \
  --used-way --used-node \
  --write-pbf routesFinal.osm.pbf
'''
    os.system(cmd)


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
    print ('Database wiped')

def importdb(host,dbname,user,password):
    os.system('''
    osm2pgsql --create --slim -E 3857 --cache-strategy sparse --cache 100 --database '''+dbname+''' --username '''+user+'''  routesFinal.osm.pbf
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
        
        import time
        now = time.strftime("%c")
        print ("Current time %s"  % now )
        
        is_download = args.download
        is_download = True
        if is_download == True:
            print "downloading"
            download_osm_overpass()

        os.system('export PGPASS='+password)

        cleardb(host,dbname,user,password)
        importdb(host,dbname,user,password)
        process(host,dbname,user,password) 
        postgis2geojson(host,dbname,user,password,'terminals_export')
        postgis2geojson(host,dbname,user,password,'routes_with_refs')

        os.system('python update_ngw_from_geojson.py  --ngw_url '+config.ngw_url+' --ngw_resource_id 94 --ngw_login '+config.ngw_login+' --ngw_password '+config.ngw_password+' --check_field road_id --filename routes_with_refs.geojson')
        os.system('python update_ngw_from_geojson.py  --ngw_url '+config.ngw_url+' --ngw_resource_id 95 --ngw_login '+config.ngw_login+' --ngw_password '+config.ngw_password+' --check_field terminal_id --filename terminals_export.geojson')
    
