# RFID Attendance System

A simple and efficient RFID-based attendance tracking system using Arduino and Python. This system allows for tracking student attendance by scanning RFID cards and storing the data in CSV format on a computer.

## System Architecture

The system consists of two main components:

1. **Arduino with PN532 NFC/RFID Module**: Reads RFID cards and sends the card IDs to the computer.
2. **Python Script**: Receives the card IDs, processes attendance data, and stores records in CSV files.

## Hardware Requirements

- Arduino board (Uno, Nano, Mega, etc.)
- PN532 NFC/RFID Module
- Jumper wires
- USB cable for Arduino-to-PC connection

## Wiring Instructions

Connect the PN532 module to Arduino using SoftwareSerial:

| PN532 Pin | Arduino Pin |
|-----------|-------------|
| VCC       | 3.3V        |
| GND       | GND         |
| TXD       | Digital Pin 2 (RX) |
| RXD       | Digital Pin 3 (TX) |

Make sure the module is set to UART mode if it has jumpers/switches for selecting the communication mode.

## Software Setup

### Arduino Setup

1. Install the following libraries in the Arduino IDE:
   - SoftwareSerial (included with Arduino)
   - PN532 library (can be installed via Library Manager)

2. Upload the provided Arduino sketch to your board.

### Python Setup with Virtual Environment

1. Create a virtual environment:
   ```
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```

3. Install the required Python packages:
   ```
   pip install pyserial
   ```

4. Run the Python script:
   ```
   python attendance_system.py
   ```

5. To deactivate the virtual environment when done:
   ```
   deactivate
   ```

## Usage Instructions

### Initial Setup

1. Connect the Arduino to your computer and ensure the PN532 module is properly connected.
2. Upload the Arduino sketch.
3. Activate your virtual environment (`.venv`).
4. Run the Python script.
5. Wait for the "Connected to Arduino" message.

### Registering Students

To register students in the system:

1. Scan an unregistered RFID card.
2. When the "Unknown card" message appears, register the student using:
   ```
   reg [Card_ID] [Name] [Grade] [Section]
   ```
   Example: `reg 45.128.67.89 JohnDoe 10 A`

### Taking Attendance

1. When a registered student scans their card for the first time in a session, the system records a "Time In" entry.
2. When the same student scans their card again, the system records a "Time Out" entry.
3. All attendance data is automatically saved to `attendance.csv`.

### Available Commands

- `reg [ID] [Name] [Grade] [Section]` - Register a new student
- `list` - Display all registered students
- `help` - Show available commands
- `exit` - Exit the program

## Data Storage

The system uses two CSV files:

1. **students.csv**: Database of all registered students with their details.
   - Columns: ID, Name, Grade, Section

2. **attendance.csv**: Record of all attendance events.
   - Columns: Date, ID, Name, Grade, Section, TimeIn, TimeOut

## Troubleshooting

### PN532 Module Not Detected

If the Arduino cannot detect the PN532 module:

1. Check all wiring connections.
2. Ensure the module is powered correctly (3.3V for most modules).
3. Verify the module is in UART mode if it has mode jumpers.
4. Try power cycling both the Arduino and the module.
5. The code includes multiple connection attempts - wait for all attempts to complete.

### Serial Communication Issues

If the Python script cannot communicate with Arduino:

1. Check that the correct COM port is selected in the Python script.
2. Ensure no other programs are using the same COM port.
3. Verify the baud rate matches in both the Arduino sketch and Python script (115200).

### Virtual Environment Issues

If you encounter issues with the virtual environment:

1. Make sure you've activated the virtual environment before running the script.
2. If packages are missing, verify they were installed while the virtual environment was active.
3. If the virtual environment becomes corrupted, you can remove the `.venv` directory and recreate it.

## Extending the System

This system can be extended with additional features:

- Add a real-time clock (RTC) module to Arduino for more accurate timekeeping.
- Include an LCD display to show feedback when scanning cards.
- Implement a more advanced database system instead of CSV files.
- Create a web interface to view attendance records.

## License

This project is open-source and free to use for educational purposes.