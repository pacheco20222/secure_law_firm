# Secure Law Firm Case Management System

## Project Overview
The Secure Law Firm Case Management System is a web-based application designed to manage legal cases using both relational and non-relational databases. This project demonstrates advanced database management techniques, programming skills, and the integration of secure and efficient systems.

## Features
* User Roles: Admin, Lawyer, and Assistant. (The admin will be able to have access to everuthing, the lawyers, to their own cases, and will be able to edit them. The assistant will only be able to view cases that they have been assigned to.)

* Case Management: Add, view, edit, and delete cases.

* Document Management: Upload, view, and edit case-related documents

* Database Integration (both database are in a remote server, and will be access remotely):

    + PostgreSQL: Handles structured data for cases, clients, and users.

    + MongoDB: Stores unstructured data such as legal case documents.

* Security:

    + Encrypted passwords.

    + SSH tunneling for secure remote database connections.

    + Remote access to only trusted ssh keys.

* Backup and Restore Processes: 

    + Scripts to backup the database, set up to execute every week, using the crontab for tasks.

    + Scripts to restore the database, not the information, but to restore tables, and structure.


## Technologies Used
* Backend: Python (Flask framework).

* HTML, CSS, Bootstrap

* Databases:
    
    + PostgreSQL: Relational database for structured data.

    + MongoDB: NoSQL database for unstructured data (e.g., documents).

* Main libraries used:

    + SQLAlchemy (ORM for PostgreSQL)

    + pymongo (MongoDB client)

    + Bootstrap for UI styling


## Project setup

### Prerequisites

* Python 3.x installed

* MySQL and MongoDB running in a remote server or virtual machine

* SSH keys configure for accessing the server remotely

### .env file
There is a template_env file, where you will find the template for your own .env file to set up usernames, passwords, ssh keys.

## Installation
1. Clone the Repository:
```bash
git clone https://github.com/pacheco20222/secure_law_firm
cd secure_law_firm
```

2. Create a Virtual Environment and install Dependencies (recommended)

```bash
python -m venv venv # or you could use python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt # or you could use pip3 install -r requirements.txt
```

3. Remember to configure the environment variables: Create the .env file in the root project directory and set up your variables

4. Initilize the Database:
* For MySQL, go to the database_scripts folder, then to the MySQL folder, and copy the create_sql_database.sql for the MySQL database in your server

* For MongoDB go to the database_scripts folder, then to the MongoDB folder, and copy the script create_nosql_database.js, this java script file has the commands to create the collections. Remember in mongo you will need to use. use name_of_your_db, and then you will create the collection with the script

5. Run the application
```bash
python app.py
```
or
```bash
python3 app.py
```
or
```bash
flask run
```

## Usage
1. Admin:
* Can add, view, edit, and delete cases.

* Can upload and edit documents.

* Hass access to all system functionalities.

2. Lawyer:
* Can add, view(their own cases), and edit cases.

* Can upload and edit documents.

3. Assistant:
* Can view assigned cases.

*cannot edit or delete cases.

## Key Functionalities
1. Case Management:
* View all cases in the dashboard

* Edit case details, including status and description.

2. Document Management:
* Upload documents to cases

* Edit document details.

3. Backup and Restore:
* MySQL: backup_mysql.sh

* MongoDB: backup_mongodb.sh


## Security Features
* Authentication:
    
    + User login with encrypted passwords

    + Role-based access control for system functionalities.

* Database Security:

    + Remote connections via SSH tunneling.

    + User roles and permissions in MongoDB.

* Backupt Processes:
    
    + Scripts provided for database backup and restore

## File Structure

``` php
.
├── app.py                      # Flask application entry point
├── config.py                   # Application configuration
├── requirements.txt            # Python dependencies
├── templates/                  # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── view_case.html
│   └── view_case_details.html
├── static/                     # Static assets
│   ├── css/
│   ├── js/
│   └── img/
├── backup_scripts/             # Backup and restore scripts
│   ├── backup_postgresql.sh
│   ├── backup_mongodb.sh
├── models/                     # Database models
│   ├── case_model.py
│   ├── user_model.py
├── README.md                   # Documentation (this file)

```

### Future Improvements:

1. Working in a calendar for scheduling case hearings, or meetings.

2. Enhance UI with better accessibility features.

3. Implement notifications, and updates.