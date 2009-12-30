#!/bin/bash
import web

### CONFIGURATION ###

# Database configuration
database_type = ''  # can be 'mysql', 'postgres', 'sqlite', 'firebird', 'mssql', or 'oracle
database = ''       # name of the database to migrate
database_user = ''  # name of the user that can access the database
database_pw = ''    # password for the database user

# Migration-specific configuration
migration_versioning_table = 'migration'

### MIGRATIONS ###

# Keys for the migration dict must be floats, and values must be valid SQL
# To write the migrations, simply edit the below dictionary directly, adn run:
#
#   python migration.py
#
# Version 0.0 is reserved for the blank state, so please start with any number
# larger than 0, such as 0.1 or 0.02.
#
# Inserting migrations between migrations that were _already_ run is not
# supported.
migrations = {
    1.0: """
         ENTER YOUR SQL HERE
         """,
}


### NO NEED TO MODIFY ANYTHING BELOW THIS LINE ###

web.config.debug = False

db_kwargs = {}
if database_type:
    db_kwargs['dbn'] = database_type
if database:
    db_kwargs['db'] = database
if database_user:
    db_kwargs['user'] = database_user
if database_pw:
    db_kwargs['pw'] = database_pw

db = web.database(dbn='', db='', user='')

try:
    schema_record = db.select(migration_versioning_table,
                              what='migration_version',
                              limit=1)
    print "[<<<] Found migration table. Reading schema version."
    current_version = schema_record[0].migration_version
except:
    print "[NFO] No migration table found."
    try:
        with db.transaction():
            db.query("""
                     CREATE TABLE %(migration_table)s (
                        migration_version   FLOAT
                     );
                     INSERT INTO %(migration_table)s
                        VALUES (0.0);
                     """ % {'migration_table': migration_versioning_table})
            current_version = 0.0
            print "[>>>] Created tables and set schema version to 0.0"
    except:
        print "[ERR] There was an error creating the migration table."
        raise

print "[NFO] Current schema version %s." % current_version

def run_migrations():
    migration_versions = [i for i in sorted(migrations.keys()) if i > current_version]
    if len(migration_versions) < 1:
        print "[NFO] Schema already at latest version."
    else:
        print "[NFO] Starting with version %s." % migration_versions[0]
        for ver in migration_versions:
            print "[>>>] Processing version %s." % ver
            try:
                with db.transaction():
                    db.query(migrations[ver])
                    print "[>>>] Updating migration version."
                    db.update(migration_versioning_table,
                              where='1 = 1',
                              migration_version=ver)
            except:
                print "[ERR] There was an error running the migration %s" % ver
                raise
            else:
                print "[OK!] SUCCESS"

if __name__ == '__main__':
    run_migrations()
