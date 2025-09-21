import os
import subprocess
import shutil
import psutil
from datetime import datetime
import json
import shlex
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Store command history
command_history = []

# List of built-in commands
BUILT_IN_COMMANDS = [
    'ls', 'cd', 'pwd', 'mkdir', 'rm', 'cpu', 'memory', 'processes', 'clear', 'cat'
]

def parse_and_execute(cmd_str):
    """
    Parse a command string with pipes and redirections and execute it.
    This function handles the core logic of the terminal.
    """
    try:
        # Check for pipes
        if '|' in cmd_str:
            commands = cmd_str.split('|')
            input_data = None
            for i, cmd in enumerate(commands):
                cmd_parts = shlex.split(cmd.strip())
                if not cmd_parts:
                    return {"output": "", "error": "Invalid command in pipe"}

                if i == len(commands) - 1 and '>' in cmd:
                    # Handle redirection in the last command of a pipe
                    cmd_to_redirect, filename = cmd.split('>')
                    cmd_parts_to_redirect = shlex.split(cmd_to_redirect.strip())
                    try:
                        result = subprocess.run(
                            cmd_parts_to_redirect,
                            input=input_data,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        with open(filename.strip(), 'w') as f:
                            f.write(result.stdout)
                        return {"output": f"Output redirected to '{filename.strip()}'", "error": None}
                    except FileNotFoundError:
                        return {"output": "", "error": f"Command not found: '{cmd_parts_to_redirect[0]}'" }
                    except subprocess.TimeoutExpired:
                        return {"output": "", "error": "Command timed out" }
                    except Exception as e:
                        return {"output": "", "error": str(e) }
                else:
                    try:
                        result = subprocess.run(
                            cmd_parts,
                            input=input_data,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        input_data = result.stdout
                        if result.returncode != 0 and result.stderr:
                             return {"output": "", "error": result.stderr}
                    except FileNotFoundError:
                        return {"output": "", "error": f"Command not found: '{cmd_parts[0]}'" }
                    except subprocess.TimeoutExpired:
                        return {"output": "", "error": "Command timed out" }
                    except Exception as e:
                        return {"output": "", "error": str(e) }
            return {"output": input_data, "error": None}

        # Check for redirection
        elif '>' in cmd_str:
            cmd, filename = cmd_str.split('>')
            cmd_parts = shlex.split(cmd.strip())
            if not cmd_parts:
                return {"output": "", "error": "Invalid command for redirection"}
            
            try:
                result = subprocess.run(
                    cmd_parts, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                with open(filename.strip(), 'w') as f:
                    f.write(result.stdout)
                
                return {"output": f"Output redirected to '{filename.strip()}'", "error": None}
            except FileNotFoundError:
                return {"output": "", "error": f"Command not found: '{cmd_parts[0]}'" }
            except subprocess.TimeoutExpired:
                return {"output": "", "error": "Command timed out" }
            except Exception as e:
                return {"output": "", "error": str(e) }
        
        # Standard command
        else:
            cmd_parts = shlex.split(cmd_str)
            try:
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                output = result.stdout
                error = result.stderr if result.stderr else None
                return {"output": output, "error": error}
            except FileNotFoundError:
                return {"output": "", "error": f"Command not found: '{cmd_parts[0]}'" }
            except subprocess.TimeoutExpired:
                return {"output": "", "error": "Command timed out" }
            except Exception as e:
                return {"output": "", "error": str(e) }

    except Exception as e:
        return {"output": "", "error": str(e)}

def execute_command(cmd):
    """Execute a command and return the output"""
    try:
        # Split command into executable and arguments
        cmd_parts = shlex.split(cmd.strip())
        if not cmd_parts:
            return {"output": "", "error": "Empty command"}
        
        executable = cmd_parts[0]
        
        # Handle built-in commands
        if executable == "clear":
            return {"output": "", "error": None}
        
        elif executable == "pwd":
            return {"output": os.getcwd(), "error": None}
        
        elif executable == "ls":
            try:
                files = os.listdir(os.getcwd())
                # Add support for ls -l
                if '-l' in cmd_parts:
                    output_lines = []
                    for f in files:
                        stat = os.stat(f)
                        permissions = stat.st_mode
                        file_type = 'd' if os.path.isdir(f) else '-'
                        permissions_str = f"{file_type}{oct(permissions & 0o777)[2:]}"
                        size = stat.st_size
                        modified_time = datetime.fromtimestamp(stat.st_mtime).strftime('%b %d %H:%M')
                        output_lines.append(f"{permissions_str}\t{size}\t{modified_time}\t{f}")
                    output = "\n".join(output_lines)
                else:
                    output = "\n".join(files)
                return {"output": output, "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
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
                # Check for the -r flag and a path to handle recursive deletion
                if ('-r' in cmd_parts or '-R' in cmd_parts) and len(cmd_parts) >= 2:
                    path = cmd_parts[1]
                    shutil.rmtree(path)
                    return {"output": "", "error": None}
                
                path = cmd_parts[1]
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    return {"output": "", "error": "rm: cannot remove directory without -r flag"}
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
                    output = "PID      NAME                 USER\n" + "\n".join(processes[:20])  # Limit to 20 processes
                    if len(processes) > 20:
                        output += f"\n... and {len(processes) - 20} more"
                
                return {"output": output, "error": None}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        elif executable == "cat":
            if len(cmd_parts) < 2:
                return {"output": "", "error": "cat: missing operand"}
            try:
                with open(cmd_parts[1], 'r') as f:
                    output = f.read()
                return {"output": output, "error": None}
            except FileNotFoundError:
                return {"output": "", "error": f"cat: {cmd_parts[1]}: No such file or directory"}
            except Exception as e:
                return {"output": "", "error": str(e)}
        
        else:
            # Execute complex commands using the new parser
            return parse_and_execute(cmd)
    
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
    """Get command suggestions for autocomplete"""
    data = request.get_json()
    partial_command = data.get('partial', '').lower()
    
    suggestions = [cmd for cmd in BUILT_IN_COMMANDS if cmd.startswith(partial_command)]
    return jsonify({'suggestions': suggestions})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
