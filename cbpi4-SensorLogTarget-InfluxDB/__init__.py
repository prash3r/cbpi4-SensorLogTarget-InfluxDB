
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
import urllib3
import base64

logger = logging.getLogger(__name__)

# ToDo:
# - make log_data(id, value) to use id explicitly so there is no abiguity
# - create data legend for listener method call parameters including id, value, timestamp, name, cleanname
# - clean up data preperations for universal use
# - move influxDB logic to the plugin
# - 

class SensorLogTargetInfluxDB(CBPiExtension):

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())


    async def run(self):
        self.listener_ID = self.cbpi.log.add_sensor_data_listener(self.log_data_to_InfluxDB)
        logger.info("InfluxDB sensor log target listener ID: {}".format(self.listener_ID))

        self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
        self.influxdbaddr = self.cbpi.config.get("INFLUXDBADDR", None)
        self.influxdbport = self.cbpi.config.get("INFLUXDBPORT", None)
        self.influxdbname = self.cbpi.config.get("INFLUXDBNAME", None)
        self.influxdbuser = self.cbpi.config.get("INFLUXDBUSER", None)
        self.influxdbpwd = self.cbpi.config.get("INFLUXDBPWD", None)
        self.influxdbcloud = self.cbpi.config.get("INFLUXDBCLOUD", None)

        
       ## Check if influxdb is on config 
        if self.influxdb is None:
            logger.info("INIT Influxdb")
            try:
                await self.cbpi.config.add("INFLUXDB", "No", ConfigType.SELECT, "Write sensor data to influxdb", 
                                                                                                [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

        ## Check if influxdbaddr is in config
        if self.influxdbaddr is None:
            logger.info("INIT Influxdbaddr")
            try:
                await self.cbpi.config.add("INFLUXDBADDR", "localhost", ConfigType.STRING, "IP Address of your influxdb server (If INFLUXDBCLOUD set to Yes use URL Address of your influxdb cloud server)")
            except:
                logger.warning('Unable to update config')

        ## Check if influxdbport is in config
        if self.influxdbport is None:
            logger.info("INIT Influxdbport")
            try:
                await self.cbpi.config.add("INFLUXDBPORT", "8086", ConfigType.STRING, "Port of your influxdb server")
            except:
                logger.warning('Unable to update config')

        ## Check if influxdbname is in config
        if self.influxdbname is None:
            logger.info("INIT Influxdbname")
            try:
                await self.cbpi.config.add("INFLUXDBNAME", "cbpi4", ConfigType.STRING, "Name of your influxdb database name (If INFLUXDBCLOUD set to Yes use bucket of your influxdb cloud database)")
            except:
                logger.warning('Unable to update config')

        ## Check if influxduser is in config
        if self.influxdbuser is None:
            logger.info("INIT Influxdbuser")
            try:
                await self.cbpi.config.add("INFLUXDBUSER", " ", ConfigType.STRING, "User name for your influxdb database (only if required)(If INFLUXDBCLOUD set to Yes use organisation of your influxdb cloud database)")
            except:
                logger.warning('Unable to update config')

        ## Check if influxdpwd is in config
        if self.influxdbpwd is None:
            logger.info("INIT Influxdbpwd")
            try:
                await self.cbpi.config.add("INFLUXDBPWD", " ", ConfigType.STRING, "Password for your influxdb database (only if required)(If INFLUXDBCLOUD set to Yes use token of your influxdb cloud database)")
            except:
                logger.warning('Unable to update config')

       ## Check if influxdb cloud is on config 
        if self.influxdbcloud is None:
            logger.info("INIT influxdbcloud")
            try:
                await self.cbpi.config.add("INFLUXDBCLOUD", "No", ConfigType.SELECT, "Write sensor data to influxdb cloud (INFLUXDB must set to Yes)", 
                                                                                                [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')


        # check or register needed parameters
        # lets pretend they are already there..
    
    async def log_data_to_InfluxDB(self, cbpi, id, value, timestamp, name, cleanname):
        self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
        if self.influxdb == "No":
            return
        self.influxdbcloud = self.cbpi.config.get("INFLUXDBCLOUD", "No")
        self.influxdbaddr = self.cbpi.config.get("INFLUXDBADDR", None)
        self.influxdbport = self.cbpi.config.get("INFLUXDBPORT", None)
        self.influxdbname = self.cbpi.config.get("INFLUXDBNAME", None)
        self.influxdbuser = self.cbpi.config.get("INFLUXDBUSER", None)
        self.influxdbpwd = self.cbpi.config.get("INFLUXDBPWD", None)
        try:
            out="measurement,source=" + str(cleanname) + ",itemID=" + str(id) + " value="+str(value)
        except Exception as e:
            logging.error("InfluxDB data string creation Error: {}".format(e))
        if self.influxdbcloud == "Yes":
            self.influxdburl="https://" + self.influxdbaddr + "/api/v2/write?org=" + self.influxdbuser + "&bucket=" + self.influxdbname + "&precision=s"
            try:
                header = {'User-Agent': name, 'Authorization': "Token {}".format(self.influxdbpwd)}
                http = urllib3.PoolManager()
                req = http.request('POST',self.influxdburl, body=out, headers = header)
            except Exception as e:
                logging.error("InfluxDB cloud write Error: {}".format(e))

        else:
            self.base64string = base64.b64encode(('%s:%s' % (self.influxdbuser,self.influxdbpwd)).encode())
            self.influxdburl='http://' + self.influxdbaddr + ':' + str(self.influxdbport) + '/write?db=' + self.influxdbname
            try:
                header = {'User-Agent': name, 'Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic %s' % self.base64string.decode('utf-8')}
                http = urllib3.PoolManager()
                req = http.request('POST',self.influxdburl, body=out, headers = header)
            except Exception as e:
                logging.error("InfluxDB write Error: {}".format(e))

def setup(cbpi):
    cbpi.plugin.register("SensorLogTargetInfluxDB", SensorLogTargetInfluxDB)
