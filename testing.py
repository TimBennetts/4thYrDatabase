import sqlalchemy

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from createDatabase import theActivePurchaseOrder, createDB

#Change these
dbname = "BBBYO.db"

dbSession = createDB(dbname)
pos = [instance for instance in dbSession.query(theActivePurchaseOrder)]

for po in pos:
  print po
  print type(po)



