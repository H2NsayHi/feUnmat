from fastapi import FastAPI, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import socket
import json
import os
import time

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_directory, 'config.json')

# Load config
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
        return command

async def read_data():
    time.sleep(0.1)
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=config['start_address_read'], NUM_DATA_POINTS=50)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            command = plc_object.format_read_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
            data_section = response[4:]
            data_integers = []
            for i in range(0, len(data_section), 4):
                data_integer = int(data_section[i:i + 4], 16)
                if data_integer >= 0x8000:
                    data_integer -= 0x10000
                data_integers.append(data_integer / 100)
            return data_integers
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def read_data0():
    time.sleep(0.1)
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=config['start_address_read'] + 50, NUM_DATA_POINTS=50)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            command = plc_object.format_read_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
            data_section = response[4:]
            data_integers = []
            for i in range(0, len(data_section), 4):
                data_integer = int(data_section[i:i + 4], 16)
                if data_integer >= 0x8000:
                    data_integer -= 0x10000
                data_integers.append(data_integer / 100)
            return data_integers
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def write_data():
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=config['start_address_write'], NUM_DATA_POINTS=1, data=[0])
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            command = plc_object.format_write_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
        return JSONResponse(content={"data": 'Successful write'})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def check_data():
    plc_object = PLCRequest(PLC_IP=config['PLC_IP'], PLC_PORT=config['PLC_PORT'], REGISTER_CODE=500, NUM_DATA_POINTS=1)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            command = plc_object.format_read_command()
            sock.connect((config['PLC_IP'], config['PLC_PORT']))
            sock.sendall(command.encode("ascii"))
            response = sock.recv(1024)
            data_section = response[4:]
            data_integers = []
            for i in range(0, len(data_section), 4):
                data_integer = int(data_section[i:i + 4], 16)
                if data_integer >= 0x8000:
                    data_integer -= 0x10000
                data_integers.append(data_integer)
            return data_integers
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/read_data/")
async def read_data1():
    A = []
    if await check_data() == 1:
        data = await read_data() + await read_data0()
        A = data[config['read_from'] - 1000:config['read_to'] - 999]
        await write_data()
    return JSONResponse(content={"data": A})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
