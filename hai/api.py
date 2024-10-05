from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import socket
import json
# import sys
import os
import time

app = FastAPI()

# sys.stdout = open(os.devnull, 'w')


# Get the directory of the current script (this works both during development and when the script is packaged)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the config.json file
config_path = os.path.join(current_directory, 'config.json')

# Load the config.json file
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

class PLCRequest:
    def __init__(self, PLC_IP, PLC_PORT, REGISTER_CODE, NUM_DATA_POINTS, data=None) -> None:
        self.PLC_IP = PLC_IP
        self.PLC_PORT = int(PLC_PORT)
        self.REGISTER_CODE = int(REGISTER_CODE)
        self.NUM_DATA_POINTS = int(NUM_DATA_POINTS)
        self.data = data

    def format_read_command(self):
        IO_NUMBER = "01"  # Sub Header
        NETWORK_NUMBER = "FF"  # PC No
        MONITORING_TIMER = 10  # Timer setting, waits for 10s
        DEVICE_CODE = "4420"  # Device code for Data register
        
        start_register = format(self.REGISTER_CODE, '08X')
        num_data_points = format(self.NUM_DATA_POINTS, '02X')
        monitor_timer = format(MONITORING_TIMER, '04X')

        command = f"{IO_NUMBER}{NETWORK_NUMBER}{monitor_timer}{DEVICE_CODE}{start_register}{num_data_points}00"
        print("-- Send data: ", command, len(command))
        return command

    def format_write_command(self):
        IO_NUMBER = "03"  # Sub Header
        NETWORK_NUMBER = "FF"  # PC No
        MONITORING_TIMER = 10  # Waiting time
        DEVICE_CODE = "4420"  # Device code for Data register
        
        start_register = format(self.REGISTER_CODE, '08X')
        num_data_points_hex = format(self.NUM_DATA_POINTS, '02X')
        data_hex = ''.join(format(d, '04X') for d in self.data) if self.data else ''

        command = f"{IO_NUMBER}{NETWORK_NUMBER}{MONITORING_TIMER:04X}{DEVICE_CODE}{start_register}{num_data_points_hex}00{data_hex}"
        print("-- Gửi dữ liệu: ", command, len(command))
        return command

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_data():
    time.sleep(0.1)
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=config['start_address_read'], NUM_DATA_POINTS=50)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)  # Set a timeout to avoid blocking indefinitely
            command = plc_object.format_read_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
            print(f"Received response: {response}")

            # Process the received data
            data_section = response[4:]  # data starts from the 4th byte
            data_integers = []
            for i in range(0, len(data_section), 4):
                data_integer = int(data_section[i:i + 4], 16)
                if data_integer >= 0x8000:  # handle negative numbers
                    data_integer -= 0x10000
                data_integers.append(data_integer/100)

            return data_integers
    
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

def read_data0():
    time.sleep(0.1)
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=config['start_address_read']+50, NUM_DATA_POINTS=50)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)  # Set a timeout to avoid blocking indefinitely
            command = plc_object.format_read_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
            print(f"Received response: {response}")

            # Process the received data
            data_section = response[4:]  # data starts from the 4th byte
            data_integers = []
            for i in range(0, len(data_section), 4):
                data_integer = int(data_section[i:i + 4], 16)
                if data_integer >= 0x8000:  # handle negative numbers
                    data_integer -= 0x10000
                data_integers.append(data_integer/100)

            return data_integers
    
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

def check_data():
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=500, NUM_DATA_POINTS=1)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            command = plc_object.format_read_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
            print(f"Received response: {response}")

            # Process the received data
            data_section = response[4:]  # data starts from the 4th byte
            data_integers = []
            for i in range(0, len(data_section), 4):
                data_integer = int(data_section[i:i + 4], 16)
                if data_integer >= 0x8000:  # handle negative numbers
                    data_integer -= 0x10000
                data_integers.append(data_integer)

            return data_integers
    
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/read_data/")
def read_data1():
    data = read_data() + read_data0()
    list_first = [0] * 100
    return JSONResponse(content={"data":  data[config['read_from']-1000:config['read_to']-999]})

@app.get("/check_data/")
def check_data_1():
    return JSONResponse(content={"data": check_data()})


@app.get("/write_data/")
def write_data():
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=config['start_address_write'], NUM_DATA_POINTS=1, data=[0])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            command = plc_object.format_write_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))  # Send command
            print(f"Sent command to PLC: {command}")
            
            # Receive response from PLC
            response = sock.recv(1024)  # Limit size to 1024 bytes
            print(f"Received response: {response}")

        return JSONResponse(content={"data": 'Successful write'})
    
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
