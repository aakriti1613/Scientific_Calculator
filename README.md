# MathMental Scientific Calculator

> A modern, keyboard-friendly scientific calculator with a Python-powered brain.

<p align="center">
  <img src="docs/screenshots/screenshot-01.png" alt="UI Screenshot – Desktop layout placeholder" width="260" />
  <img src="docs/screenshots/screenshot-02.png" alt="UI Screenshot – Scientific functions placeholder" width="260" />
  <img src="docs/screenshots/screenshot-03.png" alt="UI Screenshot – Mobile view placeholder" width="260" />
</p>
<p align="center"><em>Replace the three placeholders above with your actual UI captures.</em></p>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Run the App](#run-the-app)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Roadmap & Ideas](#roadmap--ideas)
- [Contributing](#contributing)

## Overview

MathMental pairs a responsive Bootstrap front end with a Flask + SymPy service that evaluates expressions, toggles between degree and radian modes, and keeps the UI feeling instant. The calculator works offline once dependencies are installed—just open the HTML file while the backend server is running.

## Features

- 🎨 Glassmorphism-inspired UI with responsive navbar and layout.
- 🧮 60+ scientific operations, inverse trig, factorial, powers, and hyperbolics.
- 🔁 Degree ↔ Radian toggle synchronized between client and server.
- ⌨️ Full keyboard support and smart input helpers.
- 📋 One-click copy of the latest evaluated result.
- 🔌 REST API endpoints ready to integrate into other math tools.

## Tech Stack

- Frontend: HTML5, Bootstrap 5, Font Awesome 6, custom CSS.
- Interactivity: Vanilla JavaScript + jQuery helper methods.
- Backend: Python 3, Flask, Flask-CORS, SymPy, standard math utilities.

## Project Structure

```
.
├── Calcy.html        # Entry point for the UI
├── Calcy.css         # Styling extracted from the original inline styles
├── Calcy.js          # Calculator logic and event wiring
├── backend.py        # Flask API for calculation + mode handling
└── vendor/           # Optional local copies of Bootstrap & Font Awesome assets
```

## Getting Started

### Prerequisites

- Python 3.9+ (SymPy and Flask run best on recent versions).
- pip (bundled with most Python installs).

### Installation

1. Clone or download this repository to your machine.
2. (Optional) Create and activate a virtual environment.
3. Install backend dependencies:

   ```bash
   pip install flask flask-cors sympy
   ```

### Run the App

1. **Start the backend:**

   ```bash
   python backend.py
   ```

   The Flask server listens on `http://127.0.0.1:5000`.

2. **Open the frontend:**
   - Double-click `Calcy.html`, or
   - Serve the directory with any static server and visit `/Calcy.html`.

The calculator will now communicate with the backend for all evaluations and mode switches.

## Keyboard Shortcuts

- `0-9`, `.` : enter numbers quickly.
- `+`, `-`, `*`, `/`, `^`, `%` : arithmetic operators.
- `Enter` or `=` : evaluate the current expression.
- `Backspace` : delete the last character.
- `Delete` or `Esc` : clear everything.
- `s`, `o`, `t`, `l`, `g`, `p`, `e` : insert `sin(`, `cos(`, `tan(`, `ln(`, `log(`, `π`, `e`.

## API Endpoints

| Method | Endpoint       | Description                         |
| ------ | -------------- | ----------------------------------- |
| POST   | `/calculate`   | Evaluate an expression.             |
| POST   | `/mode`        | Switch between `deg` and `rad`.     |

**Sample payload** for `/calculate`:

```json
{
  "expression": "sin(45) + log(10)"
}
```

## Troubleshooting

- **CORS errors:** Ensure `backend.py` is running; it enables CORS for local use.
- **SymPy missing:** Re-run `pip install sympy`.
- **Nothing happens on button press:** Check browser console; the backend must be reachable at `http://127.0.0.1:5000`.

## Roadmap & Ideas

- Graphing mode for plotted expressions.
- History panel with export/share options.
- Dark/light theming toggle driven by CSS variables.
- Progressive Web App (PWA) packaging.

## Contributing

1. Fork the project and create a feature branch.
2. Make your changes, following the existing code style.
3. Document updates in this README if they affect usage.
4. Open a pull request describing your improvements.

---

Need assets for the gallery above? Create `docs/screenshots/` and drop three `.png` files named `screenshot-01.png`, `screenshot-02.png`, and `screenshot-03.png`—they will render automatically in the header.

