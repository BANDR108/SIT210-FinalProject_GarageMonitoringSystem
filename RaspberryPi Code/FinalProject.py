from flask import Flask, request
from tkinter import Tk, Label, StringVar, Button
import threading
import os
import signal
import requests

app = Flask(__name__)

root = Tk()
root.title("Environment Monitor")

# Create StringVar for each measurement
temp_var = StringVar()
temp_var.set("Temperature: 0°C")

co2_var = StringVar()
co2_var.set("CO2: 0 ppm")

tvoc_var = StringVar()
tvoc_var.set("TVOC: 0 ppb")

sound_var = StringVar()
sound_var.set("Sound Level: 0")

# Create Labels for each measurement
temp_label = Label(root, textvariable=temp_var, font=("Helvetica", 24), width=30)
temp_label.pack(padx=20, pady=10)

co2_label = Label(root, textvariable=co2_var, font=("Helvetica", 24), width=30)
co2_label.pack(padx=20, pady=10)

tvoc_label = Label(root, textvariable=tvoc_var, font=("Helvetica", 24), width=30)
tvoc_label.pack(padx=20, pady=10)

sound_label = Label(root, textvariable=sound_var, font=("Helvetica", 24), width=30)
sound_label.pack(padx=20, pady=10)

# IFTTT Configuration
IFTTT_KEY = 'bjzs_8SrDABrKpkewFMGQDUyKZLsXnTAWdj0IXlHhXU'  # Replace with your IFTTT Webhooks key
IFTTT_EVENT_NAME = 'environment_alert'

def send_ifttt_alert(message):
    url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT_NAME}/with/key/{IFTTT_KEY}"
    payload = {"value1": message}
    response = requests.post(url, json=payload)
    print(response.text)

def update_labels(temp, co2, tvoc, sound):
    temp_var.set(f"Temperature: {temp}°C")
    co2_var.set(f"CO2: {co2} ppm")
    tvoc_var.set(f"TVOC: {tvoc} ppb")
    sound_var.set(f"Sound Level: {sound}")

    alert_message = ""
    
    # Update background color based on temperature threshold
    temp_float = float(temp)
    if temp_float > 30:
        temp_label.config(bg="red")
    else:
        temp_label.config(bg="green")

    # Update background color based on CO2 levels
    co2_int = int(co2)
    if co2_int <= 1000:
        co2_label.config(bg="green")
    elif co2_int <= 2000:
        co2_label.config(bg="orange")
        alert_message += f"CO2 level is moderate: {co2} ppm. "
    elif co2_int <= 5000:
        co2_label.config(bg="red")
        alert_message += f"CO2 level is bad: {co2} ppm. "
    else:
        co2_label.config(bg="darkred")
        alert_message += f"CO2 level is hazardous: {co2} ppm. "

    # Update background color based on TVOC levels
    tvoc_int = int(tvoc)
    if tvoc_int < 300:
        tvoc_label.config(bg="green")
    elif tvoc_int <= 500:
        tvoc_label.config(bg="orange")
        alert_message += f"TVOC level is moderate: {tvoc} ppb. "
    else:
        tvoc_label.config(bg="red")
        alert_message += f"TVOC level is poor: {tvoc} ppb. "

    # Update background color based on sound levels
    sound_int = int(sound)
    if sound_int < 80:
        sound_label.config(bg="green")
    else:
        sound_label.config(bg="red")
        alert_message += f"Sound level is bad: {sound}. "

    # Check for high temperature and add to alert message if needed
    temp_float = float(temp)
    if temp_float > 28:
        alert_message += f"High temperature detected: {temp}°C. "

    # Send alert if any condition is met
    if alert_message:
        send_ifttt_alert(alert_message)

@app.route('/update', methods=['GET'])
def update():
    temp = request.args.get('temp')
    co2 = request.args.get('co2')
    tvoc = request.args.get('tvoc')
    sound = request.args.get('sound')
    if temp and co2 and tvoc and sound:
        threading.Thread(target=update_labels, args=(temp, co2, tvoc, sound)).start()
    return "Data received"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def stop_program():
    os.kill(os.getpid(), signal.SIGTERM)

stop_button = Button(root, text="Stop", command=stop_program, font=("Helvetica", 24), width=10, bg="red")
stop_button.pack(pady=20)

threading.Thread(target=run_flask).start()
root.mainloop()
