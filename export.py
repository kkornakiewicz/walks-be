import datetime
import json
from pathlib import Path
from parsing import Walk
import osmnx
import numpy as np

def df_to_geojson_edges(df, properties):
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type':'FeatureCollection', 'features':[]}
    
    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
            
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':
                   {'type':'LineString',
                               'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [[row["start_lon"],row["start_lat"]],[row["end_lon"],row["end_lat"]]] 

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
            
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson

def df_to_geojson_nodes(df, properties):
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type':'FeatureCollection', 'features':[]}
    
    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':
                   {'type':'Point',
                               'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row["x"],row["y"]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
            
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson

def export_geojson(G, raw_files: list[Walk], processed_walks: dict[str, dict[str, list[int]]]):
    # Simplify the graph for better visualization performance
    G_simplified = osmnx.simplify_graph(G)
    nodes, edges = osmnx.convert.graph_to_gdfs(G_simplified, nodes=True, edges=True, node_geometry=False)
    edges = edges.reset_index()

    # Process walk data
    visited_nodes = set()
    for file in raw_files:
        visited_nodes.update(sum(processed_walks[file.filename].values(), [])) 
    visited_nodes = list(visited_nodes)

    # Update node and edge data
    nodes["visited"] = nodes.index.isin(visited_nodes) # Mark visited nodes
    edges["visited"] = edges.apply(lambda row: row["u"] in visited_nodes and row["v"] in visited_nodes, axis=1) # Mark visited edges
    edges["name"] = edges["name"].fillna("Unnamed road") # Fill missing names

    # Prepare edge data for GeoJSON conversion
    edges_geojson = edges.join(nodes[["x", "y"]], on="u").rename(columns={"x": "start_lon", "y": "start_lat"}) # Join start node coordinates
    edges_geojson = edges_geojson.join(nodes[["x", "y"]], on="v").rename(columns={"x": "end_lon", "y": "end_lat"}) # Join end node coordinates
    edges_geojson = edges_geojson.drop(columns=["geometry", "visited_x", "visited_y"]) # Drop unused columns

    # Prepare node data for GeoJSON conversion
    nodes_geo = nodes.reset_index() # Reset index to make it a column

    # Export edges as GeoJSON
    export_edges = df_to_geojson_edges(edges_geojson, ["name", "osmid", "visited"])
    with open('output/edges.json', 'w', encoding='utf-8') as f:
        json.dump(export_edges, f)

    # Export nodes as GeoJSON
    export_nodes = df_to_geojson_nodes(nodes_geo, ["osmid", "visited"])
    with open('output/nodes.json', 'w', encoding='utf-8') as f:
        json.dump(export_nodes, f)
