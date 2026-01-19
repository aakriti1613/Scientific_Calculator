# MathMental Scientific Calculator

> A modern, keyboard-friendly scientific calculator with a Python-powered brain.

<p align="center">
  <img width="626" height="776" alt="image" src="https://github.com/user-attachments/assets/09c4df16-f5b1-4371-810a-80bbb9e510b0" />
  <img width="626" height="224" alt="image" src="https://github.com/user-attachments/assets/384440f1-d066-4654-9f25-24cc65e2324d" />
  <img width="628" height="245" alt="image" src="https://github.com/user-attachments/assets/eda85695-3787-41b1-af52-379d058afb12" />
</p>

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




