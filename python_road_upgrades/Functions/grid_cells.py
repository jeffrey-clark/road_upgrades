import ee
import Functions.general as f

from Imports.geometries import *
from Imports.road_collections import *
from Imports.image_collections import *


def computeCumulative(raw_list):
    '''
    Function that converts a list of numbers to the cumulative sum of the list.
    (UPDATED 2022-03-03)
    :param raw_list: list of numbers
    :return: cumulative list
    '''

    def cumulativeMap(index):
        sub_list = ee.List(raw_list).slice(0, ee.Number(index).add(1))
        sub_list_reduced = sub_list.reduce("sum")
        return sub_list_reduced
    raw_list_length = ee.List(raw_list).length()
    index_list = ee.List.sequence(0, raw_list_length.subtract(1))
    cum_list = index_list.map(cumulativeMap)
    return cum_list


def splitGeom(road_geom, new_seg_length, include_remainder=False):

    # convert the road geometry to a feature
    road_fe = f.processRoad(ee.Geometry(road_geom))

    # compute cumulative segment lengths and add as property to the element
    seg_lengths = ee.List(ee.Feature(road_fe).get("segment_lengths"))
    cum_seg_lengths = computeCumulative(seg_lengths)
    road_fe = road_fe.set("segment_lengths_cum", cum_seg_lengths)

    # compute how many new (sub)roads we are going to create from the given road
    new_road_count = ee.Number(road_fe.get("length_km")).divide(ee.Number(new_seg_length)).floor()

    # create a list of indices for the Mapping of the createSubRoad function
    new_road_index = ee.List.sequence(0, new_road_count.subtract(1))

    def createSubRoad(i):

        # get the cumulative length array
        cum_array = ee.Array(road_fe.get("segment_lengths_cum"))
        # prepend a zero to the array
        cum_array = ee.Array.cat([ee.Array([0]), cum_array])
        # take the difference from the
        start_list = cum_array.subtract(ee.Number(new_seg_length).multiply(ee.Number(i)))
        end_list = cum_array.subtract(ee.Number(new_seg_length).multiply(ee.Number(i).add(1)))

        seg_list = ee.List([0]).cat(ee.List(road_fe.get("segment_coords")))
        seg_dirs = ee.List([0]).cat(ee.List(road_fe.get("segment_directions")))

        # the start/end coordinate is the linear combination of the first positive value
        # less the absolute value of the previous negative value in the list

        def computeSignFlipSegments(a):
            a = ee.Array(a)
            # add a zero to the beginning of all used lists to enable computation of the first start point.
            a_index = ee.Number(a.lte(0).toList().reduce("sum")).subtract(1)

            a_lower_segment = ee.List(seg_list.get(a_index))
            a_lower_dir = ee.Number(seg_dirs.get(a_index))
            a_upper_segment = ee.List(seg_list.get(a_index.add(1)))
            a_upper_dir = ee.Number(seg_dirs.get(a_index.add(1)))

            # the final coordinate is getPointFromOrigin with origin being the first coordinate of a_upper_segment,
            # direction being a_upper_dir, and distance being absolute value of a.get(a_index) (the last negative value)
            o = ee.List(a_upper_segment.get(0))
            dist = ee.Number(a.toList().get(a_index)).abs()

            new_coord = f.pointFromOrigin(o, a_upper_dir, dist)

            # the Lower segment is a coordinate pair with [o, new_coord]
            # the Upper segment is a coordinate pair with [new_coord, x] where x is the second coordiate of a_upper_segment

            new_segment_lower =  ee.List([o, new_coord])
            new_segment_upper =  ee.List([new_coord, ee.List(a_upper_segment.get(1))])

            lower_line = ee.Geometry.LineString(new_segment_lower)
            upper_line = ee.Geometry.LineString(new_segment_upper)

            geom_point = ee.Geometry.Point(o)
            geom = ee.Geometry.Point(new_coord)

            # return a dictionary with the lower and upper segments
            output = ee.Dictionary({
                "lower": new_segment_lower,
                "upper": new_segment_upper,
                "a_index": a_index
            })
            return output


        s = computeSignFlipSegments(start_list)
        e = computeSignFlipSegments(end_list)

        unsplit_segs_min = ee.Number(s.get("a_index")).add(2)
        unsplit_segs_max = ee.Number(e.get("a_index")).add(2)


        unsplit_list = seg_list.slice(unsplit_segs_min, unsplit_segs_max).unzip()
        # if we no usplit segments, e.g. segment is longer than our split, then the list unsplit_segs will be empty.
        # As such we append empty val
        unsplit_list = unsplit_list.cat(ee.List([ee.List([])]))
        unsplit_segs = unsplit_list.get(0)

        s_first_upper_coord = ee.List([ee.List(s.get('upper')).get(0)])
        e_second_lower_coord = ee.List([ee.List(e.get('lower')).get(1)])

        little_road_coords = s_first_upper_coord.cat(unsplit_segs).cat(e_second_lower_coord)
        little_road = ee.Geometry.LineString(little_road_coords)
        return little_road

    split_geoms = new_road_index.map(createSubRoad)
    #split_geoms = ee.List([createSubRoad(ee.Number(new_road_index.get(0)))])
    #print(split_geoms.getInfo())

    if include_remainder:

        if split_geoms.length().getInfo() == 0:
            split_geoms = split_geoms.add(ee.Geometry(road_geom))

        else:
            full_geom = ee.Geometry(road_fe.geometry())
            full_geom_coords = full_geom.coordinates().getInfo()
            last_geom = ee.Geometry(split_geoms.get(-1))
            last_geom_coords = last_geom.coordinates().getInfo()


            # find the last (or second to last) coordinate of last geom in the full geom
            remainder_coords = None

            for q in range(1, 3):
                last_coord = last_geom_coords[-1*q]
                if last_coord in full_geom_coords:
                    index = full_geom_coords.index(last_coord)
                    if q == 1:
                        remainder_coords = full_geom_coords[index:]
                        break
                    elif q == 2:
                        index = index + 1
                        remainder_coords = [last_geom_coords[-1]] + full_geom_coords[index:]
                        break

            if remainder_coords != None:
                remainder = ee.Geometry.LineString(ee.List(remainder_coords))
                split_geoms = ee.List(split_geoms.add(remainder))

    return split_geoms




