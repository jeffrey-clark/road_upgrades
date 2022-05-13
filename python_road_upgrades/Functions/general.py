import ee
import math
import collections
collections.Callable = collections.abc.Callable
ee.Initialize()

from Imports.image_collections import *
#rom Imports.geometries import *
#from Imports.road_collections import *


# make sure that the entire region has composite image
def verifyComposite(img, region):
    '''
    Ensure that fetched composite image has raster data for entire region/geom
    (UPDATED: 2022-02-16)
    :param img: composite image (EE.Image)
    :param region: geometry (EE.Geometry.LineString)
    :return: success dummy 1 = success, 0 = fail , (ee.Number)
    '''
    img = ee.Image(img)
    region = ee.Geometry(region)

    points = coordListToFeatureList(ee.List(region.coordinates()))

    # map the band value analysis and set propoerty
    def applyBandValueExtraction(fe):
        return addBandValueToFeature(ee.Feature(fe), img, ["B8"], 10)

    points = points.map(applyBandValueExtraction)

    def getPropertyLengths(fe):
        return ee.Number(ee.Feature(fe).propertyNames().length().min(1))

    property_lengths = points.map(getPropertyLengths)

    # get the minimum property length
    verify_dummy = ee.Number(property_lengths.reduce("min"))

    return verify_dummy


def fetchS2Composite(from_date, to_date, region):
    '''
    Fetches composite images from the Sentinel 2 Image Collection  (composite of 25% images lowest cloud pixel)
    (UPDATED: 2022-02-16)
    :param from_date: (string with format "yyyy-mm-dd")
    :param to_date: (string with format "yyyy-mm-dd")
    :param region: ee.Geometry object
    :return: ee.Image object (composite)
    '''

    image_col = s2.filterDate(from_date, to_date).filterBounds(region).sort("CLOUDY_PIXEL_PERCENTAGE")

    #  compute the number of images under 5% cloudy pixel
    image_col_list = image_col.toList(ee.Number(image_col.size()))

    def get_cloudy(img):
        return ee.Number(ee.Image(img).get('CLOUDY_PIXEL_PERCENTAGE'))

    cloudy_list = image_col_list.map(get_cloudy)

    def get_cloud_dummy(max_score):
        def wrap(cloudy_score):
            max_pct = ee.Number(max_score).divide(100)
            cloudy_pct = ee.Number(cloudy_score).divide(100)
            # dummy should be between 0 and 1
            dummy = max_pct.subtract(cloudy_pct).add(0.0001).ceil()
            return dummy
        return wrap

    dummy_list = cloudy_list.map(get_cloud_dummy(10))  # ARGUMENT HERE IS THE MAX CLOUDY PERCETAGE
    img_count_lt_5pct = ee.Number(dummy_list.reduce('sum'))
    img_id_lt5 = img_count_lt_5pct.subtract(1)

    # if the image count lt 5 percent is = 0, we should take the composite of
    # first declie instead. To determine this we filter the following FC

    methods = ee.FeatureCollection([
        ee.Feature(None, {'type': '5pct', 'count': img_count_lt_5pct}),
        ee.Feature(None, {'type': 'distribution', 'count': 0.1})  # HERE IS THE BOTTOM SHARE IF NO UNDER THRESH
    ])

    method = ee.String(methods.sort("count", False).first().get('type'))

    img_id_options = ee.Dictionary({
        '5pct': img_count_lt_5pct,
        'distribution': ee.Number(image_col.size().divide(100).ceil()),
    })

    # get the img_id of the lower
    img_id = img_id_options.get(method)

    # subset the image collection with the best img_id
    subset_list = image_col.toList(img_id)
    subset_col = ee.ImageCollection(subset_list)

    composite = subset_col.median()

    verifyComposite(composite, region)

    return ee.Image(composite)


def coordListToFeatureList(coord_list):
    '''
    Convert a list of coordinates to a list of features
    (UPDATED: 2022-01-31)
    :param coord_list: list of coordinates (e.g. [[39.21933215491994, -16.743763928051344],[39.218520598528215, -16.743665827828163]])
    :return: list of features
    '''
    def x(coord):
        geom = ee.Geometry.Point(coord)
        return ee.Feature(geom)

    return ee.List(coord_list).map(lambda coord: x(coord))


def polygonCoordListToFeatureList(poly_list):
    def x(poly):
        fe = ee.Feature(ee.Geometry(poly), {})
        return fe
    return ee.List(poly_list).map(x)


