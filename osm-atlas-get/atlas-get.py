
#import configuration gpkg to postgis

#pages query

for page in result:
    #prepare poly file for clip
    
    polyfile = os.path.join(datadir,'roi.poly')
    cmd = 'ogr2ogr -where "map_id={map_id}" '
    cmd = cmd.format(map_id=page['map_id'])
    print cmd
    os.system(cmd)
    
    cmd = 'ogr2poly.py {source}'
    cmd = cmd.format(source=os.path.join(datadir,'roi.gpkg')
    print cmd
    os.system(cmd)
    
    #prepare pbf file for lines
    
    #clip pbf file by poly
    cmd = 'osmconvert {sourcepbf} -B={polyfile} -o={resultpbf}'
    cmd = cmd.format(sourcepbf = os.path.join(datadir,'country.pbf'),
                     polyfile=polyfile,
                    resultpbf = os.path.join(datadir, 'city.pbf') )
    print cmd
    os.system(cmd)
    
    #filter routes from pbf
    cmd = 'python filter_pbf.py --filter "{filter}"  --source "{source_pbf}" --result "{result_pbf}" '
    cmd = cmd.format(filter = page['filter'],  source_pbf = os.path.join('datadir','city_pbf.pbf')
    print cmd
    os.system(cmd)   
    #prepare pbf file for basemap
    
    #import pbf to postgis
    cmd = 'osm2pgsql'
    
    #run osmot
    cmd = 'python osmot/osmot.py'
    
    #export route lines from postgis to gpkg
    
    cmd = 'ogr2ogr'
    cmd = 'ogr2ogr'
    
    #move lines to folder
    
    os.move
    
    #same steps for basemaps
    
    
print 'generate layers complete'
print 'merge layers to one file'
print 'merge route lines'
for in os.walk(route_lines_folder):
  
cmd = 'ogrmerge'

print 'merge basemaps'
for in os.walk(route_lines_folder):
  
cmd = 'ogrmerge'

print 'merge layers to gpkg complete'
print 'copy qgis project'
os.copy()
print 'you can open project in qgis'
