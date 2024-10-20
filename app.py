from export import export_geojson
from parsing import read_directory
from preprocessing import process
import osmnx
import logging
from stats import calculate_stats

logging.basicConfig(level=logging.INFO)


def main():
    logging.info("Starting")
    logging.info("Downloading graph")
    G = osmnx.graph_from_place("Barcelona, Spain", network_type="walk", simplify=False)

    logging.info("Reading GPX files")
    raw_files = read_directory("./raw_walks/")
    logging.info(f"Read {len(raw_files)} files")

    logging.info("Processing GPX files")
    processed_walks = process(G, raw_files)
    logging.info("Done")

    logging.info("Calculating stats")
    stats = calculate_stats(G, raw_files, processed_walks)
    logging.info("Done")

    logging.info("Exporting to GeoJSON")
    export_geojson(G, raw_files, processed_walks)
    logging.info("Done")


# Main
if __name__ == "__main__":
    main()