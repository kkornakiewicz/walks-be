import datetime
import json
from parsing import Walk
import osmnx
import numpy as np


def df_to_geojson_edges(df, properties):
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {"type": "FeatureCollection", "features": []}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():

        # create a feature template to fill in
        feature = {
            "type": "Feature",
            "properties": {},
            "geometry": {"type": "LineString", "coordinates": []},
        }

        # fill in the coordinates
        feature["geometry"]["coordinates"] = [
            [row["start_lon"], row["start_lat"]],
            [row["end_lon"], row["end_lat"]],
        ]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature["properties"][prop] = row[prop]

        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson["features"].append(feature)

    return geojson


def df_to_geojson_nodes(df, properties):
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {"type": "FeatureCollection", "features": []}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {
            "type": "Feature",
            "properties": {},
            "geometry": {"type": "Point", "coordinates": []},
        }

        # fill in the coordinates
        feature["geometry"]["coordinates"] = [row["x"], row["y"]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature["properties"][prop] = row[prop]

        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson["features"].append(feature)

    return geojson


def export_geojson(
    G, raw_files: list[Walk], processed_walks: dict[str, dict[str, list[int]]]
):

    # For performance reasons, I simplify the graph so that the number of nodes and edges is reduced on visualisation
    G_simplified = osmnx.simplify_graph(G)
    nodes = osmnx.convert.graph_to_gdfs(G_simplified, edges=False, node_geometry=False)[
        ["x", "y"]
    ]
    edges = osmnx.convert.graph_to_gdfs(G_simplified, edges=True, nodes=False)
    edges = edges.reset_index()

    # Matching walk raw data and processed files
    data = []
    for file in raw_files:
        nodes_set = set()
        for v in processed_walks[file.filename].values():
            nodes_set.update(v)
        data.append(
            {
                "nodes": list(nodes_set),
                "length": file.length(),
                "date": datetime.datetime.fromisoformat(file.start_time()),
            }
        )
    nested_list = [d["nodes"] for d in data]
    visited_nodes = list(set(sum(nested_list, [])))
    nodes["visited"] = np.isin(nodes.index, visited_nodes)

    edges_geojson = edges.join(nodes, on="u")
    edges_geojson = edges_geojson.rename(columns={"x": "start_lon", "y": "start_lat"})
    edges_geojson = edges_geojson.drop(columns="visited")
    edges_geojson = edges_geojson.join(nodes, on="v")
    edges_geojson = edges_geojson.rename(columns={"x": "end_lon", "y": "end_lat"})
    edges_geojson = edges_geojson.drop(columns="geometry")
    edges_geojson = edges_geojson.drop(columns="visited")
    edges_geojson["name"] = edges_geojson["name"].fillna(value="Unnamed road")
    edges_geojson["visited"] = np.logical_and(
        np.isin(edges.u, visited_nodes), np.isin(edges.v, visited_nodes)
    )

    nodes_geo = osmnx.convert.graph_to_gdfs(
        G_simplified, edges=False, node_geometry=False
    )[["x", "y"]]
    nodes_geo = nodes_geo.reset_index()
    nodes_geo["visited"] = np.isin(nodes_geo.osmid, visited_nodes)

    export_edges = df_to_geojson_edges(edges_geojson, ["name", "osmid", "visited"])
    with open("output/edges.json", "w", encoding="utf-8") as f:
        json.dump(export_edges, f)

    export_nodes = df_to_geojson_nodes(nodes_geo, ["osmid", "visited"])
    with open("output/nodes.json", "w", encoding="utf-8") as f:
        json.dump(export_nodes, f)
