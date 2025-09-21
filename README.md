Terminal Simulator

A web-based terminal simulator with a Python backend and Vue.js frontend.
Features

    Real-time terminal simulation

    File and directory operations (ls, cd, pwd, mkdir, rm)

    System monitoring commands (cpu, memory, processes)

    Command history navigation (arrow keys)

    Clear screen support

    Responsive terminal interface with Tailwind CSS and DaisyUI styling

Architecture
Backend (Python)

    Built with Flask

    Handles command execution and system operations

    Provides REST API for frontend communication

    Uses psutil for system monitoring

Frontend (Vue.js)

    Single-page application with Vue 3 and Vite

    Uses Axios for API communication

    Styled with Tailwind CSS and DaisyUI

    Terminal-like interface with command history

Setup Instructions
Prerequisites

    Python 3.7+

    Node.js 14+

Running the Backend

    Navigate to the backend directory:

    cd backend

    Install dependencies:

    pip install -r requirements.txt

    Run the backend server:

    python app.py

Running the Frontend

    Navigate to the frontend directory:

    cd frontend

    Install dependencies:

    npm install

    Run the frontend development server:

    npm run dev

Available Commands

    ls - List directory contents

    cd <directory> - Change directory

    pwd - Print working directory

    mkdir <directory> - Create directory

    rm <file/directory> - Remove file or directory

    cpu - Show CPU usage

    memory - Show memory usage

    processes - Show running processes

    clear - Clear terminal screen

Development

The application follows a clean separation of concerns:

    Backend handles all system operations and provides a REST API

    Frontend handles the UI and user interactions

    Communication happens via HTTP requests to the backend API

License

This project is licensed under the MIT License.

low level :
request -> parse -> execute components -> combine results -> respond model.