def createStripGrid(road, seg_length, strip_width, dir_level, include_remainder=True):
    road = ee.Geometry(road)
    seg_length = ee.Number(seg_length)
    dir_level = ee.String(dir_level)

    road_length = road.length().divide(1000)
    seg_count = road_length.divide(seg_length).floor()

    segments = splitGeom(road, seg_length, include_remainder=include_remainder)

    road_coords = road.coordinates()
    road_first_coord = ee.List(road_coords.get(0))
    road_last_coord = ee.List(road_coords.get(-1))


    # function to make a strip from a segment (using SEGMENT direction)
    def makeStrip_segment(seg):
        seg = ee.Geometry(seg)
        coords = seg.coordinates()
        first_coord = ee.List(coords.get(0))
        last_coord = ee.List(coords.get(-1))

        dir = f.getRoadSegmentDirection(ee.List([first_coord, last_coord]))
        dir_orthog = f.getOrthogDirections(dir)

        orthog_ccw = ee.Number(dir_orthog.get(0)) # orthog_ccw
        orthog_cw = ee.Number(dir_orthog.get(1)) # orthog_cw

        dist = ee.Number(strip_width).divide(2)

        p1 = f.pointFromOrigin(first_coord, orthog_ccw, dist)
        p2 = f.pointFromOrigin(first_coord, orthog_cw, dist)
        p3 = f.pointFromOrigin(last_coord, orthog_cw, dist)
        p4 = f.pointFromOrigin(last_coord, orthog_ccw, dist)
        p5 = f.pointFromOrigin(first_coord, orthog_ccw, dist)

        strip = ee.Geometry.Polygon([p1, p2, p3, p4, p5])
        return strip


    # function to make a strip from a segment (using ROAD direction)
    def makeStrip_road(seg):
        seg = ee.Geometry(seg)
        coords = seg.coordinates()
        first_coord = ee.List(coords.get(0))
        last_coord = ee.List(coords.get(-1))

        dir = f.getRoadSegmentDirection(ee.List([road_first_coord, road_last_coord]))
        dir_orthog = f.getOrthogDirections(dir)

        orthog_ccw = ee.Number(dir_orthog.get(0)) # orthog_ccw
        orthog_cw = ee.Number(dir_orthog.get(1)) # orthog_cw

        dist = ee.Number(strip_width).divide(2)

        p1 = f.pointFromOrigin(first_coord, orthog_ccw, dist)
        p2 = f.pointFromOrigin(first_coord, orthog_cw, dist)
        p3 = f.pointFromOrigin(last_coord, orthog_cw, dist)
        p4 = f.pointFromOrigin(last_coord, orthog_ccw, dist)
        p5 = f.pointFromOrigin(first_coord, orthog_ccw, dist)

        strip = ee.Geometry.Polygon([p1, p2, p3, p4, p5])
        return strip

    strip_dic = ee.Dictionary({
        'segment': segments.map(makeStrip_segment),
        'road': segments.map(makeStrip_road)
    })

    strips = ee.List(strip_dic.get(dir_level))
    return strips