def addBandValueToFeature(feature, image, band_list, buffer):
    '''
    Adds the band value as a property to a road point (feature)
    (UPDATED: 2022-02-10)
    :param feature: The road of interest as feature element
    :param image: the composite image from which we will take band values
    :param band_list: list of bands that we want to store e.g. ['b4', 'b8']
    :return: feature with updated properties showing band value (extra information)
    '''
    # a bit unsure about how to deal with resolution set it at 10 for now
    resolution = 10


    # here we set the buffer for value extraction purpose is to control for small shifts in composite rasters
    feature_buffered = ee.Feature(feature).buffer(10, 1)
    geom = ee.Geometry(feature_buffered.geometry())

    # get the band value
    def getBandValue(band):
        # take the max value in the point buffer
        min = image.select(ee.String(band)).reduceRegion(ee.Reducer.min(), geom, resolution).get(ee.String(band))
        max = image.select(ee.String(band)).reduceRegion(ee.Reducer.max(), geom, resolution).get(ee.String(band))
        mean = image.select(ee.String(band)).reduceRegion(ee.Reducer.mean(), geom, resolution).get(ee.String(band))
        output_list = ee.List([min, max, mean])
        return output_list


    def suffixSplit(band_name):
        # make sure that we add one suffix for each var in output list in the getBandValue function above
        min = ee.String(band_name).cat("_min")
        max = ee.String(band_name).cat("_max")
        mean = ee.String(band_name).cat("_mean")
        return ee.List([min, max, mean])

    band_values = ee.List(ee.List(band_list).map(getBandValue)).flatten()
    band_names = ee.List(ee.List(band_list).map(suffixSplit)).flatten()

    return feature.set(ee.Dictionary.fromLists(band_names, band_values))



def featureListToGeom(feature_list):
    '''
    converts a list of features to a single geometry
    (UPDATED: 2022-01-31)
    :param feature_list: list of features (e.g. road points)
    :return: ee.Geometry
    '''
    # create a feature collection
    fc = ee.FeatureCollection(feature_list)
    return fc.geometry()

#def get_

'''
Here comes unit conversions between: 
    - Degrees
    - Radians
    - Compass
'''

def degreesToRadians(degrees):
    '''
    returns the radians of inputted degrees
    (UPDATED: 2022-01-31)
    :param degrees: ee.Number
    :return: ee.Number
    '''
    return ee.Number(degrees.multiply(math.pi / 180))


def radiansToDegrees(radians):
    '''
    returns the degrees of inputted radians
    (UPDATED: 2022-01-31)
    :param radians: ee.Number
    :return: ee.Number
    '''
    return ee.Number(ee.Number(radians).divide(math.pi / 180))


def degreesToCompass(degrees):
    '''
    returns the compass bearing of inputted degrees
    (UPDATED: 2022-01-31)
    :param degrees: ee.Number
    :return: ee.Number
    '''
    options = ee.List([ee.Number(90).subtract(degrees), ee.Number(90).subtract(degrees).subtract(360)])
    output = options.filter(ee.Filter.rangeContains('item', -180, 180)).get(0)
    return ee.Number(output)


def compassToDegrees(compass):
    '''
    returns the degrees of inputted compass bearing
    (UPDATED: 2022-01-31)
    :param compass: ee.Number
    :return: ee.Number
    '''
    # apparently the function degreesToCompass will inverse itself. So it goes both ways
    return ee.Number(degreesToCompass(compass))


def radiansToCompass(radians):
    '''
    returns the compass bearing of inputted radians
    (UPDATED: 2022-01-31)
    :param radians: ee.Number
    :return: ee.Number
    '''
    # convert radians to degrees
    degrees = radiansToDegrees(radians)
    return ee.Number(degreesToCompass(degrees))


def compassToRadians(compass):
    '''
    returns the radians of inputted compass bearing
    (UPDATED: 2022-01-31)
    :param compass: ee.Number
    :return: ee.Number
    '''
    degrees = compassToDegrees(compass)
    return ee.Number(degreesToRadians(degrees))


def getOrthogDirections(direction):
    '''
    Compute the two orthogonal directions to the inputted direction
    (UPDATED: 2022-01-31)
    :param direction: ee.Number
    :return:list of orthogonal directions [CCW, CW]
    '''
    # convert compass to radians
    rad = ee.Number(compassToRadians(direction))
    orthog_rads = ee.List([rad.add(math.pi/2), rad.subtract(math.pi/2)])
    orthod_dir = orthog_rads.map(radiansToCompass)
    return orthod_dir


