# Running Routes for Out-of-Towners

Running Routes for Out-of-Towners is a web-based application designed to help runners visiting a new city find the perfect route based on their preferences for **distance**, **elevation**, and **points of interest (POIs)**. Whether you’re looking to challenge yourself with elevation changes or simply enjoy scenic landmarks while staying active, this tool creates a route tailored just for you.

## Features

- **Custom Route Planning**: Generates running routes based on user-defined distance and preferences.

- **Elevation and POI Preferences**:
  - Elevation range selection.
  - Minimum POI requirement.
  - Priority factor selection (elevation vs POIs).

---

## Technologies Used

### Backend:
- **Python**: Core backend language.
- **Flask**: Backend web framework.
- **SQLAlchemy**: Database ORM for querying nodes and edges.
- **PostgreSQL with PostGIS**: Spatial database for geospatial data.
- **NetworkX**: Graph library for pathfinding and graph operations.

### Frontend:
- **React**: Frontend framework.
- **Material-UI**: For UI components.
- **Leaflet**: Interactive maps.

---

## Project Structure

### Backend (`route-api/`):
- **`app.py`**: Flask application, routes, and Google API proxies.
- **`BiDirectionalAStar.py`**: Implementation of Bi-Directional A* algorithm to generate routes that meet the distance constraint.
- **`controller/`**: Database query functions for nodes and edges.
- **`database/db.py`**: SQLAlchemy database instance.
- **`model/models.py`**: SQLAlchemy models for nodes and edges.
- **`create_graph.py`**: Graph creation and caching logic using NetworkX.

### Frontend (`route-frontend/`):
- **`src/App.js`**: Main React application with interactive map and user inputs.
- **`src/components/`**: Components for user interaction and result visualization.

---

## Installation

### Prerequisites
- Python 3.8+
- Node.js and npm
- PostgreSQL with PostGIS extension

### Backend Setup
1. Clone the repository and navigate to the `route-api/` directory:
   ```bash
   git clone <repository-url>
   cd route-api
