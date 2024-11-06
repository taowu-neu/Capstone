import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Polyline, useMap } from "react-leaflet";
import L from "leaflet"; // Import Leaflet directly
import { AntPath, antPath } from 'leaflet-ant-path';
import "./App.css";

// Default coordinates for source and target
const source = [49.2292, -122.9932];
const target = [49.2813912, -123.1217871];

function App() {
  const [distanceInput, setDistanceInput] = useState("");
  const [elevation, setElevation] = useState("max");
  const [poi, setPoi] = useState("max");
  const [distance, setDistance] = useState("N/A");
  const [elevationChange, setElevationChange] = useState("N/A");
  const [poiCount, setPoiCount] = useState("N/A");
  const [pathData, setPathData] = useState([]);
  const [pathLayer, setPathLayer] = useState(null);

  const mapRef = useRef(null);
  const calculateRoute = async () => {
    const inputDistance = parseFloat(distanceInput);
    if (isNaN(inputDistance) || inputDistance <= 0) {
      alert("Please enter a valid distance in km.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:5000/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source,
          target,
          input_distance: inputDistance,
          elevation,
          poi,
        }),
      });

      if (!response.ok) throw new Error("Failed to fetch route");

      const data = await response.json();
      const bestPath = data.best_path;

      setPathData(bestPath.path_segments);

      setDistance(bestPath.distance);
      setElevationChange(bestPath.elevation_change);
      setPoiCount(bestPath.poi_count);
    } catch (error) {
      console.error("Error:", error);
      alert("Error fetching the route.");
    }
  };

  return (
    <div>
      <div className="controls">
        <input
          type="number"
          value={distanceInput}
          onChange={(e) => setDistanceInput(e.target.value)}
          placeholder="Input Distance (km)"
        />
        <label htmlFor="elevationSelect">Elevation:</label>
        <select
          id="elevationSelect"
          value={elevation}
          onChange={(e) => setElevation(e.target.value)}
        >
          <option value="max">Max</option>
          <option value="min">Min</option>
        </select>

        <label htmlFor="poiSelect">POI:</label>
        <select
          id="poiSelect"
          value={poi}
          onChange={(e) => setPoi(e.target.value)}
        >
          <option value="max">Max</option>
          <option value="min">Min</option>
        </select>

        <button onClick={calculateRoute}>Get Route</button>
        <div id="distanceDisplay" style={{ marginTop: "10px" }}>
          Distance: {distance}
        </div>
        <div id="elevationDisplay" style={{ marginTop: "10px" }}>
          Elevation Change: {elevationChange}
        </div>
        <div id="poiDisplay" style={{ marginTop: "10px" }}>
          POI Count: {poiCount}
        </div>
      </div>

      <MapContainer
        center={[49.174, -123.184]}
        zoom={13}
        scrollWheelZoom={false}
        style={{ height: "100vh", width: "100wh" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={pathData} color="blue" weight={4} opacity={0.7} />
      </MapContainer>
    </div>
  );
}

export default App;
