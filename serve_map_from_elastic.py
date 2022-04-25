# import pandas
import folium
import flask
import sys
import time

import elasticsearch
from datetime import datetime, timedelta

app = flask.Flask("mapping")

time.sleep(60)

es = elasticsearch.Elasticsearch(["elastic:9200"])
if not es.indices.exists(index='cobra'):
    sys.exit(1)


def get_all_hits_for_the_last(days=2):
    query = {
        "sort": [
            {"datetime": {"order": "asc"}},  # , "format": "strict_date_optional_time_nanos"
        ],
        "query": {
            "bool": {
                "filter": [{
                    "range": {
                        "datetime": {
                            "gte": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S"),
                            "lte": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                }]
            }
        },
        "size": 1000
    }
    locations = []
    results = es.search(index="cobra", body=query, scroll="10m")
    while len(results["hits"]["hits"]) > 0:
        scroll_id = results["_scroll_id"]
        locations += results["hits"]["hits"]
        results = es.scroll(scroll_id=scroll_id, scroll="10m")
    return locations


def get_map():
    tracks = [[]]
    parked = True
    hits = get_all_hits_for_the_last(days=5)
    for hit in hits:
        row = hit["_source"]
        if row["operation"] == "acc on":
            parked = False
            tracks.append([(row["location"]["lat"], row["location"]["lon"])])
        elif row["operation"] == "acc off":
            parked = True
            tracks[-1].append((row["location"]["lat"], row["location"]["lon"]))
        elif not parked:
            tracks[-1].append((row["location"]["lat"], row["location"]["lon"]))

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
    app.run(host="0.0.0.0", port=5000, debug=True)
