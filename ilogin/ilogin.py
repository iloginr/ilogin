#!/usr/bin/env python
""" Single Sign-On (SSO) script
"""
import os
import sys
import json
import subprocess
from hashlib import sha256
from getpass import getpass

DATABASE = {"services": [], "password": ""}


def _clipboard(cmd, text):
    """Copy text to clipboard using provided cmd"""
    try:
        with subprocess.Popen(cmd, stdin=subprocess.PIPE).stdin as pipe:
            pipe.write(text)
    except OSError as err:
        return err


class ILogin(object):
    """
    ilogin version 1.0

    Usage: ilogin <cmd>

    cmd:
      - login   Get login password for service

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
        self._db = None

    def initialize(self):
        """Initialize database"""
        password = getpass("New password:")
        db = DATABASE.copy()
        db["password"] = sha256(password.encode()).hexdigest()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(db, f)

    @property
    def path(self):
        """Get database path"""
        if self._path:
            return self._path

        path = os.path.expanduser("~/.ilogin")
        if not os.path.exists(path):
            os.mkdir(path)
        self._path = os.path.join(path, "config")
        return self._path

    @property
    def tries(self):
        """Number of tries"""
        return self._tries

    @property
    def database(self):
        """Database"""
        if not self._database:
            if not os.path.exists(self.path):
                self.initialize()
            with open(self.path, "r", encoding="utf-8") as ofile:
                self._database = json.load(ofile)
        return self._database

    #
    # Actions
    #
    def login(self):
        """Login"""
        services = self.database["services"]
        service = input("Service:")
        if sha256(service.encode()).hexdigest() not in services:
            raise ValueError(
                f"Service '{service}' not supported yet. "
                f"Try adding it first."
            )

        pwd = self.database["password"]
        loggedin = False
        for _tri in range(self.tries):
            password = getpass("Password:")
            if sha256(password.encode()).hexdigest() != pwd:
                print("Invalid password. Try again.")
                continue
            loggedin = True
            break

        if not loggedin:
            raise ValueError("Fuck off")

        string = f"{service}:{password}"
        return sha256(string.encode()).hexdigest()[-9:]

    def add(self):
        """Add new service"""
        name = input("Service:")
        service = sha256(name.encode()).hexdigest()
        if service in self.database["services"]:
            return
        self.database["services"].append(service)
        with open(self.path, "w", encoding="utf-8") as ofile:
            json.dump(self.database, ofile)
        self._db = None
        return "Service added"

    def passwd(self):
        """Change password"""
        old = getpass("Old password:")
        if sha256(old.encode()).hexdigest() != self.database["password"]:
            raise ValueError("Invalid password.")

        new = getpass("New password:")
        confirm = getpass("Confirm:")
        if new != confirm:
            raise ValueError(
                "Confirmed password should match the new password"
            )

        self.database["password"] = sha256(new.encode()).hexdigest()
        with open(self.path, "w", encoding="utf-8") as ofile:
            json.dump(self.database, ofile)
        self._db = None
        return "Password changed"

    def copy(self):
        """
        Copy password to clipboard using xsel, xclip (UNIX) or pdcopy (OS X)
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

        return (
            "Couldn't copy password to clipboard. "
            "Required clipboard tools are not installed."
        )


def main():
    """Run script"""
    service = ILogin()
    cmd = len(sys.argv) > 1 and sys.argv[1] or "login"
    cmd = getattr(service, cmd, None)
    if not cmd:
        print(service.__doc__)
        sys.exit(1)

    try:
        print(cmd())
    except ValueError as err:
        print(err)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
