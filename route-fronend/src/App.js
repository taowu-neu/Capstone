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
  RadioGroup,
  FormControlLabel,
  Radio,
  Autocomplete,
} from "@mui/material";
import "./App.css";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import L from "leaflet";

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
});

L.Marker.prototype.options.icon = DefaultIcon;

const BACKEND_BASE_URL = "http://127.0.0.1:5000";

function App() {
  const [distanceInput, setDistanceInput] = useState(""); // Input distance as string for safe handling
  const [elevationRange, setElevationRange] = useState("0-200");
  const [poiMin, setPoiMin] = useState(0);
  const [priorityFactor, setPriorityFactor] = useState("elevation");
  const [distance, setDistance] = useState(null); // null indicates no distance initially
  const [elevationChange, setElevationChange] = useState(null);
  const [poiCount, setPoiCount] = useState(null);
  const [pathData, setPathData] = useState([]);
  const [startPlace, setStartPlace] = useState("");
  const [endPlace, setEndPlace] = useState("");
  const [startCoords, setStartCoords] = useState(null);
  const [endCoords, setEndCoords] = useState(null);
  const [startOptions, setStartOptions] = useState([]);
  const [endOptions, setEndOptions] = useState([]);
  const [poiNodes, setPoiNodes] = useState([]);

  const fetchPlaceSuggestions = async (input, setOptions) => {
    if (!input || input.trim() === "") {
      setOptions([]);
      return;
    }

    const url = `${BACKEND_BASE_URL}/proxy/google_places?input=${encodeURIComponent(
      input
    )}`;

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch suggestions");
      const data = await response.json();

      if (data.status === "OK") {
        const options = data.predictions.map((place) => ({
          label: place.description,
          placeId: place.place_id,
        }));
        setOptions(options);
      } else {
        console.error("Google API Error:", data.error_message);
        setOptions([]);
      }
    } catch (error) {
      console.error("Error fetching place suggestions:", error);
      setOptions([]);
    }
  };

  const fetchCoordinatesFromPlaceId = async (placeId) => {
    const url = `${BACKEND_BASE_URL}/proxy/google_geocode?place_id=${placeId}`;
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch coordinates");
      const data = await response.json();
      if (data.status === "OK") {
        const location = data.results[0].geometry.location;
        return { lat: location.lat, lng: location.lng };
      } else {
        console.error("Google Geocode API Error:", data.error_message);
        return null;
      }
    } catch (error) {
      console.error("Error fetching coordinates:", error);
      return null;
    }
  };

  const calculateRoute = async () => {
    const inputDistance = parseFloat(distanceInput);
    if (isNaN(inputDistance) || inputDistance <= 0) {
      alert("Please enter a valid distance in km.");
      return;
    }

    if (!startCoords || !endCoords) {
      alert("Please select valid start and end places.");
      return;
    }

    try {
      const response = await fetch(`${BACKEND_BASE_URL}/route`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: [startCoords.lat, startCoords.lng],
          target: [endCoords.lat, endCoords.lng],
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
        <Autocomplete
          options={startOptions}
          getOptionLabel={(option) => option.label}
          onInputChange={(e, value) => {
            setStartPlace(value);
            fetchPlaceSuggestions(value, setStartOptions);
          }}
          onChange={async (e, value) => {
            if (value) {
              const coords = await fetchCoordinatesFromPlaceId(value.placeId);
              setStartCoords(coords);
            } else {
              setStartCoords(null);
            }
          }}
          renderInput={(params) => (
            <TextField {...params} label="Start Place" variant="outlined" />
          )}
          sx={{ mb: 2 }}
        />

        <Autocomplete
          options={endOptions}
          getOptionLabel={(option) => option.label}
          onInputChange={(e, value) => {
            setEndPlace(value);
            fetchPlaceSuggestions(value, setEndOptions);
          }}
          onChange={async (e, value) => {
            if (value) {
              const coords = await fetchCoordinatesFromPlaceId(value.placeId);
              setEndCoords(coords);
            } else {
              setEndCoords(null);
            }
          }}
          renderInput={(params) => (
            <TextField {...params} label="End Place" variant="outlined" />
          )}
          sx={{ mb: 2 }}
        />

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
          onChange={(e) => setPoiMin(parseInt(e.target.value, 10) || 0)}
          sx={{ mb: 2 }}
        />

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
          <Typography variant="body1">Distance: {distance || "N/A"}</Typography>
          <Typography variant="body1">
            Elevation Change: {elevationChange || "N/A"}
          </Typography>
          <Typography variant="body1">POI Count: {poiCount || "N/A"}</Typography>
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
        {startCoords && (
          <Marker position={[startCoords.lat, startCoords.lng]}>
            <Popup>
              Start Point <br /> {startPlace}
            </Popup>
          </Marker>
        )}

        {endCoords && (
          <Marker position={[endCoords.lat, endCoords.lng]}>
            <Popup>
              End Point <br /> {endPlace}
            </Popup>
          </Marker>
        )}

        {poiNodes.map((poi, index) => (
          <Marker key={index} position={poi.coordinates}>
            <Popup>{poi.description || `POI ${index + 1}`}</Popup>
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
      </MapContainer>
    </div>
  );
}

export default App;