def getOppositeDirection(direction):
    '''
    Compute the opposite direction of inputted direction
    (UPDATED: 2022-01-31)
    :param direction: ee.Number
    :return: ee.Number
    '''
    options = ee.List([ee.Number(direction).add(180), ee.Number(direction).subtract(180)])
    output = options.filter(ee.Filter.rangeContains('item', -180, 180)).get(0)
    return ee.Number(output)



def distanceInKmBetweenCoordinates(coord_pairs):
    '''
    Compute the distance, in km, between a pair of coordinates
    (UPDATED: 2022-01-31)
    :param coord_pairs: pair of coordinates e.g [[lon1, lat1], [lon2, lat2]]
    :return: distance in km (ee.Number)
    '''
    # coord_1 = ee.List(coord_pairs).get(0)
    # coord_2 = ee.List(coord_pairs).get(1)
    line = ee.Geometry.LineString(ee.List(coord_pairs))
    length = line.length().divide(1000)
    return length



def distanceInKmBetweenCoordinates_OLD(coord_pairs):
    '''
    Compute the distance, in km, between a pair of coordinates
    (UPDATED: 2022-01-31)
    :param coord_pairs: pair of coordinates e.g [[lon1, lat1], [lon2, lat2]]
    :return: distance in km (ee.Number)
    '''
    coord_1 = ee.List(coord_pairs).get(0)
    coord_2 = ee.List(coord_pairs).get(1)

    lat1 = ee.Number(ee.List(coord_1).get(1))
    lon1 = ee.Number(ee.List(coord_1).get(0))
    lat2 = ee.Number(ee.List(coord_2).get(1))
    lon2 = ee.Number(ee.List(coord_2).get(0))

    earthRadiusKm = 6371

    dLat = degreesToRadians(lat2.subtract(lat1))
    dLon = degreesToRadians(lon2.subtract(lon1))

    lat1 = degreesToRadians(lat1)
    lat2 = degreesToRadians(lat2)

    a1 = dLat.divide(2).sin().pow(2)
    a2 = dLon.divide(2).sin().pow(2).multiply(lat1.cos()).multiply(lat2.cos())
    a = a1.add(a2)
    c = a.multiply(-1).add(1).sqrt().atan2(a.sqrt()).multiply(2)

    return c.multiply(earthRadiusKm)



def pointFromOrigin(origin_coords, direction, distance):
    '''
    Computes the coordinates of a point x km in theta direction from the origin coordinates
    (UPDATED: 2022-01-31)
    :param origin_coords: coordinates (ee.list)
    :param direction: direction to new coordinates [-180, 180]
    :param distance: distance to new coordinates (km)
    :return: coordinates of the new point (ee.List)
    '''

    lon1 = ee.Number(ee.List(origin_coords).get(0))
    lat1 = ee.Number(ee.List(origin_coords).get(1))

    # remember that direction and distance is orthogonal
    # take absolute value of direction
    abs_dir = ee.Number(direction).abs()

    # get a dummy to indicate if the abs_dir is obtuse i.e. > 90
    obtuse = abs_dir.subtract(90).max(0).divide(abs_dir.subtract(90))  # acute == 0, obtuse == 1

    # get a dummy for if direction is positive
    positive = ee.Number(direction).max(0).divide(ee.Number(direction))
    negative = ee.Number(1).subtract(positive)

    # theta for type 1 and 2
    theta_degrees = obtuse.multiply(180).add(abs_dir).subtract(obtuse.multiply(2).multiply(abs_dir))
    theta = ee.Number(degreesToRadians(theta_degrees))

    # dLon and dLat in meters  (apparently .subtract(... is not needed)
    dLon_km = ee.Number(distance).multiply(theta.sin()).multiply(ee.Number(1).subtract(ee.Number(2).multiply(negative)))
    dLat_km = ee.Number(distance).multiply(theta.cos()).multiply(ee.Number(1).subtract(ee.Number(2).multiply(obtuse)))

    earth_radius_km = ee.Number(6371)

    lonX = lon1.add(dLon_km.divide(earth_radius_km).multiply(180/math.pi))#.divide(lat1.multiply(180/math.pi).cos()))
    latX = lat1.add(dLat_km.divide(earth_radius_km).multiply(180/math.pi))

    return ee.List([lonX, latX])



