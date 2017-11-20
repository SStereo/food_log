# This create a new database for the nutrition planner application

import psycopg2
#TODO: import bleach

def createtables():
    db = psycopg2.connect(dbname="np", user="vagrant", host="localhost", port="5432")
    c = db.cursor()
    SQL_LIST = [
        """CREATE TABLE meals (
            id SERIAL PRIMARY KEY,
            title TEXT,
            description TEXT,
            rating SMALLINT,
            image BYTEA,
            created TIMESTAMP WITH TIME ZONE DEFAULT now());"""
        ,
        """CREATE TABLE ingredients (
            id SERIAL PRIMARY KEY,
            title TEXT,
            description TEXT,
            image BYTEA,
            created TIMESTAMP WITH TIME ZONE DEFAULT now())"""
        ]

    for statement in SQL_LIST:
        c.execute(statement)
        print ("Excuted "+statement[0:30])
    db.commit()
    db.close()

def testconnection():
    try:
        db = psycopg2.connect(dbname="np", user="vagrant", host="127.0.0.1", port="5432")
        c = db.cursor()
        c.execute("SELECT * FROM meals;")
        db.close
        print (c.fetchall())
        return 
    except psycopg2.OperationalError as err:
        print ("Can not connect: {0}".format(err))
        
if __name__ == '__main__':
    print ("Start testing PostgreSQL connection ...")
    #testconnection()
    createtables()
    
