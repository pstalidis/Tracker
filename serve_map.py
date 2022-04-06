import pandas
import folium
import flask


def dms2dd(sample):
    # example: s = """2257.702"""
    degrees, minutes = divmod(float(sample), 100)
    dd = round(float(degrees) + float(minutes)/60, 6)
    return dd


app = flask.Flask("mapping")


def get_map():
    df = pandas.read_csv("locations.csv")
    df["datetime"] = pandas.to_datetime(df['datetime'], format='%y%m%d%H%M%S')
    # df["clock"] = pandas.to_datetime(df['clock'], format='%H%M%S').dt.time
    df["latitude"] = df.lat.apply(dms2dd)
    df["longitude"] = df.lon.apply(dms2dd)

    tracks = [[]]
    parked = True
    for i, row in df.iterrows():
        if row.operation == "acc on":
            parked = False
            tracks.append([(row["latitude"], row["longitude"])])
        elif row.operation == "acc off":
            parked = True
            tracks[-1].append((row["latitude"], row["longitude"]))
        elif not parked:
            tracks[-1].append((row["latitude"], row["longitude"]))

    tracks = tracks[1:]
    my_map = folium.Map(location=tracks[-1][-1], tiles='OpenStreetMap', zoom_start=16)
    for i, track in enumerate(tracks):
        fg = folium.FeatureGroup(name="Track %d" % i, show=False)
        folium.PolyLine(track, color="blue", weight=10, opacity=0.5).add_to(fg)
        folium.Marker(location=track[0],
                      icon=folium.Icon(color="green", icon="car", prefix='fa')).add_to(fg)
        if not parked and i == len(tracks) - 1:
            folium.Marker(location=track[-1],
                          icon=folium.Icon(color="blue", icon="car", prefix='fa')).add_to(fg)
        else:
            folium.Marker(location=track[-1],
                          icon=folium.Icon(color="red", icon="car", prefix='fa')).add_to(fg)
        if i == len(tracks) - 1:
            fg.show = True
        fg.add_to(my_map)

    folium.LayerControl().add_to(my_map)
    return my_map


@app.route('/')
def index():
    return get_map().get_root().render()


if __name__ == '__main__':
    app.run(host="195.251.117.224", port=8181, debug=True)
