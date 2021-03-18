#!/usr/bin/env python

"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Mazen Al Jundi (majundi) <majundi@cisco.com>"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import configparser
import os
from datetime import datetime
from tetpyclient import RestClient
from tqdm import tqdm


def check_settings():
    list_dir = os.listdir()
    if 'settings.ini' not in list_dir:
        print('Alert!: settings.ini is missing, please make sure to have the setting.ini in the same folder of cby.py')
        exit(0)
    else:
        settings_path = os.getcwd()
        return settings_path


# Get values from settings.ini
def get_value(key, value):
    settings = configparser.ConfigParser()
    settings.read('settings.ini')
    try:
        setting = settings.get(key, value)
        if not value:
            print(f'{setting} value is missing')
            exit(0)
        else:
            return setting
    except:
        print(f'{setting} is not defined in the settings.ini')
        exit(0)


# Create Backup Folder
def create_backup_folder(backup_path):
    os.chdir(backup_path)
    backup_folder = str(datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.mkdir(backup_folder)
    os.chdir(backup_folder)


# download Labels(annotations)
def inv_sensors_scope_backup(tet_client, root_app_scope_name):
    tet_client.download('labels.csv', '/assets/cmdb/download/' + root_app_scope_name)
    # app scopes and sensors backup
    backups = ['app_scopes', 'sensors']
    for backup in backups:
        tet_client.download(backup + '.json', '/' + backup)
    # inventory filters backup
    tet_client.download('inventories.json', '/filters/inventories')


# workspaces Backup
def workspaces_backup(tet_client):
    # create workspace folder
    os.mkdir('workspaces')
    # change directory
    os.chdir('workspaces')
    # Download workspaces
    tet_client.download('workspaces.json', '/applications')
    resp = tet_client.get('/applications')
    return resp.json()


# Download Policies for the workspaces
def policies_backup(workspaces, tet_client):
    for workspace in tqdm(workspaces):
        os.mkdir(workspace['name'])
        tet_client.download(workspace['name'] + '/policies.json', '/applications/' + workspace['id'] + '/policies')


def main():
    check_settings()
    endpoint = get_value('tetration', 'endpoint')
    api_key = get_value('tetration', 'api_key')
    api_secret = get_value('tetration', 'api_secret')
    root_app_scope_name = get_value('tetration', 'tenant')
    backup_path = get_value('backup', 'path')
    create_backup_folder(backup_path)
    tet_client = RestClient(endpoint, api_secret=api_secret, api_key=api_key)
    inv_sensors_scope_backup(tet_client, root_app_scope_name)
    workspaces = workspaces_backup(tet_client)
    policies_backup(workspaces, tet_client)
    print('Configuration Backup completed Successfully!')


if __name__ == "__main__":
    main()
