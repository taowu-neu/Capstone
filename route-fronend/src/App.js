import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
} from "react-leaflet";
import {
  TextField,
  Button,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Typography,
  Box,
} from "@mui/material";
import "./App.css";

// Default coordinates for source and target
const defaultSource = [49.2292, -122.9932];
const defaultTarget = [49.2813912, -123.1217871];

function App() {
  const [distanceInput, setDistanceInput] = useState("");
  const [elevation, setElevation] = useState("max");
  const [poi, setPoi] = useState("max");
  const [distance, setDistance] = useState("N/A");
  const [elevationChange, setElevationChange] = useState("N/A");
  const [poiCount, setPoiCount] = useState("N/A");
  const [pathData, setPathData] = useState([]);
  const [startLat, setStartLat] = useState(defaultSource[0]);
  const [startLng, setStartLng] = useState(defaultSource[1]);
  const [endLat, setEndLat] = useState(defaultTarget[0]);
  const [endLng, setEndLng] = useState(defaultTarget[1]);

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
          source: [startLat, startLng],
          target: [endLat, endLng],
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
      <div
        style={{
          position: "absolute",
          top: "20px",
          left: "20px",
          zIndex: 1000,
          backgroundColor: "white",
          padding: "16px",
          borderRadius: "8px",
          boxShadow: "0px 4px 6px rgba(0,0,0,0.1)",
        }}
      >
        {/* Start Point Input Fields */}
        <Box display="flex" justifyContent="space-between" sx={{ mb: 2 }}>
          <TextField
            label="Start Latitude"
            variant="outlined"
            type="number"
            fullWidth
            value={startLat}
            onChange={(e) => setStartLat(parseFloat(e.target.value))}
          />
          <TextField
            label="Start Longitude"
            variant="outlined"
            type="number"
            fullWidth
            value={startLng}
            onChange={(e) => setStartLng(parseFloat(e.target.value))}
          />
        </Box>

        {/* End Point Input Fields */}
        <Box display="flex" justifyContent="space-between" sx={{ mb: 2 }}>
          <TextField
            label="End Latitude"
            variant="outlined"
            type="number"
            fullWidth
            value={endLat}
            onChange={(e) => setEndLat(parseFloat(e.target.value))}
          />
          <TextField
            label="End Longitude"
            variant="outlined"
            type="number"
            fullWidth
            value={endLng}
            onChange={(e) => setEndLng(parseFloat(e.target.value))}
          />
        </Box>

        <TextField
          sx={{ mb: 2 }}
          label="Input Distance (km)"
          variant="outlined"
          fullWidth
          value={distanceInput}
          onChange={(e) => setDistanceInput(e.target.value)}
        />

        {/* Elevation and POI Preferences */}
        <Box display="flex" justifyContent="space-between">
          <FormControl variant="outlined" sx={{ mb: 2 }} fullWidth>
            <InputLabel>Elevation</InputLabel>
            <Select
              value={elevation}
              onChange={(e) => setElevation(e.target.value)}
              label="Elevation"
            >
              <MenuItem value="max">Max</MenuItem>
              <MenuItem value="min">Min</MenuItem>
            </Select>
          </FormControl>

          <FormControl variant="outlined" sx={{ mb: 2 }} fullWidth>
            <InputLabel>POI</InputLabel>
            <Select
              value={poi}
              onChange={(e) => setPoi(e.target.value)}
              label="POI"
            >
              <MenuItem value="max">Max</MenuItem>
              <MenuItem value="min">Min</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={calculateRoute}
          sx={{ mt: 2 }}
        >
          Get Route
        </Button>

        <div style={{ marginTop: "16px" }}>
          <Typography variant="body1">Distance: {distance}</Typography>
          <Typography variant="body1">
            Elevation Change: {elevationChange}
          </Typography>
          <Typography variant="body1">POI Count: {poiCount}</Typography>
        </div>
      </div>

      <MapContainer
        center={[49.174, -123.184]}
        zoom={13}
        scrollWheelZoom={false}
        style={{ height: "100vh", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {/* Markers for Start and End Points */}
        <Marker position={[startLat, startLng]}>
          <Popup>
            Start Point <br /> Latitude: {startLat}, Longitude: {startLng}
          </Popup>
        </Marker>

        <Marker position={[endLat, endLng]}>
          <Popup>
            End Point <br /> Latitude: {endLat}, Longitude: {endLng}
          </Popup>
        </Marker>

        {pathData.length > 0 && (
          <Polyline
            positions={pathData}
            color="blue"
            weight={4}
            opacity={0.7}
          />
        )}
      </MapContainer>
    </div>
  );
}

export default App;
