"""
gs_examples.py
Created on June 24, 2019
Author: Dylan Montagu

Accesses drift_header.EXAMPLE_SHEET (google sheet) on the noaa.drifters@gmail.com account
Is a worksheet to be manipulated and worked on to famliarize the user with
the google sheets API

a spreadsheet is the whole drift_header file
a worksheet is individual tabs in the spreadsheet
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

def gs_example():
    """
    Accesses example worksheet on drift_header.gs, second worksheet
    Easy examples of grabbign data from google sheet
    """

    # set up google sheet access
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("noaa_drifter_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("drift_header").get_worksheet(1)
    # to see all worksheet methods, uncomment the line below
    # help(sheet)

    col_A = (sheet.col_values(1)) # Indexes start at 1, get column A data
    row_1 = (sheet.row_values(1)) # get row 1 data
    return col_A, row_1


if __name__ == "__main__":
    """ prints data returned from get_gs_data in clean format """
    pp = pprint.PrettyPrinter() # print formatted output
    output = gs_example()
    for elt in output:
        pp.pprint(elt)
