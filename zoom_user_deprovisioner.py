"""
Zoom User Deprovisioning

This tool is intended to help automate the deprovisioning process with Zoom. The
user provides an import CSV containing users to be deprovisioned, this listing is
compared with current Zoom user information, then deprovisioning is performed on
the users which were found in the system. Please note that due to Zoom API
limitations only 10 requests per second may be performed. This can cause the
tool to take a longer time to complete it's deprovisioning than expected.

Note: import CSV is expected to have the following:
- Header row as row 1 (not containing user data)
- Email column as column 1 (containing user emails associated with Zoom)

Pre-reqs: Python 3.x and requests library
Last modified: Oct 2017
By: Dave Bunten

License: MIT (see license.txt)
"""

import os
import sys
import logging
import json
import time
import math
import csv
import datetime
import argparse
import random
import zoom_web_api_client as zoom_web_api_client

def import_csv_zoom_users_list(filepath):
    """
    Function for gathering Zoom user emails based on user-supplied CSV file.

    Note: import CSV is expected to have the following:
    - Header row as row 1 (not containing user data)
    - Email column as column 1 (containing user emails associated with Zoom)

    arguments:
    filepath: file path to a JSON configuration file

    returns:
    zoom_user_emails_to_deprovision: list containing all emails from the import file
    """

    logging.info("Collecting user information from imported CSV file...")

    #initialize list for holding emails from imported CSV file
    zoom_user_emails_to_deprovision = []

    #open the CSV file for reading
    with open(filepath) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')

        #skip first row as this is expected to be the header row
        next(readCSV)

        #read each row of the CSV file collecting the first column value for each
        for row in readCSV:
            zoom_user_emails_to_deprovision.append(row[0])

    return zoom_user_emails_to_deprovision

def get_current_zoom_user_data(client, log_dir, current_datetime_string, zoom_user_emails_to_deprovision):
    """
    Function for finding current Zoom user data on all users. This function
    creates a backup of all current Zoom users on the system and collects full
    information on users to be deprovisioned (including the user's Zoom-internal
    ID which is used for the actual deprovisioning).

    arguments:
    client: Zoom API client for making requests
    log_dir: directory where logs are stored for this application
    current_datetime_string: string containing filename-safe string for current datetime
    zoom_user_emails_to_deprovision: list containing emails to potentially deprovision

    returns:
    zoom_users_to_deprovision: full information for Zoom users to be deprovisioned
        based on emails provided in zoom_user_emails_to_deprovision.
    """

    logging.info("Gathering current Zoom user data and metrics...")

    #create filepath string for backup of all user data (just in case)
    zoom_backup_filepath = log_dir+'zoom_users_backup_before_deprovisioning_'+current_datetime_string+'.csv'


    #initialize list for full Zoom user information on those to be deprovisioned
    zoom_users_to_deprovision = []

    #create various counts which will help provide metrics
    pro_account_count = 0
    basic_account_count = 0
    account_count = 0
    pro_account_remove_count = 0
    basic_account_remove_count = 0

    #page and result counts for user list requests
    page_count = 1
    result_count = 300

    #desired keys for backup of all users (not all keys are relevant)
    zoom_user_info_keys = [
        "id",
        "email",
        "first_name",
        "last_name",
        "type",
        "enable_webinar",
        "enable_large",
        "dept",
        "created_at",
        "lastClientVersion",
        "lastLoginTime",
        "status",
        "pmi"
    ]

    #open a new CSV writer to facilitate the backup file creation
    with open(zoom_backup_filepath, 'w', newline="") as f:

        #use keys found from zoom_user_info_keys to build the DictWriter
        csvwriter = csv.DictWriter(f, zoom_user_info_keys, dialect='excel', extrasaction='ignore')
        csvwriter.writeheader()

        #Zoom allows a maximum of 300 results per request with user listings.
        #This loop will go through each page of 300 or less to gather and backup
        #the information necessary to the function.
        while result_count == 300:
            #make the Zoom api request and parse the result for the data we need
            result = client.do_request("user/list", {"page_size":"300","page_number":page_count})

            #if no users are returned in the result, we break our loop
            if "users" not in result.json():
                break

            user_results = result.json()["users"]
            result_count = len(user_results)
            account_count += result_count

            #loop through each element in the user data returned
            for user_data in user_results:

                #change type from integer to human-readable value
                #also make counts of the number of accounts per type
                if user_data["type"] == 1:
                    basic_account_count += 1
                    user_data["type"] = "Basic"
                if user_data["type"] == 2:
                    pro_account_count += 1
                    user_data["type"] = "Pro"

                #gather user information based on emails found from imported CSV
                if user_data["email"] in zoom_user_emails_to_deprovision:
                    zoom_users_to_deprovision.append(user_data)

                    #count the nubmer of users in each category to be removed
                    if user_data["type"] == "Basic":
                        basic_account_remove_count += 1
                    if user_data["type"] == "Pro":
                        pro_account_remove_count += 1

                #write to our backup file to store the user information
                csvwriter.writerow(user_data)

            #increment our page count by 1 for each time we loop requests for
            #the user listings from Zoom
            page_count += 1

    #Share information on where the backup file will be located
    logging.info("Backup user data stored at: "+zoom_backup_filepath)

    #Share various metrics with the user on total, basic, pro and deprovisioning
    #information to better inform them before proceeding.
    logging.info("Total accounts: "+str(account_count))
    logging.info("Basic accounts: "+str(basic_account_count))
    logging.info("Pro accounts: "+str(pro_account_count))
    logging.info("Accounts to deprovision count (imported file): "+str(len(zoom_user_emails_to_deprovision)))
    logging.info("Estimated total accounts after deprovisioning: "+str(account_count-len(zoom_user_emails_to_deprovision)))
    logging.info("Estimated Pro accounts after deprovisioning: "+str(pro_account_count-pro_account_remove_count))
    logging.info("Estimated Basic accounts after deprovisioning: "+str(basic_account_count-basic_account_remove_count))

    return zoom_users_to_deprovision

