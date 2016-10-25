#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse

import json
import pprint

def filter_osm_dump():


    pp=pprint.PrettyPrinter(indent=2)



    with open('cfg/mostrans_night.json') as data_file:    
        data = json.load(data_file)

    refs={}
    refs['tram']=[]
    refs['trolleybus']=[]
    refs['bus']=[]
    for batches in data['dataset'].values(): 
        for batch in batches:
            for transport in batch['routes']:
                for current_reading_transport in transport:
                    print current_reading_transport
                    for ref in transport[current_reading_transport]:
                        refs[current_reading_transport].append(ref)

                
                                 


    refStrings={}
    for transport in refs:
        refStrings[transport]=','.join(refs[transport])


    print '---   bus ---'
    #we assume that we have in config buses, trolleybuses and tram routes, for simplify


    print 'Filter step 1'

    cmd='''
    ~/osmosis/bin/osmosis \
  -q  \
  --read-pbf moscow_russia.osm.pbf \
  --tf accept-relations ref="'''+refStrings['bus'].encode("UTF-8")+'''" \
  --used-way --used-node \
  --write-pbf osm/routes1.osm.pbf
'''

    print cmd
    os.system(cmd)

    print 'Filter step 2'
    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-pbf osm/routes1.osm.pbf \
  --tf accept-relations route=bus \
  --used-way --used-node \
  --write-pbf osm/routesBus.osm.pbf
    '''
    print cmd
    os.system(cmd)

    print '---   trolleybus ---'

    print 'Filter step 1'
    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-pbf moscow_russia.osm.pbf \
  --tf accept-relations route=trolleybus \
  --used-way --used-node \
  --write-pbf osm/routes.osm.pbf
'''
    print cmd
    os.system(cmd)

    print 'Filter step 2'
    cmd='''
~/osmosis/bin/osmosis \
  -q  \
  --read-pbf osm/routes.osm.pbf \
  --tf accept-relations ref="'''+refStrings['trolleybus'].encode("UTF-8")+'''" \
  --used-way --used-node \
  --write-pbf osm/routesTrolleybus.osm.pbf
    '''
    print cmd
    os.system(cmd)

    print '---   tram ---'

    print 'Filter step 1'
    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-pbf moscow_russia.osm.pbf \
  --tf accept-relations route=tram \
  --used-way --used-node \
  --write-pbf osm/routes.osm.pbf
'''
    print cmd
    os.system(cmd)

    print 'Filter step 2'
    cmd='''
~/osmosis/bin/osmosis \
  -q  \
  --read-pbf osm/routes.osm.pbf \
  --tf accept-relations ref="'''+refStrings['tram'].encode("UTF-8")+'''" \
  --used-way --used-node \
  --write-pbf osm/routesTramStep2.osm.pbf
    '''
    print cmd
    os.system(cmd)


    cmd='''
~/osmosis/bin/osmosis \
  -q \
  --read-pbf osm/routesTramStep2.osm.pbf \
  --tf accept-relations "payment:troika=yes" \
  --used-way --used-node \
  --write-pbf osm/routesTram.osm.pbf
    '''
    print cmd
    os.system(cmd)

    print 'Filter merge'
    cmd='''
~/osmosis/bin/osmosis \
  -q \
--read-pbf file=osm/routesBus.osm.pbf outPipe.0=1 \
--read-pbf file=osm/routesTrolleybus.osm.pbf outPipe.0=2 \
--read-pbf file=osm/routesTram.osm.pbf outPipe.0=3 \
--merge inPipe.0=1 inPipe.1=2 outPipe.0=4 \
--merge inPipe.0=3 inPipe.1=4 outPipe.0=5 \
--write-pbf file=osm/routesFinal.osm.pbf omitmetadata=true inPipe.0=5

    '''
    print cmd
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
    osm2pgsql --create --slim -E 3857 --cache-strategy sparse --cache 100 --database '''+dbname+''' --username '''+user+'''  osm/routesFinal.osm.pbf
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
ogr2ogr -f GeoJSON '''+table+'''.geojson    \
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

        filter_osm_dump()
        os.system('export PGPASS='+password)
        cleardb(host,dbname,user,password)
        importdb(host,dbname,user,password)
        process(host,dbname,user,password) 
        postgis2geojson(host,dbname,user,password,'terminals_export')
        postgis2geojson(host,dbname,user,password,'routes_with_refs')

        os.system('python update_ngw_from_geojson.py  --ngw_url '+config.ngw_url+' --ngw_resource_id 704 --ngw_login '+config.ngw_login+' --ngw_password '+config.ngw_password+' --check_field road_id --filename routes_with_refs.geojson')
        os.system('python update_ngw_from_geojson.py  --ngw_url '+config.ngw_url+' --ngw_resource_id 705 --ngw_login '+config.ngw_login+' --ngw_password '+config.ngw_password+' --check_field terminal_id --filename terminals_export.geojson')
        
        #quit('Удаление выключено')
        if os.path.exists('osm/routes.osm.pbf'):
            os.remove('osm/routes.osm.pbf')
        if os.path.exists('osm/routes1.osm.pbff'):
            os.remove('osm/routes1.osm.pbf')
        if os.path.exists('osm/routesBus.osm.pbf'):
            os.remove('osm/routesBus.osm.pbf')
        if os.path.exists('osm/routesFinal.osm.pbf'):
            os.remove('osm/routesFinal.osm.pbf')
        if os.path.exists('osm/routesTram.osm.pbf'):
            os.remove('osm/routesTram.osm.pbf')
        if os.path.exists('osm/routesTramStep2.osm.pbf'):
            os.remove('osm/routesTramStep2.osm.pbf')
        if os.path.exists('osm/routesTrolleybus.osm.pbf'):
            os.remove('osm/routesTrolleybus.osm.pbf')
