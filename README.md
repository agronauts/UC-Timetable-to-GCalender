# UC-Timetable-to-GCalender
Converts the exported CSV file from the UC Timetable webapp into a less verbose format for importing into Google Calenders

# Requirements
Python 3 installed

# Installation
Download or clone the python script to a suitable location and you're ready to go

# Usage
1. In the UC Timetable web app, go:
    a. Timetable
    b. Export button (Looks like a square with an arrow protuding out the right side of it) 
    c. Text
2. Move the CSV file into the same directory as the python script.
3. From the command line, run `python UC_Timetable_GCalender.py filename` where `filename` is the name of the downloaded CSV file
4. In Google Calenders, go:
    a. Click the cog button in top right corner
    b. Settings
    c. Calenders
5. After that, go:
    a. Click the cog button in top right corner
    b. Settings
    c. Calenders
    d. Import Calender
    e. Choose file
    f. Select the CSV file that was made by the python script
    g. Select the calender you just made
    h. Import
    
Congratulations, you will now have a non-verbose looking University timetable that's integrated with all your other events!
