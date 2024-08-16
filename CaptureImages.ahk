#Requires AutoHotkey v2
#Include _JXON.ahk

; Remote shooting process vars
; EOS M50
; ahk_class WindowsForms10.Window.8.app.0.e4c6c4_r8_ad1
; ahk_exe EOS Utility 3.exe
; ahk_pid 37232
; ahk_id 725596

; Control ClassNN identifiers
exposureControl := "WindowsForms10.Window.8.app.0.e4c6c4_r8_ad129"  ; Client	x: 73	y: 160	w: 120	h: 40
isoControl := "WindowsForms10.Window.8.app.0.e4c6c4_r8_ad131"  ; Client	x: 195	y: 203	w: 106	h: 40
captureButton := "WindowsForms10.Window.8.app.0.e4c6c4_r8_ad147"  ; Client	x: 220	y: 34	w: 60	h: 60

ExposureControlId_0_4 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad121"
ExposureControlId_1_15 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad129"
ExposureControlId_1_30 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad132"
ExposureControlId_1_100 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad137"
ExposureControlId_1_1000 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad147"
ExposureControlId_1_4000 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad153"

ISOControlId_800 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad111"
ISOControlId_1600 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad114"
ISOControlId_6400 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad120"
ISOControlId_10000 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad122"
ISOControlId_16000 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad124"
ISOControlId_25600 := "WindowsForms10.BUTTON.app.0.e4c6c4_r8_ad126"

; Set coordinate mode to Client
CoordMode "Mouse", "Client"
BlockInput("MouseMove")
SetDefaultMouseSpeed(0)
SetMouseDelay(-1)

statusFile := "status.txt"

^!k:: ; Esc
{
    ExitApp
}

WriteStatus(message) {
	message := String(message)
    file := FileOpen(statusFile, "w")
    if !file {
        MsgBox "Could not open status file for writing."
        return
    }
    file.Write(message "`n")
    file.Close()
}


SelectControl(controlId) {
    ControlFocus(controlId, "ahk_exe EOS Utility 3.exe")
    ControlClick(controlId, "ahk_exe EOS Utility 3.exe")
}

SetParameters(exposureTime, ISO) {
    ; Set Exposure Time
    click(73, 160)
    Sleep(400)
    ; Determine which control to click based on exposureTime
    switch exposureTime {
        case "0.4":
            SelectControl(ExposureControlId_0_4)
        case "1/15":
            SelectControl(ExposureControlId_1_15)
		case "1/30":
            SelectControl(ExposureControlId_1_30)
		case "1/100":
            SelectControl(ExposureControlId_1_100)
		case "1/1000":
            SelectControl(ExposureControlId_1_1000)
		case "1/400":
            SelectControl(ExposureControlId_1_4000)
        default:
            MsgBox("Unknown exposure time: " exposureTime)
            return
    }
	
	MsgBox("Exposure Set")
    
    ; Set ISO
    click(195, 203)
    Sleep(400)
    ; Determine which control to click based on ISO
    switch ISO {
        case 800:
            SelectControl(ISOControlId_800)
        case 1600:
            SelectControl(ISOControlId_1600)
		case 6400:
            SelectControl(ISOControlId_6400)
        case 10000:
            SelectControl(ISOControlId_10000)
		case 16000:
            SelectControl(ISOControlId_16000)
        case 25600:
            SelectControl(ISOControlId_25600)
        default:
            MsgBox("Unknown ISO: " ISO)
			status := 0
            return
    }
	
	MsgBox("ISO Set")
}

CaptureImages(button_hold_time, capture_delay) {
	MouseMove(240, 55)
	sleep(capture_delay)
		
	click(240,55,"down")
	sleep(button_hold_time)
	click(240,55,"up")
}

DisplayJSONData(config) {
	MyGui := Gui()
    MyGui.Add("Text", "x10 y10 w200 h20", "update_config: " String(config["update_config"]))
	MyGui.Add("Text", "x10 y40 w200 h20", "Exposure Time: " String(config["exposure_time"]))
	MyGui.Add("Text", "x10 y70 w200 h20", "ISO: " String(config["ISO"]))
	MyGui.Add("Text", "x10 y100 w200 h20", "button_hold_time: " String(config["button_hold_time"]))
    MyGui.Show
	}

status := 1

jsonString := FileRead("config.json")
config := jxon_load(&jsonString)
;DisplayJSONData(config)
update_config := config["update_config"]
exposureTime := config["exposure_time"]
ISO := config["ISO"]
button_hold_time := config["button_hold_time"]
capture_delay := config["capture_delay"]

while status = 1
{
	; Step 1: Select remote shooting window
	If WinExist("ahk_exe EOS Utility 3.exe") {
		WinActivate
		WinWaitActive
	} else {
		MsgBox "EOS Utility 3.exe window not found!"
		status := 0
		break
	}

	; Step 2: Import parameters from Python (read config file)
	if !FileExist("config.json") {
		MsgBox "Config file not found!"
		status := 0
		break
	}
	
	; Step 3: Set parameters in camera
	if update_config {
		SetParameters(exposureTime, ISO)
	}
	
	; Step 4: Capture photos
	CaptureImages(button_hold_time,capture_delay)
	
	;MsgBox "Images captured"
	Break
}

WriteStatus(status)

ExitApp ; Exit the script