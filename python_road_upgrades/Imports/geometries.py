import ee


region_1 = ee.Geometry.Polygon(
    [[[39.325013195421946, -15.40058788989606],
      [39.32136539116169, -15.412172390591678],
      [39.32870391502644, -15.414116868506305],
      [39.332995449450266, -15.401994613692356]]])

region_2 = ee.Geometry.Polygon(
    [[[35.75291589019721, -12.841064012596293],
      [35.75291589019721, -12.854222991230456],
      [35.77033951995795, -12.854222991230456],
      [35.77033951995795, -12.841064012596293]]])

region_3 = ee.Geometry.MultiPolygon(
    [[[[39.77919003185838, -15.391426393138541],
       [39.77919003185838, -15.42171155996196],
       [39.84334847149461, -15.42171155996196],
       [39.84334847149461, -15.391426393138541]]],
     [[[40.50780984421659, -14.98848362467065],
       [40.50780984421659, -14.996069804788258],
       [40.51832410355497, -14.996069804788258],
       [40.51832410355497, -14.98848362467065]]]])