"""
Author: Patrick Nicholls
Date: 12/07/2016
Description: Takes the CSV output from the Uni timetable and processes it so
that it can be imported to GCalenders.
Todo:
    -Intelligent lecturer
    -Intelligent room
    -Google maps room
    -GUI
    -Webcal server
"""
import sys
from tkinter import *
import csv
import argparse
import re
from datetime import datetime, timedelta

G_EVENT_FIELDNAMES = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location'] 
DATE_INPUT_FORMAT="%d/%m/%Y"
DATE_OUTPUT_FORMAT="%m/%d/%Y"
TIME_INPUT_FORMAT="%I:%M %p"
TIME_OUTPUT_FORMAT="%H:%M"

#arguments parsing
def parse_args():
    """Parses arguments from command line"""
    parser = argparse.ArgumentParser(description='Determine mode of operation')
    parser.add_argument("source",  help="Source file from the UC timetable webapp")
    parser.add_argument("-d", "--dest", default="UC_GCalender.csv", help="Destination for output")
    return parser.parse_args()

"""
Returns dict of google event given the details of the event and a list of the date it
occurs on
"""
def make_g_event(UC_event, date):
    #Subject : The name of the event, required. : Example: Final exam
    #Start Date : The first day of the event, required. : Example: 05/30/2020
    #Start Time : The time the event begins. : Example: 10:00 AM
    #End Date : The last day of the event. : Example: 05/30/2020
    #End Time : The time the event ends. : Example: 1:00 PM
    #All Day Event : Whether the event is an all-day event. Enter True if it is an all-day event, and False if it isn't. : Example: False
    #Description : Description or notes about the event. : Example: 50 multiple choice questions and two essay questions 
    #Location : The location for the event. : Example: "Columbia, Schermerhorn 614"
    #Private : Whether the event should be marked private. Enter True if the event is private, and False if it isn't. : Example: True
    g_event = {}
    g_event['Subject'] =  UC_event['Group'] + ' ' + UC_event['Subject Code'].split('-')[0] 
    g_event['Start Date'] = date.strftime(DATE_OUTPUT_FORMAT)
    g_event['Start Time'] = parseStartTime(UC_event['Time'])
    g_event['End Date'] = date.strftime(DATE_OUTPUT_FORMAT)
    g_event['End Time'] = parseEndTime(UC_event['Time'], UC_event['Duration'])
    g_event['Description'] = "{} :: {}".format(UC_event['Description'], get_time_dep_item(UC_event, 'Staff', date))
    g_event['Location'] = get_time_dep_item(UC_event, 'Location', date)
    return g_event
    
def parseStartTime(t):
    dt = datetime.strptime(t, TIME_OUTPUT_FORMAT)
    return dt.strftime(TIME_INPUT_FORMAT)

def parseEndTime(t, d):
    dt = datetime.strptime(t, TIME_OUTPUT_FORMAT)
    dd = timedelta(hours=int(d[0]))
    dt = dt + dd
    return dt.strftime(TIME_INPUT_FORMAT)

def get_time_dep_item(UC_event, key, date):
    #Get durations
    #precess this hunk of shit
    item = ''
    lecSet = False
    for chunk in UC_event[key].split(' '):
        print(chunk)
        chunk = chunk.strip('/')
        if chunk == '-':
            return "No item"
        if chunk.find('/') == -1:
            if lecSet:
                lecSet = False
                item = chunk
            else:
                item += ' ' + chunk
        else:
            lecSet = True
            chunk = chunk.strip('(),')
            if len(chunk.split('-')) == 1:
                if date == datetime.strptime(chunk + '/2016', DATE_INPUT_FORMAT):
                    print('found')
                    return item
            else:
                start_d, end_d = chunk.split('-')
                start_d = datetime.strptime(start_d + '/2016', DATE_INPUT_FORMAT)
                end_d = datetime.strptime(end_d + '/2016', DATE_INPUT_FORMAT)
                if date > start_d and date < end_d:
                    print("found")
                    return item
    if item:
        return item
    return "No " + key
        
"""
Returns an array of Date objects that represent when a particular UC event
recurs on
"""
def get_dates(UC_event):
    #parse durations of course
    #Make weekly dates within duration
    dates = []
    for dur in UC_event['Dates'].split(', '):
        if (len(dur.split('-')) == 1):
            #On a single date Eg. test
            d = datetime.strptime(dur + '/2016', DATE_INPUT_FORMAT)
            dates.append(d)
        else:
            beg_d, end_d = dur.split('-')
            beg_d = datetime.strptime(beg_d + '/2016', DATE_INPUT_FORMAT)
            end_d = datetime.strptime(end_d + '/2016', DATE_INPUT_FORMAT)
            cur_d = beg_d
            dates.append(cur_d)
            cur_d = cur_d + timedelta(weeks=1)
            while cur_d <= end_d:
                dates.append(cur_d)
                cur_d = cur_d + timedelta(weeks=1)
    return dates


def gui_mode():
    class Application(Frame):
        def find_file(self):
            print("Finding file")
            #self.dest = filechooser
            self.g_events = process_UC_file(dest)

        def convert_file(self):
            write_file(self.dest, self.g_events)

        def createWidgets(self):
            self.b_file_chooser = Button(self)
            self.b_file_chooser["text"] = "Choose file"
            self.b_file_chooser["command"] = self.find_file
            self.b_file_chooser.pack({"side": "left"})

            self.b_converter = Button(self)
            self.b_converter["text"] = "Convert"
            self.b_converter["command"] = self.convert_file
            self.b_converter.pack({"side": "right"})

        def __init__(self, master=None):
            Frame.__init__(self, master)
            self.pack()
            self.createWidgets()

    root = Tk()
    app = Application(master=root)
    app.mainloop()
    root.destroy() 

def command_line_mode():
    args = parse_args()
    g_events = process_UC_file(args.source)
    write_file(args.dest, g_events)

def process_UC_file(src):
    #open file
    #Process into dictionary
    g_events = []
    with open(src) as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        for UC_event in reader:
            #WHere get teacher?
            for date in get_dates(UC_event):
                g_events.append(make_g_event(UC_event, date))
    return g_events

def write_file(dest, g_events):
    #Write CSV
    with open(dest, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=G_EVENT_FIELDNAMES)
        writer.writeheader()
        for g_event in g_events:
            writer.writerow(g_event)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command_line_mode()
    else:
        gui_mode()
