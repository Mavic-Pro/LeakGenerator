# LeakGenerator
Simple python script that generates possible emails from the full name and searches for leaks


This script asks for the user's full name (including middle name if necessary) and the target domain:
- then generates the possible target emails
- looks for data leaks for all these emails
- saves the results in an 'uncleaned' CSV file


WARNING:
the script uses the API of leakcheck.io the dataleak site that I consider to be the best value for money, obviously such APIs are required for the script to function properly.


The API is to be saved in the file:
.pylcapi


example .pylcapi editing:

using terminal:
nano .pylcapi then insert this string (API with your API)

{"key": "API", "proxy": ""}
