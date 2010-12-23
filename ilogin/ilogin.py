#!/usr/bin/env python
""" Single Sign-On (SSO) script
"""
import os
import sys
import json
from hashlib import sha256
from getpass import getpass

DATABASE = {
    "services": [],
    "password": ""
}

class ILogin(object):
    """ Usage: ilogin.py <cmd>

    cmd:
      - login   Get login password for service
      - add     Add service to ilogin
      - passwd  Change ilogin password.
                YOU'LL NEED TO MANUALLY RESET ALL YOUR SERVICES PASSWORDS !!!
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
        db["password"] = sha256(password).hexdigest()
        json.dump(db, open(self.path, 'w'))

    @property
    def path(self):
        """ Get database path
        """
        if self._path:
            return self._path

        path = os.path.expanduser("~/.ilogin")
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
        if sha256(service).hexdigest() not in services:
            raise ValueError("Service '%s' not supported yet. "
                             "Try adding it first." % service)

        pwd = self.database['password']
        loggedin = False
        for tri in range(self.tries):
            password = getpass("Password:")
            if sha256(password).hexdigest() != pwd:
                print "Invalid password. Try again."
                continue
            loggedin = True
            break

        if not loggedin:
            raise ValueError('Fuck off')

        string = "%s:%s" % (service, password)
        return sha256(string).hexdigest()[-9:]

    def add(self):
        """ Add new service
        """
        name = raw_input("Service:")
        service = sha256(name).hexdigest()
        if service in self.database['services']:
            return
        self.database['services'].append(service)
        json.dump(self.database, open(self.path, 'w'))
        self._db = None
        return "Service added"

    def passwd(self):
        """ Change password
        """
        old = getpass("Old password:")
        if sha256(old).hexdigest() != self.database["password"]:
            raise ValueError("Invalid password.")

        new = getpass("New password:")
        confirm = getpass("Confirm:")
        if new != confirm:
            raise ValueError("Confirmed password should match the new password")

        self.database["password"] = sha256(new).hexdigest()
        json.dump(self.database, open(self.path, 'w'))
        self._db = None
        return "Password changed"

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

if __name__=="__main__":
    main()
