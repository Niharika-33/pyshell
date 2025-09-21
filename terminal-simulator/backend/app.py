from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import psutil
import json
import shutil
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store command history
command_history = []

# List of all available commands for auto-completion
AVAILABLE_COMMANDS = [
    "clear", "pwd", "ls", "cd", "mkdir", "rm", "cpu", "memory", "processes", "help"
]

def execute_command(cmd):
    """Execute a command and return the output."""
    try:
        # Check for piping and redirection
        if "|" in cmd:
            return _parse_and_execute_complex_command(cmd, "|")
        if ">" in cmd:
            return _parse_and_execute_complex_command(cmd, ">")
        
        # Split command into executable and arguments
        cmd_parts = cmd.strip().split()
        if not cmd_parts:
            return {"output": "", "error": "Empty command"}
        
        executable = cmd_parts[0]
        
        # Handle built-in commands
        if executable == "clear":
            return {"output": "", "error": None}
        
        elif executable == "pwd":
            return {"output": os.getcwd(), "error": None}
        
        elif executable == "help":
            output = "Available commands:\n" + "\n".join(AVAILABLE_COMMANDS)
            return {"output": output, "error": None}

        elif executable == "ls":
            try:
                path = "."
                # Check for arguments like 'ls -l'
                args = [arg for arg in cmd_parts[1:] if not arg.startswith('-')]
                if args:
                    path = args[0]
                
                # Using subprocess to get detailed and formatted output
                result = subprocess.run(
                    ["ls", "-l", path], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                output = result.stdout
                error = result.stderr if result.stderr else None
                return {"output": output, "error": error}
            except Exception as e:
                return {"output": "", "error": f"ls: {str(e)}"}
        
        elif executable == "cd":
            if len(cmd_parts) < 2:
                return {"output": "", "error": "cd: missing argument"}
            
            path = cmd_parts[1]
            try:
                os.chdir(os.path.abspath(path))
                return {"output": "", "error": None}
            except Exception as e:
                return {"output": "", "error": f"cd: {str(e)}"}
        
        elif executable == "mkdir":
            if len(cmd_parts) < 2:
                return {"output": "", "error": "mkdir: missing operand"}
            
            try:
                os.makedirs(cmd_parts[1], exist_ok=True)
                return {"output": "", "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        elif executable == "rm":
            if len(cmd_parts) < 2:
                return {"output": "", "error": "rm: missing operand"}
            
            try:
                path = cmd_parts[1]
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                return {"output": "", "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        elif executable == "cpu":
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                output = f"CPU Usage: {cpu_percent}%"
                return {"output": output, "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        elif executable == "memory":
            try:
                memory = psutil.virtual_memory()
                output = f"Memory Usage: {memory.percent}%\nAvailable: {memory.available // (1024**2)} MB\nTotal: {memory.total // (1024**2)} MB"
                return {"output": output, "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        elif executable == "processes":
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'username']):
                    try:
                        processes.append(f"{proc.info['pid']:>6} {proc.info['name']:<20} {proc.info['username']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if not processes:
                    output = "No processes found"
                else:
                    output = "PID      NAME                 USER\n" + "\n".join(processes[:20])
                    if len(processes) > 20:
                        output += f"\n... and {len(processes) - 20} more"
                
                return {"output": output, "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        else:
            # Fallback for external commands
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                output = result.stdout
                error = result.stderr if result.stderr else None
                return {"output": output, "error": error}
            except subprocess.TimeoutExpired:
                return {"output": "", "error": "Command timed out"}
            except Exception as e:
                return {"output": "", "error": str(e)}
    
    except Exception as e:
        return {"output": "", "error": str(e)}

def _parse_and_execute_complex_command(cmd, operator):
    """Parses and executes commands with pipes or redirection."""
    parts = cmd.split(operator, 1)
    if len(parts) != 2:
        return {"output": "", "error": f"Invalid syntax for {operator}"}
    
    command1 = parts[0].strip()
    command2 = parts[1].strip()

    try:
        if operator == "|":
            # Execute the first command and capture its output
            proc1 = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Execute the second command, using the first's output as input
            proc2 = subprocess.Popen(command2, shell=True, stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc1.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
            stdout, stderr = proc2.communicate(timeout=10)
            return {"output": stdout, "error": stderr if stderr else None}
        
        elif operator == ">":
            # Execute the first command and capture its output
            result = subprocess.run(
                command1,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            # Write the output to a file
            filepath = command2
            with open(filepath, 'w') as f:
                f.write(result.stdout)
            
            return {"output": f"Output redirected to '{filepath}'.", "error": None}
        
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Command timed out"}
    except Exception as e:
        return {"output": "", "error": str(e)}

@app.route('/execute', methods=['POST'])
def handle_execute():
    """Handle command execution"""
    data = request.get_json()
    command = data.get('command', '')
    
    # Add to command history
    command_history.append({
        'command': command,
        'timestamp': datetime.now().isoformat()
    })
    
    # Execute the command
    result = execute_command(command)
    
    return jsonify(result)

@app.route('/history', methods=['GET'])
def get_history():
    """Get command history"""
    return jsonify({'history': command_history})

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear command history"""
    global command_history
    command_history = []
    return jsonify({'success': True})

@app.route('/suggestions', methods=['POST'])
def get_suggestions():
    """Get command suggestions for autocompletion."""
    data = request.get_json()
    partial_command = data.get('partial', '').lower()
    
    suggestions = [
        cmd for cmd in AVAILABLE_COMMANDS 
        if cmd.lower().startswith(partial_command)
    ]
    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
