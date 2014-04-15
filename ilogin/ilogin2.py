#!/usr/bin/env python
""" Single Sign-On (SSO) script
"""
import re
import os
import sys
import json
import csv
import subprocess
from hashlib import sha512
from getpass import getpass

DATABASE = {
    "services": {},
    "schema": {
        "length": {"title": "Password length", "type": "int", "default": 0},
        "user": {"title": "User name", "type": "str", "default": ""},
        "numbers": {"title": "Use numbers", "type": "bool", "default": False},
        "special": {"title": "Use special characters", "type": "bool", "default": False},
        "caps": {"title": "Use capital letters", "type": "bool", "default": False},
        "version": {"title": "Version", "type": "int", "default": 0},
    },
    "layout": ["length", "user", "numbers", "special", "caps", "version"],
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
    """
    ilogin version 2.0

    Usage: ilogin <cmd>

    For older versions use ilogin1 <cmd>

    cmd:
      login   Get login password for service (default)

      user    Get login username for service

      add     Add service to ilogin

      field   Add new field

      import  Import services from CSV file. CSV file headers (advanced options are optional):

              "Service", ["Password length", "User Name", "Use Numbers", "Use Special Charaters", "Use Capital Letters", "Version"]
              "example.com", "16", "user@example.com", "n", "y", "false", "2"
              "foo.bar", "", "", "", "", "", ""
              "bar.foo", "9", "", "0", "1", "true", "7"

      export  Export services to CSV file.
              !! This will not export your passwords !!

      passwd  Change ilogin password.
              !! ALL YOUR SERVICES PASSWORDS WILL CHANGE AND YOU'LL NEED TO MANUALLY CHANGE THEM SERVER SIDE !!

      copy    Get login password for service and copy it to clipboard
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
        json.dump(db, open(self.path, 'w'),  indent=2)

    @property
    def path(self):
        """ Get database path
        """
        if self._path:
            return self._path

        path = os.path.expanduser("~/.ilogin")
        if not os.path.exists(path):
            os.mkdir(path)
        self._path = os.path.join(path, '.config')
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
    def user(self, service=None):
        """ Get login user name
        """

        if not service:
            service = raw_input("Service: ")

        services = self.database['services']
        if service not in services:
            print "Service '%s' not supported yet. Let's add it. Ctrl+C to cancel:" % service
            try:
                self.add(service)
            except KeyboardInterrupt:
                raise SystemExit("Aborted.")
        return services[service].get('user', None)

    def login(self, service=None):
        """ Login
        """
        if not service:
            service = raw_input("Service: ")

        services = self.database['services']
        if service not in services:
            print "Service '%s' not supported yet. Let's add it. (Ctrl+C to cancel)" % service
            try:
                self.add(service)
            except KeyboardInterrupt:
                raise SystemExit("Aborted.")
            print "Service added. Provide master password to continue."

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
        version = settings.get('version', "1")
        length = settings.get('length', 16)

        string = "%s:%s:%s" % (service, password, version)

        pwd = sha512(string).hexdigest()
        newpwd = []

        for idx in range(0,length):
            stop = 128 / length
            start = idx*stop
            end = idx*stop + stop
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
                if letter in (0, 1):
                    letter = 9
            elif (idx+1) % 5 == 0 and settings.get('caps', False):
                letter = number % 25 + 97
                letter = chr(letter)
                letter = letter.upper()
                if letter in ("L",):
                    letter = "M"
                elif letter in ("O",):
                    letter = "U"
            elif (idx+1) % 7 == 0 and settings.get('special', False):
                letter = number % 14 + 33
                letter = chr(letter)
            else:
                letter = number % 25 + 97
                letter = chr(letter)
                if letter in ("l",):
                    letter = "k"

            newpwd.append(u'%s' % letter)

        return ''.join(newpwd)

    def field(self, name=None, title=None, typo=None, default=None):
        """ Add new field
        """
        if not name:
            name = raw_input("Field name: ")

        if not title:
            title = raw_input("Field title: ")

        if not typo:
            typo = raw_input("Field type [int, str, bool]: ")

        if not default:
            default = raw_input("Field default value: ")

        if typo not in ("int", "str", "bool"):
            typo = "str"

        if typo == "int":
            default = int(default)
        elif typo == "bool":
            if default in ("y", "yes", "true", "1"):
                default = True
            else:
                default = False

        self.database["schema"][name] = {
            "title": title,
            "type": typo,
            "default": default
        }

        if name not in self.database["layout"]:
            self.database["layout"].append(name)

        json.dump(self.database, open(self.path, 'w'),  indent=2)
        self._db = None
        return "Field added"

    def _add(self, service, settings):
        """ Add new service to database
        """
        self.database['services'][service] = settings
        json.dump(self.database, open(self.path, 'w'),  indent=2)
        self._db = None

    def add(self, service=None, settings=None):
        """ Add new service
        """
        if not service:
            service = raw_input("Service: ").strip()

        if settings is None:
            settings = {}
            advanced = raw_input("Advanced settings [y/N]: ")
            if advanced.lower() in ("y", "yes", "true", "1"):

                schema = self.database.get("schema", {})
                layout = self.database.get("layout", [])

                for wid in layout:
                    field = schema.get(wid, {})
                    title = field.get("title", None)
                    typo = field.get("type", "str")
                    default = field.get("default", None)
                    if not title:
                        continue

                    value = raw_input(u"%s [%s]: " % (title, default)).strip()
                    value = value or default
                    if not value:
                        continue

                    if typo == "int":
                        value = int(value)
                    elif typo == "bool":
                        if value in ("y", "yes", "true", "1"):
                            value = True
                        else:
                            value = False

                    if not value:
                        continue

                    settings[wid] = value

        self._add(service, settings)
        return "Service added"

    def export_csv(self, path=None):
        """ Export settings to CSV
        """
        if not path:
            path = raw_input("CSV Output File Path: ").strip()

        writer = csv.writer(open(path, "w"))

        header = ["service"]
        header.extend(self.database["layout"])

        services = self.database['services']

        writer.writerow(header)
        for service, settings in services.items():
            row = [service]
            for idx, col in enumerate(header):
                if idx == 0:
                    continue
                val = settings.get(col, "")
                row.append(u"%s" % val)
            writer.writerow(row)
        return "Export complete"

    def import_csv(self, path=None):
        """ Import settings from CSV
        """
        if not path:
            path = raw_input("CSV Input File Path: ").strip()

        reader = csv.reader(open(path, "r"))

        header = ["service"]
        header.extend(self.database["layout"])

        for index, row in enumerate(reader):
            if index == 0 and u'service' in row[0].lower():
                continue

            service = ''
            settings = {}
            row = [col for y, col in enumerate(row)]
            for idx, col in enumerate(header):
                if idx == 0:
                    service = row[0]
                    continue

                if len(row) > idx:
                    val = row[idx].strip()
                    if not val:
                        continue

                    if re.findall(r"\d+", val):
                        val = int(val)
                    elif val.lower() in ("y", "yes", "true", "1"):
                        val = True
                    elif val.lower() in ("n", "no", "false", "0"):
                        val = False

                    settings[col] = val

            self._add(service, settings)
        return "Import complete"

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
        json.dump(self.database, open(self.path, 'w'),  indent=2)
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
    if u"import" in cmd:
        cmd = "import_csv"
    if u"export" in cmd:
        cmd = "export_csv"
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
