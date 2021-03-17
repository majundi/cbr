#!/usr/bin/env python

import configparser
import json
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


# download Labels(annotations)
def inv_sensors_scope_backup(tet_client, root_app_scope_name):
    tet_client.download('labels.csv', '/assets/cmdb/download/' + root_app_scope_name)
    # app scopes and sensors backup
    backups = ['app_scopes', 'sensors']
    for backup in backups:
        tet_client.download(backup + '.json', '/' + backup)
    # inventory filters backup
    tet_client.download('inventories.json', '/filters/inventories')


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
    os.chdir(backup_path)
    backup_folder = str(datetime.now())
    os.mkdir(backup_folder)
    os.chdir(backup_folder)
    tet_client = RestClient(endpoint, api_secret=api_secret, api_key=api_key)
    inv_sensors_scope_backup(tet_client, root_app_scope_name)
    workspaces = workspaces_backup(tet_client)
    policies_backup(workspaces, tet_client)
    print('Configuration Backup completed Successfully!')


if __name__ == "__main__":
    main()
