SELECT z.cid_id, z.latitude, content.timeCreated
FROM JokrBackend_content_localpost AS z 
LEFT JOIN JokrBackend_postablecontent as content ON z.cid_id = content.id



SELECT id, fromUser_id, latitude, longitude, timeCreated, text, url, weight, distance
                FROM (
                    SELECT content.id, content.fromUser_id, lp.latitude, lp.longitude, content.timeCreated, lp.text, content.url,
                    p.radius,
                     p.distance_unit
                             * DEGREES(ACOS(COS(RADIANS(p.latpoint))
                             * COS(RADIANS(lp.latitude))
                             * COS(RADIANS(p.longpoint - lp.longitude))
                             + SIN(RADIANS(p.latpoint))
                             * SIN(RADIANS(lp.latitude)))) AS distance,
                    (POW(10,7) / (2 * POW(                                      
                    p.distance_unit
                             * DEGREES(ACOS(COS(RADIANS(p.latpoint))
                             * COS(RADIANS(lp.latitude))
                             * COS(RADIANS(p.longpoint - lp.longitude))
                             + SIN(RADIANS(p.latpoint))
                             * SIN(RADIANS(lp.latitude))))                   
                    , 2)                   
                    + 1.7 * ((UNIX_TIMESTAMP() - content.timeCreated) / 60.0)                   
                    )) as weight
                    FROM JokrBackend_content_localpost AS lp
		JOIN JokrBackend_postablecontent as content ON lp.cid_id = content.id
                JOIN (   /* these are the query parameters */
                    SELECT  40.0000  AS latpoint,  -80.000 AS longpoint,
                            90000 AS radius,      123 AS distance_unit
                ) AS p ON 1=1
              WHERE lp.latitude
                 BETWEEN p.latpoint  - (p.radius / p.distance_unit)
                     AND p.latpoint  + (p.radius / p.distance_unit)
                AND lp.longitude
                 BETWEEN p.longpoint - (p.radius / (p.distance_unit * COS(RADIANS(p.latpoint))))
                     AND p.longpoint + (p.radius / (p.distance_unit * COS(RADIANS(p.latpoint))))
             ) AS d
             ORDER BY weight DESC
