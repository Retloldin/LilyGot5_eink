import urequests
import os
import json
import machine
from time import sleep

class OTAUpdater:
    """ This class handles OTA updates. It checks for updates (using version number),
        then downloads and installs multiple filenames, separated by commas."""
    _print = print

    def __init__(self, _print=print, repo_url='', *filenames):

        self._print = _print
        
        if "www.github.com" in repo_url :
            self._print("Updating {} to raw.githubusercontent".format(repo_url), 'OTAUpdater')
            self.repo_url = repo_url.replace("www.github","raw.githubusercontent")
        elif "github.com" in repo_url:
            self._print("Updating {} to raw.githubusercontent'".format(repo_url), 'OTAUpdater')
            self.repo_url = repo_url.replace("github","raw.githubusercontent")            
        self.version_url = self.repo_url + 'version.json'
        self._print("version url is: {}".format(self.version_url), 'OTAUpdater')
        self.filename_list = [filename for filename in filenames]

        # get the current version (stored in version.json)
        if 'version.json' in os.listdir():    
            with open('version.json') as f:
                self.current_version = int(json.load(f)['version'])
            self._print("Current device firmware version is '{}'".format(self.current_version), 'OTAUpdater')

        else:
            self.current_version = 0
            # save the current version
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)

    def fetch_new_code(self, filename):
        """ Fetch the code from the repo, returns False if not found."""
    
        # Fetch the latest code from the repo.
        self.firmware_url = self.repo_url + filename
        response = urequests.get(self.firmware_url)
        if response.status_code == 200:
            self._print('Fetched file {}, status: {}'.format(filename, response.status_code), 'OTAUpdater')
    
            # Save the fetched code to file (with prepended '_')
            new_code = response.text
            with open('_{}'.format(filename), 'w') as f:
                f.write(new_code)
            self._print('Saved as _{}'.format(filename), 'OTAUpdater')
            return True
        
        elif response.status_code == 404:
            self._print('Firmware not found - {}.'.format(self.firmware_url), 'OTAUpdater')
            return False

    def check_for_updates(self):
        """ Check if updates are available. (Note: GitHub caches values for 5 min.)"""
        
        self._print('Checking for latest version... on {}'.format(self.version_url), 'OTAUpdater')
        response = urequests.get(self.version_url)
        
        data = json.loads(response.text)
        
        self._print("data is: {}, url is: {}".format(data, self.version_url), 'OTAUpdater')
        self._print("data version is: {}".format(data['version']), 'OTAUpdater')
        # Turn list to dict using dictionary comprehension
        # my_dict = {data[i]: data[i + 1] for i in range(0, len(data), 2)}
        
        self.latest_version = int(data['version'])
        self._print('latest version is: {}'.format(self.latest_version), 'OTAUpdater')
        
        # compare versions
        newer_version_available = True if self.current_version < self.latest_version else False
        
        self._print('Newer version available: {}'.format(newer_version_available), 'OTAUpdater' )
        return newer_version_available
    
    def download_and_install_update_if_available(self):
        """ Check for updates, download and install them."""
        if self.check_for_updates():

            # Fetch new code
            for filename in self.filename_list:
                self.fetch_new_code(filename)

            # Overwrite current code with new
            for filename in self.filename_list:
                newfile = "_{}".format(filename)
                os.rename(newfile, filename)
                self._print('Renamed _{} to {}, overwriting existing file'.format(filename, filename), 'OTAUpdater')

            # save the current version
            with open('version.json', 'w') as f:
                json.dump({'version': self.latest_version}, f)
            self._print('Update version from {self.current_version} to {self.latest_version}', 'OTAUpdater')

            # Restart the device to run the new code.
            self._print('Restarting device...', 'OTAUpdater')
            sleep(0.3)
            machine.reset() 
        else:
            self._print('No new updates available.', 'OTAUpdater')
