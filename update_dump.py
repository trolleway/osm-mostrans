#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Update and crop osm dump file for Moscow Oblast
# Author: Artem Svetlov <artem.svetlov@nextgis.com>


'''

#if prevdump not exists - download CFO from geofabrik and crop to MosOblast
#if prevdump dump exists - run osmupdate, it updating it to last hour state with MosOblast clipping, and save as currentdump
#rename currentdump to prevdump

return 1