def linearComboPoints(offset):
    '''
    Function with wrap (for Mapping) that returns linear combination points every 20 meters on line segment.
    The wrapping allows for offset (which is needed for parallel lines to control for noise.
    :param offset: distance (km) (positive or negative) that we want to offset points from road
    :return: output from the wrap function ee.List
    '''

    def wrap(combined_list):
        '''

        :param combined_list:  combined list with start and end coordinates of line segment,
        and with the length (km) of the segment
        :return:  list of coordinates for n points, equally spaced along the segment where the distance between the
        points is approximately 20m. If the road is less than 20m, the midpoint will receive one point.
        '''

        # write a function to return linear combinations
        lon1 = ee.Number(ee.List(combined_list).get(0))
        lat1 = ee.Number(ee.List(combined_list).get(1))
        lon2 = ee.Number(ee.List(combined_list).get(2))
        lat2 = ee.Number(ee.List(combined_list).get(3))
        length = ee.Number(ee.List(combined_list).get(4))
        orthog_ccw = ee.Number(ee.List(combined_list).get(5))
        orthog_cw = ee.Number(ee.List(combined_list).get(6))

        # implement the necessary offset
        coord1 = pointFromOrigin(ee.List([lon1, lat1]), orthog_ccw, offset)
        lon1 = ee.Number(coord1.get(0))
        lat1 = ee.Number(coord1.get(1))
        coord2 = pointFromOrigin(ee.List([lon2, lat2]), orthog_ccw, offset)
        lon2 = ee.Number(coord2.get(0))
        lat2 = ee.Number(coord2.get(1))


        #do the floor computation at 20 m
        points_to_add = length.divide(0.02).floor().max(1)

        dLat = lat2.subtract(lat1)
        dLon = lon2.subtract(lon1)

        stepLat = dLat.divide(points_to_add.add(1))
        stepLon = dLon.divide(points_to_add.add(1))

        steps = ee.List.sequence(1, points_to_add)

        def createLinCombo(step):
          lonX = lon1.add(stepLon.multiply(step))
          latX = lat1.add(stepLat.multiply(step))
          return ee.List([lonX, latX])


        # .map() på alla element i coordinates listan
        points = steps.map(createLinCombo)

        return points

    return wrap



def getRoadSegmentDirection(coord_list):
    '''
    Computes the direction of a road segment as compass bearing (-180, 180)
    :param coord_list: list of segment start and end coordinates [[lon1, lat1], [lon2, lat2]]
    :return: direction (compass bearing (-180,180)) of line segment (ee.Number)
    '''

    # extract the first coordinate
    coord1 = ee.List(ee.List(coord_list).get(0))
    lat1 = ee.Number(coord1.get(1))
    lon1 = ee.Number(coord1.get(0))

    # make a straight line north from the first coordinate
    # latN = lat1.add(0.002)
    # lonN = lon1
    # north_line_second_coord = ee.List([lonN, latN])
    # coordN = ee.List([coord1, north_line_second_coord])

    # create the north line geometry
    # geomN = ee.Geometry.LineString(coordN)

    # extract the second coordinate
    coord2 = ee.List(ee.List(coord_list).get(1))
    lat2 = ee.Number(coord2.get(1))
    lon2 = ee.Number(coord2.get(0))

    # compute the difference between coordinates of line segment
    dLat = lat2.subtract(lat1)
    dLon = lon2.subtract(lon1)

    # compute the angle (unit circle)
    angle = dLon.atan2(dLat)

    # convert the angle to compass-like degree with N = 0, S = 180/-180, E = 90, W = -90
    angle_compass = radiansToCompass(angle)

    return angle_compass



