import sqlite3

# Connect to the database
conn = sqlite3.connect('database/crm_analytics.db')
cursor = conn.cursor()

# Check statuscode = 0
cursor.execute('SELECT COUNT(*) FROM salesorder WHERE statuscode = 0')
print('Count with statuscode=0:', cursor.fetchone()[0])

# Check distinct statuscodes
cursor.execute('SELECT DISTINCT statuscode FROM salesorder LIMIT 20')
print('\nDistinct statuscodes:', cursor.fetchall())

# Check statuscode distribution
cursor.execute('SELECT statuscode, COUNT(*) as cnt FROM salesorder GROUP BY statuscode ORDER BY cnt DESC LIMIT 10')
print('\nStatuscode distribution:')
for row in cursor.fetchall():
    print(f'  Status {row[0]}: {row[1]} records')

# Check if customeridname has data
cursor.execute('SELECT COUNT(*) FROM salesorder WHERE customeridname IS NOT NULL')
print(f'\nRecords with customeridname: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM salesorder WHERE customeridname IS NULL')
print(f'Records without customeridname: {cursor.fetchone()[0]}')

# Check sample data
cursor.execute('SELECT statuscode, customeridname, totalamount FROM salesorder LIMIT 5')
print('\nSample records:')
for row in cursor.fetchall():
    print(f'  statuscode={row[0]}, customer={row[1]}, amount={row[2]}')

# Check for statuscode with data
cursor.execute('''
SELECT statuscode, COUNT(*) as cnt 
FROM salesorder 
WHERE customeridname IS NOT NULL 
GROUP BY statuscode 
ORDER BY cnt DESC 
LIMIT 5
''')
print('\nStatuscode distribution where customeridname is not NULL:')
for row in cursor.fetchall():
    print(f'  Status {row[0]}: {row[1]} records')

conn.close()