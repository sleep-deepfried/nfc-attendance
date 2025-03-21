import csv
import datetime
import time
import os
import sys
import serial


# Beep sound function (Windows and Linux/macOS support)
def beep():
    try:
        if sys.platform == "win32":
            import winsound

            winsound.Beep(1000, 500)  # Frequency: 1000 Hz, Duration: 200 ms
        else:
            os.system("play -nq -t alsa synth 0.1 sine 1000")  # Requires sox package
    except Exception as e:
        print(f"Beep error: {e}")


# Configuration
PORT = "COM10"  # Change this to your Arduino's port
BAUD_RATE = 115200
CSV_FILE = "attendance.csv"

# Student database
students = {}


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

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Date", "ID", "Name", "Grade", "Section", "TimeIn", "TimeOut"]
            )

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
        else:
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


# Main function
def main():
    if not os.path.exists("students.csv"):
        with open("students.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Grade", "Section"])

    load_students()

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {PORT}")
        time.sleep(2)
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        return

    print("RFID Attendance System")
    print("Waiting for RFID scans...")

    while True:
        if ser.in_waiting > 0:
            try:
                data = ser.readline().decode("utf-8").strip()
                if data and not data.startswith(("RFID", "Module", "Connection")):
                    beep()  # Play beep sound when RFID is detected

                    if data in students:
                        if not students[data]["present"]:
                            now = datetime.datetime.now()
                            students[data]["present"] = True
                            students[data]["time_in"] = now
                            save_attendance(data, "IN")
                            print(
                                f"IN: {students[data]['name']} at {now.strftime('%H:%M:%S')}"
                            )
                        else:
                            now = datetime.datetime.now()
                            time_in = students[data]["time_in"]
                            students[data]["present"] = False
                            save_attendance(data, "OUT", time_in)
                            print(
                                f"OUT: {students[data]['name']} at {now.strftime('%H:%M:%S')}"
                            )
                    else:
                        print(f"Unknown card: {data}")
                        print(f"Type 'reg {data} [Name] [Grade] [Section]' to register")
            except Exception as e:
                print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()
