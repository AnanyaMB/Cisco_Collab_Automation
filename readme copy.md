Overview : 
Certificate Management is a inbuilt functionality in CUCM versions 12.5 and above.
The lower versions however do not have the UCM certificate management API.
This script aims at automation the montioring of the ecpiring certificates on all CUCMs irrespective of the version using CLI commands.
Automation to bulk-delete the certificates from a CUCM server is also implemented.

Scripts : 
1. fetch_certificates.py - Used to fetch the certificate details along with isExpired true or false for mutliple CUCM clusters.
    - Accepts a csv file with hostname,username and password (Sample input file located in : /files/input_fetch_certificates.csv)
    - Generates a output file which contains the details of all successful certificates for which information is fetched (Sample output file located in : /files/output_fetch_certificates.xlsx)
    - Generate a error file which contains the details of all certificates for which there was error in fetching.(Sample error file located in : /files/error_fetch_certificates.xlsx)

2. delete_certs_per_cluster.py - Used for bulk certificate deletion from a CUCM Node.
    - Deletes the trust certificates which are expired.
    - Restarts the service (if allowed by CLI), else provides list of services to be restarted from GUI.
    - If there are multiple certificates with the same name, this script captures it and requires root access to delete it.

Data Requirements : 
1. CUCM Server (hostname)
2. CLI username
3. CLI password with minimum privilege = 1

Authors : 
Ananya Mallekatte Basavarajappa (amalleka)