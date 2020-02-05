Matching my SUSPENSE-ACCOUNT
===========================

This webapp import a CSV-file that has been downloaded from a bank (KNAB in Holand). The origin of the data is my business suspense account. The normal bank view does not provided the information I need, so I designed this webapp to provide me that information.

The reason I did this is to match all ingoing and outgoing payments. The process:
- register yourself
- login
- you will see, the first time you login, an empty dashboard.
- import a file via the IMPORT-page
- the data is stored, per user-id in a SQLite3 DB
- sorted on amount you, as user, can match payments. When ticked they will be marked as matched. They will not reappear in the dashboard.
- at the end you see only non-matched payments which you need to follow up to in your regular banking environment.

CONSTRAINTS
===========
- each record has an unique identifier provided by the bank.
- When importing the same file or same identifier, the import will skip those lines
- Moved away from GUNICORN to WAITRESS. GUNICORN caused a lot of unpredicted timeouts

TODO
====
- make webapp more responsive, will do this in CS50W
- add more validations when importing data (valid IBAN, DATES, non alfanumeric characters)
- make the description field editable, so you can add some remarks (doing this currently directly in DB ;))
- add a new page which summarizes the DEBIT and CREDIR records to see if the balance is sufficent to pay
- change password-feature
- pimp the FAQ-page
- make a page with all data either ticked or not
- add pagination
- add fancy piecharts

url: https://matching-suspense.herokuapp.com/
