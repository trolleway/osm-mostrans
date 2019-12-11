rm -r ngw
mkdir ngw

#geofabrik shp




'''
ogr2ogr -progress -nlt PROMOTE_TO_MULTI -f GeoJSON ngw/gis.osm_landuse_a_free_1.geosjon gis.osm_landuse_a_free_1.shp -lco ENCODING=UTF-8 -where "fclass IN ('residential','commercial','industrial','cemetery','retail')"

ogr2ogr -progress -nlt MULTILINESTRING -f GeoJSON ngw/gis.osm_roads_free_1.geosjon gis.osm_roads_free_1.shp -lco ENCODING=UTF-8 -where "fclass IN ('trunk','primary','secondary','tertiary','unclassifed')"

ogr2ogr -progress -nlt MULTIPOLYGON -f GeoJSON ngw/gis.osm_water_a_free_1.geojson gis.osm_water_a_free_1.shp  -where "fclass IN ('water','river','reservoir')" -lco ENCODING=UTF-8

ogr2ogr -progress -nlt MULTILINESTRING -f GeoJSON ngw/gis.osm_railways_free_1.geojson gis.osm_railways_free_1.shp  -where "fclass IN ('tram')" -lco ENCODING=UTF-8

#http://openstreetmapdata.com/data/water-polygons

ogr2ogr -progress -nlt PROMOTE_TO_MULTI -f GeoJSON ngw/simplified-water-polygons-complete-3857.geojson simplified-water-polygons-complete-3857/simplified_water_polygons.shp   -lco ENCODING=UTF-8
'''