def proceed_double_check():
    """
    Function for confirming deprovisioning action by user before proceeding. As
    the action taken from deprovisioning can have a large impact we want to be
    very certain the user does not accidentally move forward.

    returns:
    True or False: True indicates a positive response - to move forward. False
        indicates a negative response - to abort the operation of the tool.
    """

    #First check to proceed which asks for a y/n value. If the user does not answer
    #yes we return false to indicate an abort.
    if input("Do you wish to proceed with deprovisioning the specified users? (Y/N): ").upper() != "Y":
        return False

    #Second check to proceed which asks the user to type in a randomly chosen word.
    #This helps ensure the user cannot accidentally move forward with this operation
    #moreso than a single keystroke.

    #words for goodbye in various languages list
    words_for_goodbye = ["goodbye", "adieu", "ciao", "adios", "sayonara", "totsiens", "Wiedersehen"]

    #choose a random word from the words_for_goodbye list
    chosen_word = words_for_goodbye[random.randint(0, len(words_for_goodbye)-1)]

    #gather input based on the chosen random goodbye word from the user
    typed_word = input("DOUBLE CHECK: Do you wish to proceed with deprovisioning the specified users? Please type the word '"+chosen_word+"' to proceed: ")

    #check that the typed word is the random word chosen from the overall list.
    #If it is, the user has confirmed to proceed.
    if typed_word == chosen_word:
        return True
    else:
        return False

def deprovision_zoom_users(client, zoom_users_to_deprovision):
    """
    Function for performing Zoom user deprovisioning based on list of users
    provided to function. Please note: as per requirements outlined at
    https://zoom.github.io/api/#rate-limits only 10 requests per second may be
    performed. This may cause the application to seem to take longer than it
    should to perform the work involved.

    arguments:
    client: Zoom API client for making requests
    zoom_users_to_deprovision: full information for Zoom users to be deprovisioned
    """

    total_users_deprovisioned_count = 0
    time_interval_request_count = 0
    start_time_interval = datetime.datetime.now()

    #loop through each element in provided list to perform deprovisioning
    for zoom_user in zoom_users_to_deprovision:

        #perform permanent delete request using users unique Zoom ID
        result = client.do_request("user/permanentdelete", {"id":zoom_user["id"]})
        time_interval_request_count += 1

        #count the number of deprovisioned users by verifying the returned ID
        if result.json()["id"] == zoom_user["id"]:
           total_users_deprovisioned_count += 1

        #update the current time interval to accoutn for time restrictions in Zoom API
        cur_time_interval = datetime.datetime.now()

        #Check to see if less than a second has passed and 10 requests have already been made
        #If so, sleep for the remaining time until the next second begins
        if (cur_time_interval - start_time_interval).seconds < 1 and time_interval_request_count == 10:
            logging.info("Waiting to ensure Zoom request time restrictions are met.")
            time.sleep((1/1000000)*(1000000-(cur_time_interval - start_time_interval).microseconds+1000))
            start_time_interval = datetime.datetime.now()
            time_interval_request_count = 1

        #Else, if greater than a second has passed reset values to begin time
        #restriction counts again.
        elif (cur_time_interval - start_time_interval).seconds >= 1:
            start_time_interval = datetime.datetime.now()
            time_interval_request_count = 1

    #return total number of deprovisioned users to ensure validation may take place
    logging.info("Number of users deprovisioned: "+str(total_users_deprovisioned_count))

