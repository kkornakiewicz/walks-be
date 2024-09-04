from dataclasses import dataclass
from pathlib import Path
from os import listdir

import xml.etree.ElementTree as ET
import osmnx


@dataclass
class Waypoint:
    lat: float
    lon: float
    time: str


@dataclass
class Segment:
    waypoints: list[Waypoint]


@dataclass
class Walk:
    # Usually walk has only one segment, but for completenes I keep this as list
    segments: list[Segment]
    filename: str

    def start_time(self):
        return self.segments[0].waypoints[0].time

    def length(self):
        total = 0
        for segment in self.segments:
            zipped = zip(segment.waypoints, segment.waypoints[1:])
            for z in zipped:
                distance = osmnx.distance.great_circle(
                    z[0].lat, z[0].lon, z[1].lat, z[1].lon
                )
                total = total + (distance)
        return total


def read_gpx_file(file: str) -> int:
    count = 0
    segments = []
    filename = Path(file).stem  # Directory and extension is dropped

    namespaces = {"gpx": "http://www.topografix.com/GPX/1/1"}
    tree = ET.parse(file)
    root = tree.getroot()
    trk_segments = root.findall(".//gpx:trkseg", namespaces)

    for trkseg in trk_segments:
        points = []
        trk_points = trkseg.findall(".//gpx:trkpt", namespaces)

        for p in trk_points:
            lon = float(p.attrib["lon"])
            lat = float(p.attrib["lat"])
            time = p.find(".//gpx:time", namespaces).text

            points.append(Waypoint(lon=lon, lat=lat, time=time))

        segments.append(Segment(waypoints=points))

    return Walk(segments=segments, filename=filename)


def read_directory(directory: str) -> list[Walk]:
    files = listdir(directory)
    walks = []

    for file in files:
        if Path(file).suffix == ".gpx":
            walks.append(read_gpx_file(directory + file))
            # print(f"GPX file {file} found and parsed.")

        else:
            print(f"Non-GPX file {file} found, ignoring.")

    # Sorting walks by date will make processing easier
    return sorted(walks, key=lambda x: x.start_time())

