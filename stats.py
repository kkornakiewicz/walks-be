from collections import defaultdict
import datetime
import osmnx
import pandas as pd

from parsing import Walk


def calculate_stats(
    G, raw_files: list[Walk], processed_walks: dict[str, dict[str, list[int]]]
):
    # Getting geo-data of streets
    edges = list(osmnx.graph_to_gdfs(G, nodes=False, edges=True).fillna("").iterrows())

    # Calculate nodes per street name
    nodes_per_street = defaultdict(set)
    for edge in edges:
        if edge[1]["name"]:
            nodes_per_street[edge[1]["name"]].add(edge[0][0])
        nodes_per_street[edge[1]["name"]].add(edge[0][1])

    # Matching walk raw data and processed files
    data = []
    stats = []
    total_length = 0
    total_in_graph = len(G.nodes)
    total_streets = len(nodes_per_street)
    so_far_nodes = set()
    so_far_streets = set()

    for file in raw_files:
        nodes = set()
        for v in processed_walks[file.filename].values():
            nodes.update(v)
        data.append(
            {
                "nodes": nodes,
                "length": file.length(),
                "date": datetime.datetime.fromisoformat(file.start_time()),
            }
        )

        # Calculate stats


        for j in data:
            new_nodes = j["nodes"] - so_far_nodes
            so_far_nodes.update(j["nodes"])

        new_streets = 0
        for street, nodes in nodes_per_street.items():
            # Intersection of a street's node and visited nodes
            so_far_in_a_street = nodes & so_far_nodes

            # If vistited at least 90% of streets nodes, it's marked as completed
            if len(so_far_in_a_street) / len(nodes) > 0.9 and not street in so_far_streets:
                so_far_streets.add(street)
                new_streets += 1

        visited = len(j["nodes"])
        length_in_km = j["length"] / 1000
        total_length += length_in_km  # in kms
        total = len(so_far_nodes)
        progress = len(so_far_nodes) / total_in_graph * 100
        progress_streets = len(so_far_streets) / total_streets * 100
        stats.append(
            {
                "Date": j["date"].date().isoformat(),
                "Visited nodes": len(j["nodes"]),
                "New nodes": len(new_nodes),
                "Total visited nodes": total,
                "Walk length (km)": f"{length_in_km:.2f}",
                "Total walked (km)": f"{total_length:.2f}",
                "Nodes completion (%)": f"{progress:.2f}",
                "New streets": new_streets,
                "Total streets": len(so_far_streets),
                "Streets completion (%)": f"{progress_streets:.2f}",
            }
        )
    stats_df = pd.DataFrame.from_dict(stats)

    # Saving to CSV
    stats_df.to_csv("./output/stats.csv", index=False)
    return
