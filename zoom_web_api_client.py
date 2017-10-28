"""
Class for creating connections to Zoom API
Last modified: July 2017
By: Dave Bunten
"""

import json
import requests
requests.packages.urllib3.disable_warnings()

class client:
    def __init__(self, root_request_url, key, secret, data_type):
        self.root_request_url = root_request_url
        self.key = key
        self.secret = secret
        self.data_type = data_type

    def do_request(self, resource, request_parameters):
        self.resource = resource
        self.request_parameters = request_parameters

        #create URL based on what we're requesting
        url = self.root_request_url + self.resource

        # Header values required for Zoom API request
        values = {
            "api_key":self.key,
            "api_secret":self.secret,
            "data_type":self.data_type
        }

        #add the request params to the values dictionary to be sent in request
        values.update(self.request_parameters)

        #attempt to make request and return results if successful
        #else return the error
        try:
            rsp = requests.post(url, data=values, verify=False)
            return rsp
        except HTTPError as e:
            return e.response.status_code
