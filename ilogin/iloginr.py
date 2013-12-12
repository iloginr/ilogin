#!/usr/bin/env python
""" Single Sign-On (SSO) script
"""
import re
import os
import sys
import json
import subprocess
from hashlib import sha512
from getpass import getpass

DATABASE = {
    "services": {},
    "password": ""
}

def _clipboard(cmd, text):
    """ Copy text to clipboard using provided cmd
    """
    try:
        with subprocess.Popen(cmd, stdin=subprocess.PIPE).stdin as pipe:
            pipe.write(text)
    except OSError, err:
        return err


class ILogin(object):
    """ Usage: iloginr.py <cmd>

    cmd:
      - login   Get login password for service (default)

      - add     Add service to ilogin

      - passwd  Change ilogin password.
                !! YOU'LL NEED TO MANUALLY RESET ALL YOUR SERVICES PASSWORDS !!

      - copy    Get login password for service and copy it to clipboard
                  - UNIX:    xsel or xclip required
                  - OS X:    pbcopy required
                  - Windows: Not supported yet
    """
    def __init__(self):
        self._database = None
        self._tries = 3
        self._path = ""

    def initialize(self):
        """ Initialize database
        """
        password = getpass("New password:")
        db = DATABASE.copy()
        db["password"] = sha512(password).hexdigest()
        json.dump(db, open(self.path, 'w'))

    @property
    def path(self):
        """ Get database path
        """
        if self._path:
            return self._path

        path = os.path.expanduser("~/.iloginr")
        if not os.path.exists(path):
            os.mkdir(path)
        self._path = os.path.join(path, 'config')
        return self._path

    @property
    def tries(self):
        """ Number of tries
        """
        return self._tries

    @property
    def database(self):
        """ Database
        """
        if not self._database:
            if not os.path.exists(self.path):
                self.initialize()
            self._database = json.load(open(self.path, 'r'))
        return self._database
    #
    # Actions
    #
    def login(self):
        """ Login
        """
        services = self.database['services']
        service = raw_input("Service:")
        if service not in services:
            raise ValueError("Service '%s' not supported yet. "
                             "Try adding it first: iloginr add" % service)

        pwd = self.database['password']
        loggedin = False
        for _tri in range(self.tries):
            password = getpass("Password:")
            if sha512(password).hexdigest() != pwd:
                print "Invalid password. Try again."
                continue
            loggedin = True
            break

        if not loggedin:
            raise ValueError('Fuck off')

        settings = services[service]

        string = "%s:%s" % (service, password)
        pwd = sha512(string).hexdigest()
        newpwd = []
        for idx in range(0,16):
            start = idx*8
            end = idx*8 + 8
            chunk = pwd[start:end]
            if not chunk:
                break

            numbers = re.findall(r'\d+', chunk)
            numbers = [int(number) for number in numbers]
            letters = re.findall(r'[a-z]]', chunk)
            letters = [ord(letter) for letter in letters]

            number = sum(numbers) + sum(letters)

            if (idx+1) % 4 == 0 and settings.get('numbers', False):
                letter = number % 10
            elif (idx+1) % 5 == 0 and settings.get('caps', False):
                letter = number % 25 + 97
                letter = chr(letter)
                letter = letter.upper()
            elif (idx+1) % 7 == 0 and settings.get('special', False):
                letter = number % 14 + 33
                letter = chr(letter)
            else:   
                letter = number % 25 + 97
                letter = chr(letter)

            newpwd.append(u'%s' % letter)

        return ''.join(newpwd)

    def add(self):
        """ Add new service
        """
        service = raw_input("Service:")

        settings = {}
        numbers = raw_input("Use numbers [y/N]:")
        if numbers.lower() in ("y", "yes", "true", "1"):
            settings['numbers'] = True
        special = raw_input("Use special characters [y/N]:")
        if special.lower() in ("y", "yes", "true", "1"):
            settings['special'] = True
        caps = raw_input("Use capital letters: [y/N]:")
        if caps.lower() in ("y", "yes", "true", "1"):
            settings['caps'] = True
        version = raw_input("Version:")
        if version.strip():
            settings['version'] = version

        self.database['services'][service] = settings
        json.dump(self.database, open(self.path, 'w'))
        self._db = None

        return "Service added"

    def passwd(self):
        """ Change password
        """
        old = getpass("Old password:")
        if sha512(old).hexdigest() != self.database["password"]:
            raise ValueError("Invalid password.")

        new = getpass("New password:")
        confirm = getpass("Confirm:")
        if new != confirm:
            raise ValueError("Confirmed password should match the new password")

        self.database["password"] = sha512(new).hexdigest()
        json.dump(self.database, open(self.path, 'w'))
        self._db = None
        return "Password changed"

    def copy(self):
        """ Copy password to clipboard using xsel, xclip (UNIX) or pdcopy (OS X)
        """
        passwd = self.login()

        # xsel
        error = _clipboard("xsel", passwd)
        if not error:
            return "Password copied to clipboard using xsel."

        # xclip
        error = _clipboard("xclip", passwd)
        if not error:
            return "Password copied to clipboard using xclip."

        # pbcopy
        error = _clipboard("pbcopy", passwd)
        if not error:
            return "Password copied to clipboard using pbcopy."

        return ("Couldn't copy password to clipboard. "
                "Required clipboard tools are not installed.")


def main():
    """ Run script
    """
    service = ILogin()
    cmd = len(sys.argv) > 1 and sys.argv[1] or 'login'
    cmd = getattr(service, cmd, None)
    if not cmd:
        print service.__doc__
        sys.exit(1)

    try:
        print cmd()
    except ValueError, err:
        print err
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
