#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import psycopg2
import time
import config
import argparse

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='',
            formatter_class=PrettyFormatter)
    #parser.add_argument('--download', dest='download', action='store_true')
    #parser.add_argument('--no-download', dest='download', action='store_false')
    #parser.set_defaults(download=True)

    parser.epilog = \
        '''Samples:
%(prog)s 
''' \
        % {'prog': parser.prog}
    return parser

def render_atlas(host,dbname,user,password):
    ConnectionString="dbname=" + dbname + " user="+ user + " host=" + host + " password=" + password
    try:
        conn = psycopg2.connect(ConnectionString)
    except:
        print 'I am unable to connect to the database                  ' 
        print ConnectionString
        return 0
    cur = conn.cursor()

        
    tmpfiles=dict()
    tmpfiles['lines'] = 'tmp/lines.png'
    tmpfiles['terminals'] = 'tmp/terminals.png'

    tmpfiles['stage1'] = 'tmp/stage1.tif'
    tmpfiles['background'] = 'tmp/background.png'
    #Query for active maps
    
    cmd='''
ogr2ogr -f PostgreSQL "PG:host='''+host+''' dbname='''+dbname+''' user='''+user+''' password='''+password+'''" cfg/atlaspages.geojson -nln atlaspages -progress -overwrite    \

    '''
    print cmd
    os.system(cmd)
    cur.execute('''
SELECT CONCAT(
ST_YMin(Box2D(wkb_geometry)),',',
ST_XMin(Box2D(wkb_geometry)),',',
ST_YMax(Box2D(wkb_geometry)),',',
ST_XMax(Box2D(wkb_geometry))
) AS bbox_string,
CONCAT(
ST_XMin(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_YMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_XMax(Box2D(ST_Transform(wkb_geometry,3857))),' ',
ST_YMin(Box2D(ST_Transform(wkb_geometry,3857)))
) AS bbox_string_gdal
,
(
ST_Distance(
ST_PointN(Box2D(ST_Transform(wkb_geometry,3857)),1),
ST_PointN(Box2D(ST_Transform(wkb_geometry,3857)),2)
) 
/
ST_Distance(
ST_PointN(Box2D(ST_Transform(wkb_geometry,3857)),2),
ST_PointN(Box2D(ST_Transform(wkb_geometry,3857)),3)
) )AS aspect,
*
FROM atlaspages
WHERE map="mostrans-frequent-atlas4"
ORDER BY map,ref;
                ''')
    rows = cur.fetchall()
    for currentmap in rows:
        print currentmap#['map_id']

        continue

        
            
        #stage1 - simple png picture

        gdalcmd='gdal_translate -of "GTiff" -a_nodata 0 -co ALPHA=YES -outsize '+currentmap['size_px']+' -r lanczos -projwin  '+currentmap['bbox_string_gdal']+'   gdal_wms/wmsosmot.xml '+tmpfiles['stage1']
        print gdalcmd
        os.system( gdalcmd)      

        gdalcmd='gdal_translate -of "PNG" -outsize '+currentmap['size_px']+' -r lanczos -projwin  '+currentmap['bbox_string_gdal']+'   gdal_wms/wmsosm.xml '+tmpfiles['background']
        print gdalcmd
        os.system( gdalcmd)   
      

        import Image

        background = Image.open(tmpfiles['background'])
        overlay = Image.open(tmpfiles['stage1'])

        background = background.convert("RGBA")
        overlay = overlay.convert("RGBA")

        background.paste(overlay, (0, 0), overlay)
        #new_img = Image.blend(background, overlay, 0.5)
        background.save("stage02.png","PNG")
        
        fileDateStrinng=strftime('%Y-%m-%d %H%M%S', gmtime())
        os.rename("stage02.png",os.path.join('output',currentmap['map_id']+' MAP '+fileDateStrinng+'.png'))


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
        
        render_atlas(host,dbname,user,password)
        #import geojson to postgis in 3857
        #generate png for all pages
        #montage pages
        #overlay texts
        #convert to pdf
        #save
