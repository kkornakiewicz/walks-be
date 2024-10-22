import logging
import config
from parsing import Walk
import osmnx
from scipy.spatial import cKDTree


# Returns a dictionary with the filename as key and a dictionary with the time as key and the list of node ids as value
def process(G, gpx_files: list[Walk]) -> dict[str, dict[str, list[int]]]:
    nodes = osmnx.convert.graph_to_gdfs(G, edges=False, node_geometry=False)[["x", "y"]]
    list_of_nodes = list(nodes.iterrows())
    distance_m = config.DISTANCE
    distance = 0.000009 * distance_m

    tree = cKDTree(nodes)
    files = gpx_files
    result = dict()
    count_files = 0

    logging.info(f"Processing {len(files)} files")

    for gpx in files:
        count_files += 1
        logging.info(f"Processing {count_files} / {len(files)} - {gpx.filename}")

        def process_gpx(gpx, tree, list_of_nodes, distance):
            nodes = dict()
            for segment in gpx.segments:
                for p in segment.waypoints:
                    nodes_nearby = tree.query_ball_point((p.lon, p.lat), distance)
                    nodes_nearby_mapped = [list_of_nodes[x][0] for x in nodes_nearby]
                    nodes[p.time] = nodes_nearby_mapped
            return nodes

        result[gpx.filename] = process_gpx(gpx, tree, list_of_nodes, distance)

    return result