if __name__ == "__main__":

    run_path = os.path.dirname(__file__)

    #log file datetime
    current_datetime_string = '{dt.month}-{dt.day}-{dt.year}_{dt.hour}-{dt.minute}-{dt.second}'.format(dt = datetime.datetime.now())
    log_dir = run_path+'/logs/'
    log_filepath = log_dir+'zoom_user_deprovisioner_'+current_datetime_string+'.log'

    #logger for log file
    logging_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging_datefmt = '%m/%d/%Y - %I:%M:%S %p'
    logging.basicConfig(filename=log_filepath,
        filemode='w',
        format=logging_format,
        datefmt=logging_datefmt,
        level=logging.INFO
        )

    #logger for console
    console = logging.StreamHandler()
    formatter = logging.Formatter(logging_format,
    datefmt=logging_datefmt)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    #reduce the number of informational messages from the requests lib
    logging.getLogger('requests').setLevel(logging.WARNING)

    #open config file with api key/secret information
    api_config_file = open(run_path+"/"+".zoom_api_config")
    api_config_data = json.load(api_config_file)

    #create zoom client for performing API requests
    client = zoom_web_api_client.client(
        api_config_data["root_request_url"],
        api_config_data["api_key"],
        api_config_data["api_secret"],
        api_config_data["data_type"]
        )

    logging.info("Welcome to Zoom User Deprovisioner")

    #build argparser to determine if file argument was passed
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--file',help='Filepath for CSV Zoom users to deprovision list')
    args = parser.parse_args()

    #check for file arugment. if there is none ask for input from user for ad-hoc filepath
    if args.file == None:
        logging.info("Did not detect file argument, asking for input instead.")
        csv_filepath = input("Please enter a filepath for CSV Zoom users to deprovision list: ").replace("\"","")
    else:
        logging.info("Using provided file argument.")
        csv_filepath = args.file

    #find file extension to ensure we're using a CSV file
    path, file_extentsion = os.path.splitext(csv_filepath)

    #check whether the file exists
    if not os.path.exists(csv_filepath):
        logging.error("Unable to find provided filepath")
        sys.exit(0)
    #check whether the file has the correct extension (."csv")
    elif file_extentsion != ".csv":
        logging.error("Provided file is not a CSV. Please use a CSV for the Zoom users to deprovision list.")
        sys.exit(0)

    #create list of users to deprovision from import_csv_zoom_users_list function
    zoom_user_emails_to_deprovision = import_csv_zoom_users_list(csv_filepath)

    #gather current Zoom user information and full information on users to deprovision
    zoom_users_to_deprovision = get_current_zoom_user_data(client, log_dir, current_datetime_string, zoom_user_emails_to_deprovision)

    #provide forewarning for users that the requests could take some time to complete
    logging.info("Please note that due to Zoom API restrictions only 10 requests per second may be processed.")
    logging.info("Double checking with user before proceeding.")

    #Perform double check on whether to proceed or not based on user input
    if proceed_double_check():
        logging.info("Received confirmation to proceed. Starting deprovisioning process now.")
        deprovision_zoom_users(client, zoom_users_to_deprovision)
        logging.info("Finished deprovisioning Zoom users. Recommended: confirm new user counts and backup user listing files. Exiting.")
    else:
        logging.info("User indicated not to proceed with deprovisioning. Exiting.")
        sys.exit(0)
