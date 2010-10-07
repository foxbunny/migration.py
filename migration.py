#!/usr/env/python python

### CONFIGURATION ###

# Default profile
default_profile = 'dev'

# Database configuration
#
# You may specify multiple profiles by adding appropriate keys in the profiles
# dict. Any keys missing from a profile will use the default values. Only
# ``database_type`` and ``database`` keys are required.
# 
# The first argument passed to the script will determine the profile to be
# used. Otherwise, ``default_profile`` will be selected.
#
profiles = {
    'dev': {
        'database_type':    'sqlite',           # can be 'mysql', 'postgres', 'sqlite', 'firebird', 'mssql', or 'oracle
        'database':         'development.db',   # name of the database to migrate
        'database_user':    '',                 # name of the user that can access the database
        'database_pw':      '',                 # password for the database user
        'other_opts':       {},                 # other database options to pass to web.database
    },
}

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

def main():
    import sys

    import web

    profile = len(sys.argv) > 0 and sys.argv[1] or deafault_profile or None

    if profile in profiles.keys():
        profile = profiles[profile]
        print "[INFO] Using profile %s" % profile
    else:
        print "[ERR!] No default profile defined, and %s is not usable." % profile
        sys.exit(2)

    web.config.debug = False

    database_type = profile.get('database_type', None)
    database = profile.get('database', None)
    if not all([database_type, database]):
        print "[ERR!] No database type or database specified."
        sys.exit(2)
    database_user = profile.get('databse_user', '')
    database_pw = profile.get('database_pw', '')
    other_opts = profile.get('other_opts', {})


    db_kwargs = {}
    db_kwargs['dbn'] = database_type
    db_kwargs['db'] = database
    if database_user:
        db_kwargs['user'] = database_user
    if database_pw:
        db_kwargs['pw'] = database_pw

    db_kwargs.update(other_opts)

    db = web.database(**db_kwargs)

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
                         CREATE TABLE %s (
                            migration_version   FLOAT
                         );""" % migration_versioning_table)
                db.query("""INSERT INTO %s
                            VALUES (0.0);
                         """ % migration_versioning_table)
                current_version = 0.0
                print "[>>>] Created tables and set schema version to 0.0"
        except:
            print "[ERR] There was an error creating the migration table."
            raise

    print "[NFO] Current schema version %s." % current_version

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
    main()
