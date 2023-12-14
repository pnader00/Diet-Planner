import psycopg
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    """ read the database.ini file and returns connection parameters """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        parameters = parser.items(section)
        for param in parameters:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def connect(parameters):
    """ Connect to the PostgreSQL database server with params dict"""
    connection = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        connection = psycopg.connect(**parameters)

        # create a cursor
        cur = connection.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg.DatabaseError) as error:
        print(error)
    finally:
        return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)

        print("Query executed successfully")
    except (Exception, psycopg.DatabaseError) as error:
        print(error)
    finally:
        connection.commit()
        cursor.close()


def read_query(connection, query):
    cursor = connection.cursor()
    res = None
    try:
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        return res
    except (Exception, psycopg.DatabaseError) as error:
        print(error)


if __name__ == '__main__':
    """Autotest"""
    params = config()
    conn = connect(params)
    q ='SELECT * FROM legacy_db WHERE ndbnumber = 43312;'
    q2 = "SELECT * FROM nutritions_short"
    print(read_query(conn, q))
    print(read_query(conn, q2))
    conn.close()