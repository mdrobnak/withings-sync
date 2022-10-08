"""This module takes care of the Fitbit data."""
from datetime import date, datetime
import logging
import json
import os
import time
import pkg_resources
import requests

from withings_sync.withings2 import WithingsMeasure,WithingsMeasureGroup

log = logging.getLogger("fitbit")

HOME = os.environ.get("HOME", ".")

APP_CONFIG = os.environ.get(
    "WITHINGS_APP",
    pkg_resources.resource_filename(__name__, "config/withings_app.json"),
)
USER_CONFIG = os.environ.get("WITHINGS_USER", HOME + "/.withings_user.json")


class FitbitData:
    """This class gets measurements from Fitbit"""

    def get_measurements(self, startdate, enddate):
        """get Fitbit Aria measurements"""
        log.info("Get Measurements")

        filelist = []
        dir_path='/root/fitbit/MatthewDrobnak/Personal & Account/'
        for path in os.listdir(dir_path):
            # check if current path is a file
            if path.startswith('weight-') and os.path.isfile(os.path.join(dir_path, path)):
                filelist.append(os.path.join(dir_path, path))
        filelist.sort()

        # Fitbit data is in lbs, not kg at least for US users.
        # Fitbit has a date, and a time value, not a timestamp. Uses local time.
        # Generate data in the format that the rest of the program uses.
        measurements = []
        for filename in filelist:
            f = open(filename)
            file_data = json.load(f)
            for dat in file_data:
              if dat.get("source") == "Aria":
                print(dat)
                new_data = {}
                new_data["grpid"] = dat.get("logId")
                new_data["date"] = int(datetime.strptime( dat.get("date") + " " + dat.get("time"), "%m/%d/%y %H:%M:%S").timestamp())
                new_data["measures"] = [
                    { "value": dat.get("weight")*0.45359237, "type": 1, "unit": 0},
                    { "value": dat.get("fat"), "type": 6, "unit": 0},
                ]
                measurements.append(new_data)

        log.debug("Measurements received")
        return [
            WithingsMeasureGroup(g)
            for g in measurements
        ]
 
    def get_height(self):
        """get height from Withings"""
        height = None
        height_timestamp = None
        height_group = None

        log.debug("Get Height")

        f = open('/root/height.json')

        return 1.777
        measurements = json.load(f)
        #measurements = req.json()

        if measurements.get("status") == 0:
            log.debug("Height received")

            # there could be multiple height records. use the latest one
            for record in measurements.get("body").get("measuregrps"):
                height_group = WithingsMeasureGroup(record)
                if height is not None:
                    if height_timestamp is not None:
                        if height_group.get_datetime() > height_timestamp:
                            height = height_group.get_height()
                else:
                    height = height_group.get_height()
                    height_timestamp = height_group.get_datetime()

        return height
