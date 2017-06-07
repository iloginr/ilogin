Changelog
=========

3.1 - (2017-06-06)
------------------
* Feature: Add support for multiple MASTER passwords

3.0 - (2014-04-15)
------------------
* Bug fix: Fixed generation algorithm. This require you to update all your
  passwords on server side. Use 'ilogin export' to easily see all services
  where you used ilogin password generator. For backward compatibility use
  ilogin2

2.0 - (2013-12-13)
------------------

* Feature: Entirely update password generator algorithm. Default 16 chars,
  Google Application Specific Passwords like.
* Feature: Possibility to import / export settings from / to CSV file.
* Feature: Added more advanced options to control password generation.
  Password length, Use or not numbers, special characters, capital letters.
  Possibility to store and retrieve user name per service.
  Possibility to change password with versions
* Change: Use ilogin_old for previous generator/settings.

0.2 - (2011-08-02)
------------------

* Feature: Added option to auto copy password to clipboard (UNIX and OS X)


0.1 - (2010-23-12)
------------------

* Initial release