# //***** FUNCTIONS FOR HEXAGON GRID

def pointsInRectangle(rect_geom, dist):

    rect_geom = rect_geom.bounds(1)

    # extract the coordinates
    coords = ee.List(rect_geom.coordinates().get(0))

    # compute the width and height of the rectangle
    start_coords = coords.slice(0, -1)
    end_coords = coords.slice(1)
    edges = start_coords.zip(end_coords)
    lengths = edges.map(f.distanceInKmBetweenCoordinates)
    w = ee.Number(lengths.get(0))
    h = ee.Number(lengths.get(1))

    # compute the height and width remainders, which we need to adjust with offset
    w_count = w.divide(dist).floor()
    w_remainder = w.mod(dist).divide(2)
    w_offset = w_remainder
    h_count = h.divide(dist).floor()
    h_remainder = h.mod(dist).divide(2)
    h_offset = h_remainder

    coords_tl = ee.List(coords.get(3))
    coords_bl = ee.List(coords.get(0))

    dir = f.getRoadSegmentDirection(ee.List([coords_tl, coords_bl]));
    dir_orthog = f.getOrthogDirections(dir)


    arg_list = ee.List([
        ee.Number(coords_tl.get(0)),    # lon1
        ee.Number(coords_tl.get(1)),    # lat1
        ee.Number(coords_bl.get(0)),    # lon2
        ee.Number(coords_bl.get(1)),    # lat2
        h,                              # height
        ee.Number(dir_orthog.get(0)),   # orthog_ccw
        ee.Number(dir_orthog.get(1))    # orthog_cw
    ])

    def makeColumn(d):
        def wrap(offset_index):
            offset = ee.Number(offset_index).multiply(ee.Number(d)).add(w_offset).add(ee.Number(dist).divide(2))
            p = ee.List([arg_list]).map(f.linearComboPoints(ee.Number(d).multiply(0.9), offset))
            return ee.List(p.get(0))
        return wrap


    column_indices = ee.List.sequence(0, w_count.subtract(1))
    column_lists = column_indices.map(makeColumn(dist)).flatten()
    lons = column_lists.slice(0, None, 2)
    lats = column_lists.slice(1, None, 2)
    all_points = lons.zip(lats)

    # shift every other row
    col_count = column_indices.length()
    row_count = all_points.length().divide(col_count)

    def getRow(i):
        return all_points.slice(i, None, row_count)

    odd_row_indices = ee.List.sequence(0, row_count.subtract(1), 2)
    even_row_indices = ee.List.sequence(1, row_count.subtract(1), 2)

    odd_rows = odd_row_indices.map(getRow)
    even_rows = even_row_indices.map(getRow)

    def shiftRow(row):
        def shiftPoint(point):
            return f.pointFromOrigin(ee.List(point), 90, ee.Number(dist).divide(2))
        return ee.List(row).map(shiftPoint)

    even_rows_shifted = even_rows.map(shiftRow)

    final_rows = odd_rows.zip(even_rows_shifted).flatten()
    lons = final_rows.slice(0, None, 2)
    lats = final_rows.slice(1, None, 2)
    all_points = lons.zip(lats)

    return all_points




def pointsToHexagons(points, d):

    points_to_make = ee.List.sequence(0, 6)

    def makeHexagon(origin):
        def generateCoords(index):
            dir = ee.Number(index).multiply(60)
            return f.pointFromOrigin(origin, dir, ee.Number(d).divide(2))

        coords = points_to_make.map(generateCoords)
        return ee.Geometry.Polygon(coords)

    shapes = ee.List(points).map(makeHexagon)
    return shapes



def createHexagonGrid(road_geom, buffer_radius, hex_diameter):

    # buffer the road geometry and take the bound (make into a rectangle)
    buff_geom = ee.Geometry(road_geom).buffer(ee.Number(buffer_radius).multiply(1000)).bounds(1)

    points = pointsInRectangle(buff_geom, ee.Number(hex_diameter))
    hexagons = pointsToHexagons(points, ee.Number(hex_diameter).divide(0.865))
    return hexagons



