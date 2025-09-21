Terminal Simulator

A fully functional, web-based command-line terminal with a robust Python backend and a modern Vue.js frontend. This project replicates core terminal behaviors in a safe and secure web environment.
Features

    Core Command Execution: Handles standard file and directory operations like ls, cd, pwd, mkdir, and rm.

    System Monitoring: Integrates with the host system to display CPU, memory, and process information.

    Advanced Command Parsing: Securely handles complex commands with piping (|) and output redirection (>) without relying on the system shell.

    Intelligent Autocomplete: Provides dynamic, real-time command suggestions as you type.

    Command History: Navigate through previous commands using the up and down arrow keys.

    Themable UI: A clean, responsive interface with a toggle for light and dark themes.

Architecture
Backend (Python)

The backend is built with Flask and acts as a secure, stateless API. It is responsible for all low-level system interactions.

    Secure Execution: Commands are parsed with shlex and executed as lists of arguments to prevent shell injection vulnerabilities.

    REST API: Exposes endpoints for command execution and autocomplete suggestions.

    System Interaction: Uses built-in os and shutil modules for file operations and psutil for system monitoring.

Frontend (Vue.js)

The frontend is a single-page application built with Vue 3 and Vite, designed for a responsive and intuitive user experience.

    API Communication: Uses axios to send commands to the Python backend and display the output in real-time.

    Styling: Leverages Tailwind CSS for responsive design and a clean, consistent look. Custom CSS is used for unique effects like the blinking cursor.

    State Management: Manages application state, including command history, terminal output, and theme settings.

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

Development

The application is built on a clean separation of concerns, with the backend handling all logic and the frontend managing the user interface. This makes it easy to extend and maintain.