def processRoad(road_geom):

    # store all road breakpoints ina coordinate list
    coord_list = ee.Geometry(road_geom).coordinates()
    # remove the last coordinate, to get list of from_coordinates
    from_coords = coord_list.slice(0,-1)
    # remove the first coordinate to get a list of to_coordinates
    to_coords = coord_list.slice(1)

    # zip the from and too coordinates to compute distance of segment
    coord_pairs = from_coords.zip(to_coords)  # to and from coordinate pairs
    segment_lengths = coord_pairs.map(distanceInKmBetweenCoordinates)

    # store the segment directions
    segment_directions = coord_pairs.map(getRoadSegmentDirection)

    # store the orthogonal directions
    orthogonal_directions = segment_directions.map(getOrthogDirections)

    # local function to extract the first orthogonal (CCW) and second orthogonal (CW) directions
    # note when mapping a function and including argument we need to wrap a function
    # see here: https://gis.stackexchange.com/questions/302760/gee-imagecollection-map-with-multiple-input-function
    def getNFromList(n):
        def wrap(l):
            output = ee.List(l).get(n)
            return ee.Number(output)
        return wrap

    orthog_ccw = orthogonal_directions.map(getNFromList(0))
    orthog_cw = orthogonal_directions.map(getNFromList(1))


    zipped_segments = coord_pairs.zip(segment_lengths)
    # zip flatten zip flatten zip flatten
    def flatten_func(list):
        return ee.List(list).flatten()

    zipped_segments = zipped_segments.zip(orthog_ccw).zip(orthog_cw).map(flatten_func)

    # print("zipped segments are", zipped_segments)

    def generatePointSet(zipped_segments, offset):
        lcp_flat = zipped_segments.map(linearComboPoints(offset)).flatten()
        lons = lcp_flat.slice(0, None, 2)
        lats = lcp_flat.slice(1, None, 2)
        coord_list = lons.zip(lats)
        # convert the list of coordinates to a list of features
        return coordListToFeatureList(coord_list)

    # now map the linear combo function to get all points from all segments
    points = generatePointSet(zipped_segments, 0)

    left_25 = generatePointSet(zipped_segments, 0.025)
    left_50 = generatePointSet(zipped_segments, 0.05)
    left_75 = generatePointSet(zipped_segments, 0.075)

    right_25 = generatePointSet(zipped_segments, -0.025)
    right_50 = generatePointSet(zipped_segments, -0.05)
    right_75 = generatePointSet(zipped_segments, -0.075)

    control_points = ee.Dictionary(
        {"left_25": left_25, "left_50": left_50, "left_75": left_75,
            "right_25": right_25, "right_50": right_50, "right_75": right_75}
     )

    return ee.Feature(road_geom,
    {
        # 'from_coords': from_coords,
        # 'to_coords': to_coords,
        'segment_coords': coord_pairs,
        'segment_lengths': segment_lengths,
        'segment_directions': segment_directions,
        'segment_orth_directions': orthogonal_directions,
        'length_km': segment_lengths.reduce('sum'),
        'points': points,
        'points_control': control_points
    })


