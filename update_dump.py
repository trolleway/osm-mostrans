#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Update and crop osm dump file for Moscow Oblast
# Author: Artem Svetlov <artem.svetlov@nextgis.com>


'''

#if prevdump not exists - download CFO from geofabrik and crop to MosOblast
def updateDump():
    
    dump_url='http://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf'
    downloaded_dump='central-fed-district-latest.osm.pbf'
    work_dump='data.osm.pbf'
    updated_dump='just_updated_dump.osm.pbf'
    poly_file='cfg/mostrans.poly'

    #frist run of program
    if exists(work_dump) = False:
        os.system('wget '+dump_url)
        os.rename(downloaded_dump, work_dump) 

    #if prevdump dump exists - run osmupdate, it updating it to last hour state with MosOblast clipping, and save as currentdump
    os.system('osmupdate '+ work_dump + ' ' + updated_dump + '--daily --hourly -B='+poly_file)
    
    #rename currentdump to prevdump
    os.remove(work_dump)
    os.rename(updated_dump, work_dump)

return 0
