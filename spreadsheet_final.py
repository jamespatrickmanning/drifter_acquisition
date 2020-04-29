"""
spreadsheet.py
Created on June 19, 2019
Author: Dylan Montagu

Accesses drift_header.DRIFT_HEADER (google sheet) on the noaa.drifters@gmail.com account

getfix_gs_data grabs data necessary for getfix.py, and returns that data
as a dictionary

getfix_ap3_gs_data grabs data necessary for getfix_ap3.py, and returns that data
as a dictionary.

If program run directly, runs get_gs_data and getfix_ap3_gs_data, and prints
formatted for display version of the dictinoaries
noaa_drifter_crednetials.json needs to be in same directory as spreadsheet.py
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dateutil.parser import parse
import numpy as np


def getfix_gs_data(project_name):
    """
    Accesses data on drift_header.gs
    Gets raw data from the first 6 columns (id, esn, case_id, start_date, end_date, and drogue_depth),
    selects rows of the project name being worked on, and returns a dictionary with meta data of all
    entries in the project
    Returns a dictionary with
        keys =     id,      esn,   case_id,      start_date,              end_date,    drogue_depth
        values = <[int]>, <[int]>, <[int]>, [<datetime.datetime>], [<datetime.datetime>], <[int]>
    in: project_name <string>
    out: output_data <dict>
    """

    # set up google sheet access
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("noaa_drifter_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open('drift_header').get_worksheet(0) # specify which "tab"/worksheet accessed

    # access individual column data
    # col indexes start at 1, elts are returned as strings
    id = sheet.col_values(1)[1:]
    esn = sheet.col_values(2)[1:]
    case_id = sheet.col_values(3)[1:]
    start_date = sheet.col_values(4)[1:]
    end_date = sheet.col_values(5)[1:]
    drogue_depth = sheet.col_values(6)[1:]
    project_names = sheet.col_values(14)[1:]
    pi = sheet.col_values(16)[1:]
    communication = sheet.col_values(20)[1:]


    # clean data types
    for i in range(len(id)):
        #print case_id#[i]
        case_id[i] = int(case_id[i])
        start_date[i] = parse(start_date[i])
        end_date[i] = parse(end_date[i])

    # find indexes of rows of project that we want to get metadata for
    project_indexes = []
    for index, name in enumerate(project_names):
        if (name == project_name) and (communication[index] == "GLOBALSTAR"):
            project_indexes.append(index)

    # set up data and info for reformatting, and output as dicitonary
    all_data_raw = [id, esn, case_id, start_date, end_date, drogue_depth, project_names, pi]
    data_titles = ["id", "esn", "case_id", "start_date", "end_date", "drogue_depth", "project_names", "pi"]
    output_data = {}
    for index, col in enumerate(all_data_raw):
        col_data = []
        for row in (project_indexes): # only get data from rows of the project we're getting info from
            col_data.append(col[row])
        output_data[data_titles[index]] = col_data

    return output_data


def write_codes_file(data_dict):
    """ writes a .dat file sililar to codes.dat format
        to be used in newer version of drift2xml
    """
    esn = data_dict["esn"]
    ide = data_dict["id"]
    depth = data_dict["drogue_depth"]
    pi = data_dict["pi"]
    project = data_dict["project_names"]

    file_read = open("/net/data5/jmanning/drift/codes.dat","r")
    dat_ids=[]
    for line in file_read:
      dat_ids.append(line.split()[1])
    file_read.close()

    file = open("/net/data5/jmanning/drift/codes.dat", "a")
    for i in range(len(ide)):
        if ide[i] not in dat_ids:
            file.write(esn[i] + " " + ide[i] + " " + depth[i] + " " + pi[i] + " " + project[i] + "\n")

    file.close()



def getfix_ap3_gs_data():
    """
    ap3 version, same as getfix_gs_data but different subsect (columns)
    of data accesed and returned
    Accesses all rows that don't utilized GLOBALSTAR satellite communication links
    which should single out miniboats (hopefully)
    in: <>
    out: output_data <dict>
    """

    # set up google sheet access
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("noaa_drifter_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open('drift_header').get_worksheet(0) # specify which gs accessed

    # access individual column data
    id = sheet.col_values(1)[1:]
    esn = sheet.col_values(2)[1:]
    case_id = sheet.col_values(3)[1:]
    start_date_codes= sheet.col_values(4)[1:]
    end_date_codes = sheet.col_values(5)[1:]
    start_date= sheet.col_values(4)[1:]
    end_date = sheet.col_values(5)[1:]    drogue_depth = sheet.col_values(6)[1:]
    project_names = sheet.col_values(14)[1:]
    boat_pi = sheet.col_values(16)[1:]
    school = sheet.col_values(15)[1:]
    consecutive_batch = sheet.col_values(22)[1:]
    communication = sheet.col_values(20)[1:]

    # clean data types
    for i in range(len(id)):
        # id[i] = int(id[i])
        # esn[i] = int(esn[i])
        # case_id[i] = int(case_id[i])
        # drogue_depth[i] = int(drogue_depth[i])
        start_date[i] = parse(start_date[i])
        end_date[i] = parse(end_date[i])
        # consecutive_batch[i] = int(consecutive_batch[i])

    # find indexes of rows of project that we want to get metadata for
    project_indexes = []
    for index, name in enumerate(communication):
        if name != "GLOBALSTAR":
            project_indexes.append(index)

    # set up data and info for reformatting, and output as dicitonary
    all_data_raw = [id, esn, case_id, start_date, end_date, drogue_depth, boat_pi, school, consecutive_batch, project_names]
    data_titles = ["id", "esn", "case_id", "start_date", "end_date", "drogue_depth", "boat_pi", "school", "consecutive_batch", "project_names"]
    output_data = {}
    for index, col in enumerate(all_data_raw):
        col_data = []
        for row in (project_indexes): # only get data from entries that are not GLOBALSTAR
            col_data.append(col[row])
        output_data[data_titles[index]] = col_data

    return output_data


def write_ap3_codes_file(data_dict):
    """ writes a .dat file sililar to codes_ap3.dat format
        to be used in newer version of drift2xml
    """


    id = data_dict["id"]
    esn = data_dict["esn"]
    case_id = data_dict["case_id"]
    start_date = data_dict["start_date"]
    end_date = data_dict["end_date"]
    start_date_codes = data_dict["start_date_codes"]
    end_date_codes = data_dict["end_date_codes"]    
	drogue_depth = data_dict["drogue_depth"]
    boat_pi = data_dict["boat_pi"]
    school = data_dict["school"]
    consecutive_batch = data_dict["consecutive_batch"]
    project_names = data_dict["project_names"]

    file_read = open("/net/data5/jmanning/drift/codes_ap3.dat","r")
    dat_ids=[]
    for line in file_read:
      dat_ids.append(line.split()[2])
    file_read.close()

    file = open("/net/data5/jmanning/drift/codes_ap3.dat", "a")
    for i in range(len(id)):
        if id[i] not in dat_ids:
            print("WRITING TO CODES_AP3")			
            print(id[i])
            file.write(esn[i] + "\t" + case_id[i] + "\t" + id[i] + "\t" + drogue_depth[i] + "\t" + boat_pi[i] + "\t" + school[i] +
            "\t" + project_names[i] + "\t" + consecutive_batch[i] + "\t" + str(start_date_codes[i]) + "\t" + str(end_date_codes[i]) + "\n")
        else:
            print("NOT WRITING TO CODES AP3")

    file.close()


if __name__ == "__main__":
    """ prints data returned from get_gs_data in clean format """

    output_data = getfix_gs_data("ECOHAB")
    for field, data in output_data.items():
        print(field, ":", data)
    write_codes_file(output_data)

    print("")
    output_data = getfix_ap3_gs_data()
    for field, data in output_data.items():
        print(field, ":", data)
    write_ap3_codes_file(output_data)