def analyzeBandsInDiff(road_feature, band_list, date_interval1, date_interval2):
    '''
    analyzes the diff image composite on specified bands and updates feature properties of each point on the road
    Note: function processRoad should be run before this!
    (UPDATED: 2022-02-16)
    :param road_feature: road object ee.Feature
    :param band_list: list e.g. ["B4", "B8"]
    :param date_interval1: list with string start date interval e.g. ["2017-06-01", "2017-08-01"]
    :param date_interval2: list with string end date interval e.g. ["2021-06-01", "2021-08-01"]
    :return: updated road feature with band values as properties on points
    '''

    #generate the images that we need for the road
    d1_from = date_interval1[0]
    d1_to = date_interval1[1]
    t1 = fetchS2Composite(d1_from, d1_to, road_feature.geometry())

    d2_from = date_interval2[0]
    d2_to = date_interval2[1]
    t2 = fetchS2Composite(d2_from, d2_to, road_feature.geometry())

    diff = t1.subtract(t2)

    # extract the point for band value analysis
    points = ee.List(road_feature.get("points"))

    # CODE FOR BRIGHTNESS FACTOR ADJUSTMENT
    # CORRECTED THE DIFF FACTOR BELOW
    def getDiffFactor(band_name):
        road_geom = ee.Feature(road_feature).geometry()
        buffer_geom = road_geom.buffer(2000)
        median_t1 = ee.Number(t1.select(ee.String(band_name)).reduceRegion(ee.Reducer.median(), buffer_geom, 10).get(
            ee.String(band_name)))
        median_t2 = ee.Number(t2.select(ee.String(band_name)).reduceRegion(ee.Reducer.median(), buffer_geom, 10).get(
            ee.String(band_name)))
        diff_factor = median_t1.subtract(median_t2)
        return diff_factor
        # old code (problematic to take diff of
        #return ee.Number(diff.select(ee.String(band_name)).reduceRegion(ee.Reducer.median(), buffer_geom, 10).get(ee.String(band_name)))


    diff_factor_list = ee.List(band_list).map(getDiffFactor)
    diff_factors = ee.Dictionary.fromLists(ee.List(band_list), diff_factor_list )


    def getPropertyValue(feature_element):
        def wrap(prop_name):
            return ee.Number(ee.Feature(feature_element).get(ee.String(prop_name)))
        return wrap

    def getPropBands(property_name):
        bands = ee.List(band_list)
        prop_name = ee.String(property_name)

        def getIndex(string):
            def wrap(substring):
                index = ee.Number(ee.String(string).index(ee.String(substring))).min(0)
                return ee.Feature(None, {"band": ee.String(substring), "index": index})
            return wrap

        index_list = bands.map(getIndex(prop_name))
        f = ee.Feature(index_list.filter(ee.Filter.eq("index", 0)).get(0))
        band = ee.Number(f.get('band'))

        return band


    def getStoredDiffFactor(band_key):
        return ee.Number(diff_factors.get(ee.String(band_key)))

    # OLD NORMALIZING FUNCTION
    def normalizeDiffProperties(feature_element):
        # get list of all properties
        fe = ee.Feature(feature_element)
        prop_names = fe.propertyNames()
        prop_values = ee.Array(prop_names.map(getPropertyValue(fe)))
        prop_bands = prop_names.map(getPropBands)
        diff_factors = ee.Array(prop_bands.map(getStoredDiffFactor))
        prop_values_new = prop_values.subtract(diff_factors).toList()

        to_set = ee.Dictionary.fromLists(prop_names, prop_values_new)

        fe = fe.set(to_set)
        return fe


    # OLD METHOD OF MAX IN DIFF

    # # map the band value analysis and set property
    # def applyBandValueExtraction(feature_element):
    #     fe = addBandValueToFeature(ee.Feature(feature_element), diff, band_list)
    #     fe_norm = normalizeDiffProperties(fe)
    #     return ee.Feature(fe_norm)
    #
    # points = points.map(applyBandValueExtraction)


    # NEW METHOD OF DIFF IN MAXES

    # map the band value analysis and set property

    def applyBandValueExtraction(feature_element):
        fe_t1 = addBandValueToFeature(ee.Feature(feature_element), t1, band_list, 10)
        fe_t2 = addBandValueToFeature(ee.Feature(feature_element), t2, band_list, 10)

        # take the difference between the two time periods
        prop_names = fe_t1.propertyNames()
        t1_props = fe_t1.toArray(prop_names)
        t2_props = fe_t2.toArray(prop_names)
        diff_in_props = t1_props.subtract(t2_props)

        # set the new peoperty values as the difference between t1 and t2
        prop_dic = ee.Dictionary.fromLists(prop_names, diff_in_props.toList())
        fe_t1 = fe_t1.set(prop_dic)


        fe_norm = normalizeDiffProperties(fe_t1)
        #fe_t1 = fe_t1.set("diff_factors", diff_factors)
        fe_norm = fe_norm.set("diff_factors", diff_factors)
        return fe_norm

    points = points.map(applyBandValueExtraction)


    # also map to the dictionary of control points
    def mapToDictionary(key, value):
        return ee.List(value).map(applyBandValueExtraction)

    control_points = ee.Dictionary(road_feature.get("points_control")).map(mapToDictionary)

    return road_feature.set("points", points, "points_control", control_points)


