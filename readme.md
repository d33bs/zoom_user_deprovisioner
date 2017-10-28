# Zoom User Deprovisioner

This tool is intended to help automate the user deprovisioning process with Zoom. The tool requires a user to provide an import CSV containing users to be deprovisioned, this listing is compared with current Zoom user information, then deprovisioning is performed on the users which were found in the system. Please note that due to Zoom API limitations only 10 requests per second may be performed. This can cause the tool to take a longer time to complete it's deprovisioning than expected.

Note: the imported CSV is expected to have the following:
- Header row as row 1 (not containing user data)
- Email column as column 1 (containing user emails associated with Zoom)

## Prerequisites and Documentation

Before you get started, make sure to install or create the following prerequisites:

* Python 3.x: [https://www.python.org/downloads/](https://www.python.org/downloads/)
* Python Requests Library (non-native library used for HTTP requests): [http://docs.python-requests.org/en/master/](http://docs.python-requests.org/en/master/)
* Enable Zoom API key: [https://zoom.us/developer/api/credential](https://zoom.us/developer/api/credential)

Zoom API documentation can be found at the following URL: [https://zoom.github.io/api/](https://zoom.github.io/api/)

## File Descriptions

- **zoom_web_api_client.py**
A web api client used to connect to the system. This is Python class file used for making connections to the Zoom system.

- **.zoom_api_config_sample**
A file which uses JSON to store credentials used by the zoom_web_api_client.py Python class for making web API connections to Zoom. The file as it stands in this repository is a template and must be modified to be named ".zoom_api_config" and filled in with your site-specific information.

- **zoom_user_deprovisioner.py**
A file which makes use of the zoom_web_api_client.py Python class for making web API connections to Zoom. This example will take input from the user on a local destination filepath for an imported CSV file, execute a Zoom API requests for current Zoom users, create a backup file of all Zoom users in the associated account, then perform the deprovisioning based on the imported file.

## Usage

1. Ensure prerequisites outlined above are completed.
2. Fill in necessary &lt;bracketed&gt; areas in .zoom_api_config_sample specific to your account
2. Rename .zoom_api_config_sample to  .zoom_api_config (removing the text "_sample")
2. Create CSV containing list of users you wish to deprovision in Zoom.
3. Run zoom_api_example.py with Python 3.x (you may use the --file argument to indicate the imported CSV file or the tool will prompt you for one as well)

### Sample Usage

    C:\sgtpepper>python C:\sgtpepper\zoom_user_deprovisioner\zoom_user_deprovisioner.py --file C:\sgtpepper\zoom_users_to_deprovision_10_2017_TEST.csv
    10/25/2017 - 03:38:41 PM - INFO - Welcome to Zoom User Deprovisioner
    10/25/2017 - 03:38:41 PM - INFO - Using provided file argument.
    10/25/2017 - 03:38:41 PM - INFO - Collecting user information from imported CSV file...
    10/25/2017 - 03:38:41 PM - INFO - Gathering current Zoom user data and metrics...
    10/25/2017 - 03:38:57 PM - INFO - Backup user data stored at: C:\sgtpepper\zoom_user_deprovisioner/logs/zoom_users_backup_before_deprovisioning_10-25-2017_15-38-41.csv
    10/25/2017 - 03:38:57 PM - INFO - Total accounts: ####
    10/25/2017 - 03:38:57 PM - INFO - Basic accounts: ####
    10/25/2017 - 03:38:57 PM - INFO - Pro accounts: ####
    10/25/2017 - 03:38:57 PM - INFO - Accounts to deprovision count (imported file): ####
    10/25/2017 - 03:38:57 PM - INFO - Estimated total accounts after deprovisioning: ####
    10/25/2017 - 03:38:57 PM - INFO - Estimated Pro accounts after deprovisioning: ####
    10/25/2017 - 03:38:57 PM - INFO - Estimated Basic accounts after deprovisioning: ####
    10/25/2017 - 03:38:57 PM - INFO - Please note that due to Zoom API restrictions only 10 requests per second may be processed.
    10/25/2017 - 03:38:57 PM - INFO - Based on your number of accounts to deprovision (####) it may take up to #### minutes to complete this action.
    10/25/2017 - 08:32:20 AM - INFO - Double checking with user before proceeding.
    Do you wish to proceed with deprovisioning the specified users? (Y/N): y
    DOUBLE CHECK: Do you wish to proceed with deprovisioning the specified users? Please type the word 'Wiedersehen' to proceed: Wiedersehen
    10/25/2017 - 08:32:26 AM - INFO - Received confirmation to proceed. Starting deprovisioning process now.
    10/25/2017 - 08:32:26 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:27 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:28 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:29 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:30 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:31 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:32 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:33 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:34 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:35 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:36 AM - INFO - Waiting to ensure Zoom request time restrictions are met.
    10/25/2017 - 08:32:37 AM - INFO - Number of users deprovisioned: ####
    10/25/2017 - 08:32:37 AM - INFO - Finished deprovisioning Zoom users. Recommended: confirm new user counts and backup user listing files. Exiting.