def filterGrid(grid_list, geom):

    # convert the list of polygons to a list of features
    grid_list = f.polygonCoordListToFeatureList(grid_list)

    # set a property dummy if intersects with the masking geom

    def applyFilter(fe):
        fe = ee.Feature(fe)
        fe_geom = ee.Feature(fe).geometry()
        result_list = ee.List([ee.Geometry(geom).intersects(fe_geom)])
        i_dummy = result_list.filter(ee.Filter.eq("item", True)).length()
        fe = fe.set("i", i_dummy)
        return fe

    grid_list = grid_list.map(applyFilter)
    grid_list = grid_list.filter(ee.Filter.eq("i", 1))


    def getGeoms(fe):
        return ee.Feature(fe).geometry()

    grid_list = grid_list.map(getGeoms)
    return grid_list;




def analyzeGrid(grid_list, year_list, start_mm_dd, end_mm_dd):

    grid_list = ee.List(grid_list)
    #year_list_str = ee.List([str(x) for x in year_list])
    #year_list = ee.List(year_list)
    year_list_str = [str(x) for x in year_list]


    ## ADD GRID IDENTIFIERS

    def extractFirstGeomLat(geom):
        geom = ee.Geometry(geom)
        coords = ee.List(geom.coordinates().get(0))
        first_coord = ee.List(coords.get(0))
        first_lat = ee.Number(first_coord.get(1))
        return first_lat

    def countInList(list):
        def wrap(val):
            count = ee.List(list).filter(ee.Filter.eq("item", ee.Number(val))).length()
            return count
        return wrap

    first_lat_list = grid_list.map(extractFirstGeomLat)
    distinct_lats = first_lat_list.distinct()

    row_count = distinct_lats.length()
    cols_per_row = distinct_lats.map(countInList(first_lat_list))

    # convert the list of polygons to a list of features
    grid_list = f.polygonCoordListToFeatureList(grid_list)


    # add row and col identifiers to the grid
    def addGridIdentifiers(fe_list, dim_list):

        fe_list = ee.List(fe_list)
        dim_list = ee.List(dim_list)
        row_index_list = ee.List.sequence(0, dim_list.length().subtract(1))

        def makeTuple(row_id):
            col_count_in_row = ee.Number(dim_list.get(ee.Number(row_id)))
            col_ids =  ee.List.sequence(0, col_count_in_row.subtract(1))
            row_ids = ee.List.repeat(ee.Number(row_id), col_count_in_row)
            tups = row_ids.zip(col_ids)
            return tups

        id_tuples = row_index_list.map(makeTuple).flatten()
        x = id_tuples.slice(0, None, 2)
        y = id_tuples.slice(1, None, 2)
        cell_id_tuples = x.zip(y)

        cell_index_list = ee.List.sequence(0, fe_list.length().subtract(1))

        def identifyCell(cell_id):
            cell_id = ee.Number(cell_id)
            fe = ee.Feature(fe_list.get(cell_id))
            tup = ee.List(cell_id_tuples.get(cell_id))
            row_id = ee.Number(tup.get(0))
            col_id = ee.Number(tup.get(1))
            fe = fe.set('id_row', row_id, 'id_col', col_id)
            return fe

        updated_fe_list = cell_index_list.map(identifyCell)
        return updated_fe_list

    grid_list = addGridIdentifiers(grid_list, cols_per_row)


    ## STORE THE GRID MIDPOINT

    def getGeomCentroid(fe):
        fe = ee.Feature(fe)
        geom = fe.geometry()
        center_point = geom.centroid(1).coordinates()
        area = ee.Number(geom.area(1).divide(1000000))
        fe = fe.set("midpoint", center_point, "area", area)

        # also let us compute the width of the grid cell
        # if the road is going from left to right, we know that the coordinates in the grid come in the order
        # [TL, BL, BR, TR, TL] where T= Top, B= Bottom, L= Left, R= Right
        # thus to get the grid distance, we need to compute the distance between points BL and BR or TR and TL
        coords = ee.List(ee.List(geom.coordinates()).get(0))
        height = ee.Number(ee.Geometry.LineString(coords.slice(0, 2)).length()).divide(1000)
        width = area.divide(height)
        fe = fe.set("width", width, "height", height)
        return fe

    grid_list = grid_list.map(getGeomCentroid)


    # NDVI ANALYSIS FOR YEARS IN YEAR_LIST

    def getNDVI(fe, year, year_str):
        fe = ee.Feature(fe)
        t1 = ee.String(year_str).cat(ee.String(f"-{start_mm_dd}"))
        t2 = ee.String(year_str).cat(ee.String(f"-{end_mm_dd}"))
        poly = fe.geometry()
        img = ee.Image(MODIS.filterDate(t1, t2).filterBounds(poly).median())
        ndvi_mean = ee.Number(ee.Feature(f.addBandValueToFeature(ee.Feature(fe), img, ee.List(["NDVI"]), 0)).get("NDVI_mean")).multiply(0.0001)
        return ndvi_mean

    def mapNDVI(year_list, year_list_str):
        def wrap(fe):
            def exec(year_duo):
                year_duo = ee.List(year_duo)
                year = ee.Number(year_duo.get(0))
                year_str = ee.String(year_duo.get(1))

                output = getNDVI(ee.Feature(fe), year, year_str)
                return ee.List([ee.String("NDVI_").cat(year_str), output])

            year_list_comb = year_list.zip(year_list_str)
            arg_list = year_list_comb.map(exec).flatten()
            return ee.Feature(fe).set(arg_list)
        return wrap

    grid_list = ee.List(grid_list).map(mapNDVI(ee.List(year_list), ee.List(year_list_str)))
    # take one year at a time, Mapping many years cause server computation overload
    # for i in range(0, len(year_list)):
    #     temp_list = ee.List(year_list[i:i+1])
    #     print(f"    - GETTING NDVI FOR YEAR:{year_list[i]}")
    #     temp_list_str = ee.List(year_list_str[i:i + 1])
    #     grid_list = ee.List(grid_list).map(mapNDVI(temp_list, temp_list_str))

    ## FACEBOOK POPULATION MEASUREMENT

    def getFacebookPop(fe):
        fe = ee.Feature(fe)
        geom = fe.geometry()
        pop = ee.Number(fb_pop.select("b1").reduceRegion(ee.Reducer.sum(), geom, 10).get("b1"))
        fe = fe.set("population", pop)
        return fe

    grid_list = grid_list.map(getFacebookPop)


    ## RAINFALL DATA

    def getRainfall(fe, year, year_str):
        fe = ee.Feature(fe)
        t1 = ee.String(year_str).cat(ee.String(f"-{start_mm_dd}"))
        t2 = ee.String(year_str).cat(ee.String(f"-{end_mm_dd}"))
        poly = fe.geometry()
        img = ee.Image(rainfall.filterDate(t1, t2).filterBounds(poly).median())

        rain_mean = ee.Number(ee.Feature(
            f.addBandValueToFeature(ee.Feature(fe), img, ee.List(["total_precipitation"]), 0)
        ).get('total_precipitation_mean')
        )

        return rain_mean

    def mapRainfall(year_list, year_list_str):
        def wrap(fe):
            def exec(year_duo):
                year_duo = ee.List(year_duo)
                year = ee.Number(year_duo.get(0))
                year_str = ee.String(year_duo.get(1))

                output = getRainfall(ee.Feature(fe), year, year_str)
                return ee.List([ee.String("rainfall_").cat(year_str), output])

            year_list_comb = year_list.zip(year_list_str)
            arg_list = year_list_comb.map(exec).flatten()
            return ee.Feature(fe).set(arg_list)
        return wrap

    grid_list = ee.List(grid_list).map(mapRainfall(ee.List(year_list), ee.List(year_list_str)))

    return grid_list



## Compute nearest distances to point in a feature collection e.g. commercial

def computeNearestDistances(grid_list, att_name, fc):

    grid_list = ee.List(grid_list)
    fc = ee.FeatureCollection(fc)

    def featureCollectionToCoordList(fc):
        fc = ee.FeatureCollection(fc)
        fe_list = fc.toList(ee.Number(fc.size()))
        def getPointFromFE(fe):
            return ee.Feature(fe).geometry().coordinates()
        return fe_list.map(getPointFromFE)


    def distanceToClosestCoord(coord_list_local):
        def wrap(grid):
            coord_list = ee.List(coord_list_local)
            origin = ee.List(ee.Feature(grid).get("midpoint"))
            origin_list = ee.List.repeat(origin, coord_list.length())

            vector_list = origin_list.zip(coord_list)
            distance_list = vector_list.map(f.distanceInKmBetweenCoordinates)
            min_distance = distance_list.reduce("min")

            grid = ee.Feature(grid)
            return grid.set(ee.String(att_name), min_distance)
        return wrap


    coord_list = featureCollectionToCoordList(fc)
    updated_grid_list = grid_list.map(distanceToClosestCoord(coord_list))
    return updated_grid_list




if __name__ == "__main__":
    pass