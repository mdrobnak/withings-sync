"""This module takes care of the Eufy SQLite data."""
from datetime import date, datetime
import logging
import json
import os
import time
import pkg_resources
import requests
import sqlite3

from withings_sync.withings2 import WithingsMeasure,WithingsMeasureGroup

log = logging.getLogger("eufy")

class EufyData:
    """This class gets measurements from Eufy"""

    def get_measurements(self, startdate, enddate):
        """get Eufy Device measurements"""
        log.info("Get Measurements")

        dbcon = sqlite3.connect('/root/EufyLifeDb.db')
        cur = dbcon.cursor()
         
        measurements = []
        # Data comes back as a tuple and can be accessed via row[position]
        print(startdate, enddate)
        print("dataid, createtime, fatmode, bodyfat, bodyfatmass, bonemass, leanbodymass ,musclemass, proteinpercentage, visceralfat , water, weight from bodyfathistorym")
        for row in cur.execute("select dataid, createtime, fatmode, bodyfat, bodyfatmass, bonemass, leanbodymass ,musclemass, proteinpercentage, visceralfat , water, weight from bodyfathistorym WHERE bodyfat != 0.0 AND createtime >= ? AND createtime <= ? ORDER BY createtime", (startdate,enddate)):
          print(row)
          new_data = {}
          new_data["grpid"] = row[0]
          new_data["date"] = row[1]
          new_data["measures"] = [
           { "value": row[11], "type": 1, "unit": 0},
           { "value": row[3], "type": 6, "unit": 0},
           { "value": row[7], "type": 76, "unit": 0},
           { "value": (row[10]*row[11]/100.0), "type": 77, "unit": 0},
           { "value": row[5], "type": 88, "unit": 0},
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
