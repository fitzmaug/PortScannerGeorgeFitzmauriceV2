#!/usr/bin/env python - George Fitzmaurice port scanner version 3.1 with Tkinter GUI
# refactored and cleaned up comments in this version
# V3.1 updates:
#   - textBox scrolls as scan runs
#   - user can press <enter> in the GUI which is the same as hitting the scan button
#   - refactored to separate (to some degree) the GUI code from scanning code
#   - Cleaned up comments
#
# This python program will scan ports 1-1025 and report if they are open or closed.  Output is shown on the screen
# and also in the output file named GeorgeFitz_outfile.txt.  The output file is overwritten on each subsequent run.
#
# User enters a hostname and that host is scanned
#

import tkinter as tk
import socket
import subprocess
import platform
from datetime import datetime

#
# Create a function to format date time in the way we want it displayed
# m/d/y H:M:S
#


def formatDateTime(dateTime):
    return dateTime.strftime("%m/%d/%Y %H:%M:%S")


#
# function to update the GUI and write to an output file
#


def printAndWriteFile(fileToUse, stringToOutput):
    fileToUse.write(stringToOutput+"\n")
    textBox.insert(tk.END, stringToOutput+"\n")
    textBox.yview_pickplace("end")  # Insure that we autoscroll to the bottom of the text box as the scan runs
    window.update()  # This forces the UI to update as we write.



#
#  Check that a given host IP responds to ping
#


def checkHostPing(IP):
    status_text.set("Check that host responds....")
    window.update()
    # Determine system type - Windows needs ping -n and mac/linux need ping -n
    try:
        output = subprocess.check_output(
            "ping -{} 1 {}".format('n' if platform.system().lower() == "windows" else 'c', IP), shell=True)
    except Exception as e:
        return False

    return True


#
# Function to connect to a port on a given host and return if the port is open or closed.
#


def checkPort(hostName, portNum):
    s = socket.socket()
    s.settimeout(5)  # setting a 5 sec timeout so this completes faster
    try:
        s.connect((hostName, portNum))
    except Exception:
        return False
    else:
        return True

#
# Function to run the scan.   This handler is run when the user presses the scan button.
#


def handle_scan(event):
    status_text.set("")
    textBox.delete("1.0", tk.END)
    window.update()
    serverToScan = entry.get()
    #
    # Open the output file
    #
    outFile = open("GeorgeFitz_outfile.txt", "w")
    window.update()  # Make sure the GUI is up to date as we start the scan - Cleans up from prior scan

    if serverToScan.isspace() or serverToScan == "":
        printAndWriteFile(outFile, "You entered a blank server name")
        status_text.set("You Entered a blank server name, Please Try again")
    #
    #   If the server name is not blank lets see if it is good or not
    #
    else:
        try:
            serverToScanIP = socket.gethostbyname(serverToScan)
        except Exception:
            printAndWriteFile(outFile, "The host named: " + serverToScan + " could not be found")
            status_text.set("The host named: " + serverToScan + " could not be found, Please Try another host")
            return
        #
        #   Now we have a resolved IP.  Check that the IP is responding.
        #
        if not checkHostPing(serverToScanIP):
            printAndWriteFile(outFile, "Host IP : " + serverToScanIP + " is not responding")
            status_text.set("Host IP : " + serverToScanIP + " is not responding, please try another host")
            return
        #
        # We have a resolved and responding IP - Lets scan.
        #
        status_text.set("Scanning underway...")
        #
        # Display in GUI and write to outfile a banner with information on which host we are about to scan
        #
        printAndWriteFile(outFile, "=" * 60)
        printAndWriteFile(outFile, "Please wait, scanning remote host: " + serverToScan + " IP: " + serverToScanIP)
        printAndWriteFile(outFile, "=" * 60)
        #
        # Get Scan Start Time and write it to outFile and display in GUI
        #
        startTime = datetime.now()
        printAndWriteFile(outFile, "=" * 60)
        printAndWriteFile(outFile, "Scan Start time: " + formatDateTime(startTime))
        printAndWriteFile(outFile, "=" * 60)
        #
        # Do the Scan - go from 1 to 1026 to insure we get port 1025
        #
        for port in range(1, 1026):
            portOpen = checkPort(serverToScanIP, port)
            if portOpen:
                printAndWriteFile(outFile, "Port: " + str(port) + "  Is Open")
            else:
                printAndWriteFile(outFile, "Port: " + str(port) + "  Is Closed")

        status_text.set("Scan Complete")
        #
        # Get End Scan Time
        #
        endTime = datetime.now()
        #
        # Calculate elapsed time
        #
        elapsedTime = endTime - startTime

        #
        # Display on GUI and write to outFile banner with end time and elapsed time
        #
        printAndWriteFile(outFile, "=" * 60)
        printAndWriteFile(outFile, "Scanning Complete at : " + formatDateTime(endTime) + "\nElapsed Scan Time: " +
                          str(elapsedTime))

        printAndWriteFile(outFile, "=" * 60)
        #
        # Close the output file
        #
        outFile.close()


#
#  Create GUI and main loop
#
#  Create the main window
#
#

window = tk.Tk()
window.bind("<Return>", handle_scan)  # If the user hits enter in the GUI assume they want to scan

#
#  Create the top label that simply shows what the application does
#


label = tk.Label(
    text="Port Scanner - Enter a Hostname and press Scan",
    fg="white",
    bg="black",
    width=100,
    height=1
)
label.pack()  # pack method adds this object to the window and organizes it in the default way.


#
#  Status bar text variable - used to update status
#


status_text = tk.StringVar()  # tk string var used to set status text in the status bar
statusWin = tk.Label(window,
                     textvariable=status_text,
                     fg="red",
                     bg="white",
                     width=100,
                     height=1)
statusWin.pack()  # pack method adds this object to the window and organizes it in the default way.


#
#  Create input field for hostName
#


entry = tk.Entry(fg="black", bg="white", width=100)
entry.pack()  # pack method adds this object to the window and organizes it in the default way.


#
# Create button to start scan
#


buttonScan = tk.Button(
    text="Scan",
    width=5,
    height=1,
    bg="white",
    fg="green",
)
buttonScan.bind("<Return>", handle_scan)  # If the user hits enter in the GUI assume they want to scan
buttonScan.bind("<Button-1>", handle_scan)  # Pressing the scan button runs the scan
buttonScan.pack()   # pack method adds this object to the window and organizes it in the default way.


#
# Create button to quit
#


def handle_quit(event):
    exit()


buttonQuit = tk.Button(
    text="Quit",
    width=5,
    height=1,
    bg="white",
    fg="red",
)
buttonQuit.bind("<Button-1>", handle_quit)
buttonQuit.pack()  # pack method adds this object to the window and organizes it in the default way.


#
# Text box for output - We display the output of the scan in this textbox
#


textBox = tk.Text(bg="gray90", bd=3, width=100)
textBox.pack()  # pack method adds this object to the window and organizes it in the default way.


#
#  Start Main loop - This starts the event loop handler of tkinter and shows the GUI.   All actions
#  in the GUI application happen from within this call.
#


window.mainloop()
