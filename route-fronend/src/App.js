import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMap
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
  RadioGroup,
  FormControlLabel,
  Radio,
} from "@mui/material";
import "./App.css";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import L from "leaflet";

// Default coordinates for source and target
const defaultSource = [49.2292, -122.9932];
const defaultTarget = [49.2813912, -123.1217871];

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
});

L.Marker.prototype.options.icon = DefaultIcon;

function App() {
  const [distanceInput, setDistanceInput] = useState("");
  const [elevationRange, setElevationRange] = useState("0-200");
  const [poiMin, setPoiMin] = useState(0);
  const [priorityFactor, setPriorityFactor] = useState("elevation");
  const [distance, setDistance] = useState("");
  const [elevationChange, setElevationChange] = useState("");
  const [poiCount, setPoiCount] = useState("");
  const [pathData, setPathData] = useState([]);
  const [startLat, setStartLat] = useState(defaultSource[0]);
  const [startLng, setStartLng] = useState(defaultSource[1]);
  const [endLat, setEndLat] = useState(defaultTarget[0]);
  const [endLng, setEndLng] = useState(defaultTarget[1]);
  const [poiNodes, setPoiNodes] = useState([]);

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
          elevation_range: elevationRange,
          poi_min: poiMin,
          priority_factor: priorityFactor,
        }),
      });

      const data = await response.json();
      if (data.message) {

        alert(data.message);
        return;
      }

      if (!response.ok) throw new Error("Failed to fetch route");

      const bestPath = data.best_path;

      setPathData(bestPath.path_segments);
      setDistance(bestPath.distance);
      setPoiNodes(bestPath.poi_nodes);
      setElevationChange(bestPath.elevation_change);
      setPoiCount(bestPath.poi_count);
    } catch (error) {
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
          maxWidth: "300px",
          width: "100%",
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

        <FormControl variant="outlined" sx={{ mb: 2 }} fullWidth>
          <InputLabel>Elevation Range</InputLabel>
          <Select
            value={elevationRange}
            onChange={(e) => setElevationRange(e.target.value)}
            label="Elevation Range"
          >
            <MenuItem value="0-200">0-200</MenuItem>
            <MenuItem value="200-400">200-400</MenuItem>
            <MenuItem value="400-600">400-600</MenuItem>
            <MenuItem value="600-800">600-800</MenuItem>
            <MenuItem value="800-1000">800-1000</MenuItem>
            <MenuItem value="1000+">1000+</MenuItem>
          </Select>
        </FormControl>

        <TextField
          label="Minimum POI"
          variant="outlined"
          type="number"
          fullWidth
          value={poiMin}
          onChange={(e) => setPoiMin(parseInt(e.target.value, 10))}
          sx={{ mb: 2 }}
        />

        {/* Priority Factor */}
        <FormControl component="fieldset" sx={{ mb: 2 }}>
          <Typography>Priority Factor</Typography>
          <RadioGroup
            row
            value={priorityFactor}
            onChange={(e) => setPriorityFactor(e.target.value)}
          >
            <FormControlLabel
              value="elevation"
              control={<Radio />}
              label="Elevation"
            />
            <FormControlLabel
              value="poi"
              control={<Radio />}
              label="POI"
            />
          </RadioGroup>
        </FormControl>

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
        scrollWheelZoom={true}
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

        {/* Mark POI Nodes */}
        {poiNodes.map((poi, index) => (
          <Marker key={index} position={[poi[0], poi[1]]}>
            <Popup>
              POI {index + 1} <br />
            </Popup>
          </Marker>
        ))}

        {pathData.length > 0 && (
          <Polyline
            positions={pathData}
            color="blue"
            weight={4}
            opacity={0.7}
          />
        )}
         <MapCenterUpdater pathData={pathData} />
      </MapContainer>
    </div>
  );
}

// Component to reset the map center after route calculation
const MapCenterUpdater = ({ pathData }) => {
  const map = useMap();

  React.useEffect(() => {
    if (pathData.length > 0) {
      const bounds = L.latLngBounds(pathData);
      map.fitBounds(bounds); // Fit the map to the bounds of the path
    }
  }, [pathData, map]);

  return null; // This component does not render anything visible
};

export default App;

