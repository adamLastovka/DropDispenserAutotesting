import json
import os
import subprocess
import pandas as pd
import serial
import time


def create_config(update_config, exposure_time, ISO, button_hold_time,capture_delay):
    config = {
        "update_config": update_config,
        "exposure_time": exposure_time,
        "ISO": ISO,
        "button_hold_time": button_hold_time,
        "capture_delay": capture_delay
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)


def run_autohotkey_script(script_path):
    subprocess.run([r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe", script_path])


def read_status():
    if os.path.exists('status.txt'):
        with open('status.txt', 'r') as f:
            status = f.read()
        os.remove('status.txt')  # Clean up the status file after reading
        return status
    return "No status file found"


def wait_for_log(port):
    log = port.readline().decode('utf-8').strip()

    while not log:
        log = port.readline().decode('utf-8').strip()

    print(log)
    return log

END = '\n\r'
OK = 'OK'
NAK = 'NAK'
dispenser = serial.Serial('COM7', 115200, timeout=1.5)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    testing_profile_path = 'TestProfileTemplate.xlsx'
    results_path = r''
    first_drop = True

    repeats = 5  # Repeats per test condition

    if first_drop:
        capture_delay = 1550
    else:
        capture_delay = 200

    # Read in testing profile
    df = pd.read_excel(testing_profile_path)
    num_runs = df.shape[0]

    # initialize logging arrays
    dispense_log = []
    capture_log = []
    images_log = []
    prev_total = 0
    for run in range(num_runs):
        print(f'------Run{int(run + 1):04}------')

        # Read in test configuration
        rise_time = df.loc[run, 'Rise Time']
        fall_time = df.loc[run, 'Fall Time']
        delay_time = df.loc[run, 'Delay Time']
        needle_lift = df.loc[run, 'Needle Lift']
        num_drops = df.loc[run, 'Num Drops']

        # Select appropriate camera settings
        if delay_time == 2:
            button_hold_time = 510
            exposure_time = "1/1000"
            ISO = "25600"
        elif delay_time == 0.2:
            button_hold_time = 200
            exposure_time = "1/10"
            ISO = "3200"

        # Write configuration file for camera interface script, dont select iso, exposure in gui (unreliable)
        create_config(False, exposure_time, ISO, button_hold_time, capture_delay)

        for repeat in range(repeats):
            # Run camera capture script - run before valve open for first drop capturing
            run_autohotkey_script('CaptureImages.ahk')

            # Send valve open command
            msg = f"VALVE:AOPEN:{int(rise_time * 100)},0,{int(fall_time * 100)},{int(needle_lift)},{int(num_drops)},{int(delay_time * 10)}" + END
            dispenser.write(bytes(msg, 'utf-8'))

            # Receive information
            log = wait_for_log(dispenser)
            if log == NAK:
                print(f"Failed to dispense at run: {run}")
            dispense_log.append(log)

            status = read_status()
            if status == 0:
                print(f"Failed to capture at run: {run}")
            capture_log.append(status)

            time.sleep(0.8)  # at least 6s for 5 photos to dl, 10s for first drop drying

        # Find number of saved images
        total_images = len(os.listdir(results_path))
        images_captured = total_images - prev_total

        # Wait longer in case image download isn't keeping up
        # if images_captured < 5:
        #     time.sleep(1)
        total_images = len(os.listdir(results_path))
        images_captured = total_images - prev_total
        images_log.append(images_captured)
        prev_total = total_images

        print(f"Captured {images_captured} images")

    df["Dispense Status"] = pd.Series(dispense_log)
    df["Capture Status"] = pd.Series(capture_log)
    df["Images Captured"] = pd.Series(images_log)

    # Print out img id list
    img_ids = []
    for i in range(len(images_log)):
        cum_sum = sum(images_log[0:i])
        img_ids.append(f"{cum_sum + 1}-{cum_sum + images_log[i]}")
    df["IMG IDS"] = pd.Series(img_ids)

    print("CAPTURE LOG")
    print(capture_log)

    print("IMAGES LOG")
    print(images_log)

    df.to_excel(testing_profile_path, index=False)
