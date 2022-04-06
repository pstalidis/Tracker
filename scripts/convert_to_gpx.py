import gpxpy


gpx = gpxpy.gpx.GPX()
# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Create points:
with open("locations.txt", "r") as source:
    for point in source:
        date, lat, lon = point.strip().split(",")
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=1))


# You can add routes and waypoints, too...
# print('Created GPX:', )
with open("locations.gpx", "w") as target:
    target.write(gpx.to_xml())


