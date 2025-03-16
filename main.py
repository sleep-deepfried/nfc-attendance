import serial
import csv
import datetime
import time
import os

# Configuration
PORT = "COM10"  # Change this to your Arduino's port
BAUD_RATE = 115200
CSV_FILE = "attendance.csv"

# Student database
students = (
    {}
)  # Will store {card_id: {"name": name, "grade": grade, "section": section, "present": bool}}


# Load existing students from CSV if it exists
def load_students():
    if os.path.exists("students.csv"):
        with open("students.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 4:
                    card_id, name, grade, section = row[0], row[1], row[2], row[3]
                    students[card_id] = {
                        "name": name,
                        "grade": grade,
                        "section": section,
                        "present": False,
                        "time_in": None,
                    }
    print(f"Loaded {len(students)} students from database")


# Save attendance record
def save_attendance(card_id, status, time_in=None):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Create file with header if it doesn't exist
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Date", "ID", "Name", "Grade", "Section", "TimeIn", "TimeOut"]
            )

    # Append attendance record
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if status == "IN":
            writer.writerow(
                [
                    date_str,
                    card_id,
                    students[card_id]["name"],
                    students[card_id]["grade"],
                    students[card_id]["section"],
                    time_str,
                    "",
                ]
            )
        else:  # OUT
            writer.writerow(
                [
                    date_str,
                    card_id,
                    students[card_id]["name"],
                    students[card_id]["grade"],
                    students[card_id]["section"],
                    time_in.strftime("%H:%M:%S"),
                    time_str,
                ]
            )


# Process commands
def process_command(cmd):
    cmd = cmd.strip()

    if cmd.startswith("reg "):
        parts = cmd.split(" ", 4)
        if len(parts) >= 4:
            card_id = parts[1]
            name = parts[2]
            grade = parts[3]
            section = parts[4] if len(parts) > 4 else ""

            students[card_id] = {
                "name": name,
                "grade": grade,
                "section": section,
                "present": False,
                "time_in": None,
            }

            # Save to students.csv
            with open("students.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([card_id, name, grade, section])

            print(f"Registered student: {name}")
        else:
            print("Invalid format. Use: reg [ID] [Name] [Grade] [Section]")

    elif cmd == "list":
        print("\nStudent List:")
        print("ID, Name, Grade, Section")
        for card_id, data in students.items():
            print(f"{card_id}, {data['name']}, {data['grade']}, {data['section']}")
        print()

    elif cmd == "help":
        print("\nCommands:")
        print("reg [ID] [Name] [Grade] [Section] - Register a student")
        print("list - List all registered students")
        print("help - Show this help")
        print("exit - Exit the program\n")

    elif cmd == "exit":
        return False

    return True


# Main function
def main():
    # Create students.csv if it doesn't exist
    if not os.path.exists("students.csv"):
        with open("students.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Grade", "Section"])

    # Load students database
    load_students()

    # Connect to Arduino
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {PORT}")
        time.sleep(2)  # Wait for Arduino to initialize
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        return

    print("RFID Attendance System")
    print("Type 'help' for commands")

    running = True
    while running:
        # Check for Arduino data
        if ser.in_waiting > 0:
            try:
                data = ser.readline().decode("utf-8").strip()
                if (
                    data
                    and not data.startswith("RFID")
                    and not data.startswith("Module")
                    and not data.startswith("Connection")
                ):
                    # Process RFID tag
                    if data in students:
                        # Student exists in database
                        if not students[data]["present"]:
                            # Time in
                            now = datetime.datetime.now()
                            students[data]["present"] = True
                            students[data]["time_in"] = now
                            save_attendance(data, "IN")
                            print(
                                f"IN: {students[data]['name']} at {now.strftime('%H:%M:%S')}"
                            )
                        else:
                            # Time out
                            now = datetime.datetime.now()
                            time_in = students[data]["time_in"]
                            students[data]["present"] = False
                            save_attendance(data, "OUT", time_in)
                            print(
                                f"OUT: {students[data]['name']} at {now.strftime('%H:%M:%S')}"
                            )
                    else:
                        # Unknown card
                        print(f"Unknown card: {data}")
                        print(
                            "Type 'reg "
                            + data
                            + " [Name] [Grade] [Section]' to register"
                        )
            except Exception as e:
                print(f"Error processing data: {e}")

        # Check for user input
        if not running:
            break

        # Non-blocking input check
        try:
            import msvcrt

            if msvcrt.kbhit():
                line = input()
                running = process_command(line)
        except ImportError:
            # For non-Windows platforms
            import select

            if select.select([sys.stdin], [], [], 0)[0]:
                line = input()
                running = process_command(line)

    # Close serial connection
    ser.close()
    print("Program ended")


if __name__ == "__main__":
    main()