def determineUpgrade(road):
    '''

    :param road:
    :return:
    '''

    # extract all of the points for upgrade detection (main list and control dictionary)
    road_points = ee.List(road.get("points"))
    control_points = ee.Dictionary(road.get("points_control"))


    # declare function for band-value evaluation (returns list of matching points)
    def bandValueEval(list, band, operator, thresh):
        intersection_gt = ee.List(list).filter(ee.Filter.gt(band, thresh))
        intersection_lt = ee.List(list).filter(ee.Filter.lt(band, thresh))
        intersection_dic = ee.Dictionary({"gt": intersection_gt, "lt": intersection_lt})
        intersection = ee.List(intersection_dic.get(operator))
        share = intersection.length().divide(ee.List(list).length())
        return ee.Number(share)

    # filter out all of the left and right keys to separate lists
    left_keys = ee.List(control_points.keys().filter(ee.Filter.stringContains("item", "left")))
    right_keys = ee.List(control_points.keys().filter(ee.Filter.stringContains("item", "right")))


    # mapping function for evaluation of share for control points
    def bandValueEvalMapped(band, operator, thresh):
        def wrap(key):
            list = ee.List(control_points.get(key))
            share = ee.Number(bandValueEval(list, band, operator, thresh))
            return share
        return wrap


    left_list_B4_dark = left_keys.map(bandValueEvalMapped('B4_max', "gt", 200))
    left_list_B8_dark = left_keys.map(bandValueEvalMapped('B8_max', "gt", 200))
    right_list_B4_dark = right_keys.map(bandValueEvalMapped('B4_max', "gt", 200))
    right_list_B8_dark = right_keys.map(bandValueEvalMapped('B8_max', "gt", 200))

    left_list_B4_bright = left_keys.map(bandValueEvalMapped('B4_min', "lt", -200))
    left_list_B8_bright = left_keys.map(bandValueEvalMapped('B8_min', "lt", -200))
    right_list_B4_bright = right_keys.map(bandValueEvalMapped('B4_min', "lt", -200))
    right_list_B8_bright = right_keys.map(bandValueEvalMapped('B8_min', "lt", -200))

    avg_share_left_B4_dark = ee.Number(left_list_B4_dark.reduce(ee.Reducer.mean()))
    avg_share_left_B8_dark = ee.Number(left_list_B8_dark.reduce(ee.Reducer.mean()))
    avg_share_right_B4_dark = ee.Number(right_list_B4_dark.reduce(ee.Reducer.mean()))
    avg_share_right_B8_dark = ee.Number(right_list_B8_dark.reduce(ee.Reducer.mean()))

    avg_share_left_B4_bright = ee.Number(left_list_B4_bright.reduce(ee.Reducer.mean()))
    avg_share_left_B8_bright = ee.Number(left_list_B8_bright.reduce(ee.Reducer.mean()))
    avg_share_right_B4_bright = ee.Number(right_list_B4_bright.reduce(ee.Reducer.mean()))
    avg_share_right_B8_bright = ee.Number(right_list_B8_bright.reduce(ee.Reducer.mean()))

    share_B4_dark = ee.Number(bandValueEval(road_points, "B4_max", "gt", 200))
    share_B8_dark = ee.Number(bandValueEval(road_points, "B8_max", "gt", 200))
    share_B4_bright = ee.Number(bandValueEval(road_points, "B4_min", "lt", -200))
    share_B8_bright = ee.Number(bandValueEval(road_points, "B8_min", "lt", -200))


    # Set THRESHOLDS for upgrade classification

    thresholds = ee.List([
      ee.Dictionary({
        "B4_share_abs": 0.5, "B4_share_rel": 0.5,
        "B8_share_abs": 0.5, "B8_share_rel": 0.5}),
      ee.Dictionary({
        "B4_share_abs": 0.2, "B4_share_rel": 0.25,
        "B8_share_abs": 0.2, "B8_share_rel": 0.25})
    ])


    def checkThresh(thresh_dic):

        thresh_dic = ee.Dictionary(thresh_dic)
        B4_share_abs = thresh_dic.get("B4_share_abs")
        B4_share_rel = thresh_dic.get("B4_share_rel")
        B8_share_abs = thresh_dic.get("B8_share_abs")
        B8_share_rel = thresh_dic.get("B8_share_rel")


        # *** CHECK FOR PAVING

        # process dummies for relative share
        check_B4_asph = ee.List([share_B4_dark.multiply(B4_share_abs).subtract(avg_share_left_B4_dark).max(0).ceil(),
                                share_B4_dark.multiply(B4_share_abs).subtract(avg_share_right_B4_dark).max(0).ceil()])

        check_B4_asph = check_B4_asph.reduce(ee.Reducer.min())

        # also control for minimum value threshold
        thresh_check_B4_asph = share_B4_dark.subtract(B4_share_rel).ceil()

        check_B4_asph = ee.List([check_B4_asph, thresh_check_B4_asph]).reduce(ee.Reducer.min())



        check_B8_asph = ee.List([share_B8_dark.multiply(B8_share_abs).subtract(avg_share_left_B8_dark).max(0).ceil(),
                          share_B8_dark.multiply(B8_share_abs).subtract(avg_share_right_B8_dark).max(0).ceil()])

        check_B8_asph = check_B8_asph.reduce(ee.Reducer.min())

        # also control for minimum value threshold
        thresh_check_B8_asph = share_B8_dark.subtract(B8_share_rel).ceil()

        check_B8_asph = ee.List([check_B8_asph, thresh_check_B8_asph]).reduce(ee.Reducer.min())


        # Road is upgraded if check_B4 or check_B8 return 1, as such take the max of the two
        upgraded_asph = ee.Number(ee.List([check_B4_asph, check_B8_asph]).reduce(ee.Reducer.max()))


        # *** Check for LEVELING

        # process dummies for relative share
        check_B4_lev = ee.List([share_B4_bright.multiply(B4_share_abs).subtract(avg_share_left_B4_bright).max(0).ceil(),
                            share_B4_bright.multiply(B4_share_abs).subtract(avg_share_right_B4_bright).max(0).ceil()])

        check_B4_lev = check_B4_lev.reduce(ee.Reducer.min())

        # also control for minimum value threshold
        thresh_check_B4_lev = share_B4_bright.subtract(B4_share_rel).ceil()

        check_B4_lev = ee.List([check_B4_lev, thresh_check_B4_lev]).reduce(ee.Reducer.min())


        check_B8_lev = ee.List([share_B8_bright.multiply(B8_share_abs).subtract(avg_share_left_B8_bright).max(0).ceil(),
                            share_B8_bright.multiply(B8_share_abs).subtract(avg_share_right_B8_bright).max(0).ceil()])

        check_B8_lev = check_B8_lev.reduce(ee.Reducer.min())

        # also control for minimum value threshold
        thresh_check_B8_lev = share_B8_bright.subtract(B8_share_rel).ceil()

        check_B8_lev = ee.List([check_B8_lev, thresh_check_B8_lev]).reduce(ee.Reducer.min())

        # Road is upgraded if check_B4 or check_B8 return 1, as such take the max of the two
        upgraded_lev = ee.Number(ee.List([check_B4_lev, check_B8_lev]).reduce(ee.Reducer.max()))

        return ee.List([upgraded_asph, upgraded_lev])



    # Now map the threshold share upgrade detection onto the list of thresholds
    # here we unzip such that first list has dummies for asph, and second for lev
    upg_dummies = thresholds.map(checkThresh).unzip()


    def mapReduce(mylist):
        mylist = ee.List(mylist)
        return ee.Number(mylist.reduce(ee.Reducer.max()))

    upg_dummies = upg_dummies.map(mapReduce)

    # Dummy for upgraded in general
    upgraded = ee.Number(upg_dummies.reduce(ee.Reducer.max()))

    upgraded_asph = ee.Number(upg_dummies.get(0))
    upgraded_lev =  ee.Number(upg_dummies.get(1))

    #get string categorization of upgrade type
    upgrade_sum = upgraded_asph.add(upgraded_lev)

    # extract the determined upgrade type
    upgrade_options = ee.List([
        ee.Feature(None, {'type': 'paving', 'value': ee.Number(upgraded_asph)}),
        ee.Feature(None, {'type': 'leveling', 'value': ee.Number(upgraded_lev)}),
        ee.Feature(None, {'type': 'none', 'value': ee.Number(0.1)}),
        ee.Feature(None, {'type': 'error', 'value': ee.Number(ee.Number(upgrade_sum).multiply(0.9))})
    ])
    upgrade_type = ee.String(ee.FeatureCollection(upgrade_options).sort('value', False).first().get('type'))

    # Create the dictionaries for each upgrade type
    analysis_bright = ee.Dictionary(
        {"share_B4": share_B4_bright, "share_B4_left": avg_share_left_B4_bright,
         "share_B4_right": avg_share_right_B4_bright, "share_B8": share_B8_bright,
         "share_B8_left": avg_share_left_B8_bright, "share_B8_right": avg_share_right_B8_bright}
        )
    analysis_dark = ee.Dictionary(
        {"share_B4": share_B4_dark, "share_B4_left": avg_share_left_B4_dark,
         "share_B4_right":avg_share_right_B4_dark, "share_B8": share_B8_dark,
         "share_B8_left": avg_share_left_B8_dark, "share_B8_right": avg_share_right_B8_dark}
        )

    road = road.set("analysis_bright", analysis_bright, "analysis_dark", analysis_dark,
                      "upgraded", upgraded, "upgrade_type", upgrade_type)

    print(road.getInfo())
    return road


def subsetFeatureCollection(fc, id_list):

    if id_list == None:
        return ee.FeatureCollection(fc)

    def getFeatureByID(fc):
        def wrap(id):
            return ee.FeatureCollection(fc).toList(1, ee.Number(id)).get(0)
        return wrap

    fc_list = ee.List(id_list).map(getFeatureByID(fc))
    return ee.FeatureCollection(fc_list)


if __name__ == "__main__":

    x = distanceInKmBetweenCoordinates([[40.1594667255232, -15.008981876915604],
                                    [40.15947564372531, -15.008981876915604]])
    print("x is", x.getInfo())
    pass