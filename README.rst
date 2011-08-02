======
iLogin
======
ilogin is a single sign-on script (SSO) that allows you to generate passwords
for each online service you're using.

This way you will have different passwords for each service and you don't have
to remember them as you'll be able to obtain each every time you want
to login to your service.

.. contents::

Install
=======

    ::

        $: easy_install ilogin
        $: python setup.py install


How it works?
=============
First time when you'll run this script, you'll be asked for the new password in
order to initialize the database::

    $: ilogin
    New password: MYSECRETPASSWORD

Remember this password as it will be used to login to database and to generate
passwords for your services. There is no possible way to recover this password.
If you lose it you'll have to reset all your online services passwords.

Add a service that you want to use with this script::

    $: ilogin add
    Service: google

Get a login for your service::

    $: ilogin
    Service: google
    Password: MYSECRETPASSWORD
    3dsad3425

Now go to google.com > Change password and update your password with the one
provided by this script: 3dsad3425

For now one, every time you want to login to google, run ilogin and
copy&paste generated password within gooogle.com Password field::

    $: ilogin
    Service: google
    Password: MYSECRETPASSWORD
    3dsad3425

You can also auto copy password to clipboard (UNIX and OS X)::

    $: ilogin copy
    Service: google
    Password: MYSECRETPASSWORD
    Password copied to clipboard

