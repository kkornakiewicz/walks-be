from parser import read_gpx_file, read_directory, Waypoint
import osmnx
import geopandas as gpd
from shapely.geometry import  Point
import pandas as pd
import json
import os.path
from os import listdir
from pathlib import Path
from multiprocessing import Pool
from functools import partial

# Find nodes near a given point
def process_point(point: Waypoint, G):
    distance = 20 # in meteres
    try:
        found = []
        box = osmnx.utils_geo.bbox_from_point((point.lat, point.lon), distance)
        sub = osmnx.truncate.truncate_graph_bbox(G, bbox=box, retain_all=True)
        found = list(sub.nodes)
        print(f"Found: {len(found)}")

        # Return tuple of time and found nodes
        return (point.time, found)
    except Exception as e:
        print("No nodes found.")
        print(e)
        return (point.time, [])

def get_graph():
    return osmnx.graph_from_place("Barcelona, Spain", network_type="walk", simplify=False)

def process(G):
    gpx_files = read_directory("./raw_walks/")

    count_files = 0

    files = gpx_files
    for gpx in files:
        count_files += 1
        print(f"Processing {count_files} / {len(files)} - {gpx.filename}")
        json_name = f"./processed_walks/{gpx.filename}.json"
        if os.path.isfile(json_name):
            continue
        
        _process_point = partial(process_point, G=G)

        nodes = dict()
        for segment in gpx.segments:
            count = 0
            print(f"Processing {len(segment.waypoints)} points")
            p = Pool(5)
            result = p.imap(_process_point, segment.waypoints)
    
            for r in result:
                nodes[r[0]] = r[1]
                if count % 10 == 0:
                    print(f"Processed {count}/{len(segment.waypoints)}")
                count += 1
    
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(nodes, f, ensure_ascii=False)
    
