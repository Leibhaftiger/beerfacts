import sqlite3
import json
import ssl
import urllib.request, urllib.error

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('beerfacts.sqlite')
cur = conn.cursor()

baseurl = "https://world.openfoodfacts.org/category/beers/"

cur.execute('DROP TABLE IF EXISTS facts_beer')      # enable this if you want a fresh start with an empty table
cur.execute('DROP TABLE IF EXISTS facts_brewery')   # enable this if you want a fresh start with an empty table

cur.execute('''CREATE TABLE IF NOT EXISTS facts_brewery (
	'id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	'name'	TEXT,
	'place'	TEXT,
	'country' TEXT )''')

cur.execute('''CREATE TABLE IF NOT EXISTS facts_beer (
	'id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	'beer_name'	TEXT,
	'alcohol' REAL,
	'brewery_id' INTEGER, 
	'code' TEXT,
	'page' INTEGER,
	 FOREIGN KEY(brewery_id) REFERENCES facts_brewery(id) )''')


# Pick up where we left off
page_count = None
cur.execute('SELECT max(page) FROM facts_beer' )
try:
    row = cur.fetchone()
    page_count = row[0]
    if not page_count :
        page_count = 1
    else:
        print("DB already contains content up to page:", str(page_count))
except:
    page_count = 1

if page_count is None : page_count = 1

many = 0
all_beers = False
beer_count = 0
while True:
    if ( many < 1 ) :
        conn.commit()
        sval = input('How many beers do you want to fetch (value or "all" or <cr>=exit: ')
        if ( len(sval) < 1 ) : exit()
        elif sval.lower() == "all" :
            all_beers = True
        else : many = int(sval)

    url = baseurl + str(page_count) + ".json"

    data = "None"
    try:
        # Open with a timeout of 30 seconds
        document = urllib.request.urlopen(url, None, 30, context=ctx)
        data = document.read().decode()
        if document.getcode() != 200 :
            print("Error code=",document.getcode(), url)
            break
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except Exception as e:
        print("Unable to retrieve or parse page",url)
        print("Error",e)
        fail = fail + 1
        if fail > 5 : break
        continue

    print(url,len(data))
    #print(data)  # for debug

    if len(data) == 68 :
        print("end of data set reached, exiting...")
        conn.commit()
        exit()

    try:
        js = json.loads(data)
    except:
        js = None

    if not js or js['products'] == None :
        print('==== Failure To Retrieve ====')
        print(data)
        break

    # print(json.dumps(js, indent=4))  # for debug

    beer_count = js["count"]
    if all_beers :
        many = beer_count
        all_beers = False

    print("Total number of  beers in foodfacts: " + str(beer_count))

    page_size = js["page_size"]
    nr_products_on_page = len(js["products"])
    print("Page Size:",page_size)
    if (nr_products_on_page < page_size) and (nr_products_on_page < many) :
        many = nr_products_on_page # don't try to read more entries than there is entries on page
        print("!!!Only",str(nr_products_on_page),"beers left to fetch from this page!!!")

    for product in range(page_size) :
        if many == 0 :  break

        try :
            beer_name = js["products"][product]["product_name"]
        except :
            beername = "not specified"
            print("no beername found, skip")
            many -= 1
            print(str(many), "left to retrieve")
            print(80 * "-")
            continue    #no name no gain
        if beer_name == "" :
            print("no beername found, skip")
            many -= 1
            print(str(many), "left to retrieve")
            print(80 * "-")
            continue    #no name no gain

        try :
            alcohol = js["products"][product]["nutriments"]["alcohol"]
        except:
            alcohol = -1
        try :
            brewery = js["products"][product]["brands"]
        except :
            brewery = "not specified"
        if brewery == "" : brewery = "not specified"
        try:
            place = js["products"][product]["manufacturing_places"]
        except:
            place = "not specified"
        if place == "" : place = "not specified"

        try:
            country = js["products"][product]["countries"]
        except:
            country = "not specified"
        if country == "" : country = "not specified"

        try:
            code = js["products"][product]["code"]
        except:
            code = "not specified"

        if product + 1   == 1 : suffix = "st"
        elif product + 1 == 2 : suffix = "nd"
        elif product + 1 == 3 : suffix = "rd"
        else : suffix = "th"

        print(str(product +1 ) + suffix + " Beer on Page " + str(page_count))

        print("beer name: " + beer_name)
        print("alcohol: " + str(alcohol))
        print("brewery: " + brewery)
        print("place: " + place)
        print("country: " + country)

        #check if beer is already in database checking scan code
        cur.execute('SELECT code FROM facts_beer WHERE code=? LIMIT 1', (code,))

        try:
            row = cur.fetchone()
            code = row[0]
            print('scan code', code, 'already exists, skipping.')
            many -= 1  # one beer less to fetch
            print(str(many), "left to retrieve")
            print(80 * "-")
            continue
        except:
            print('scan code', code, 'is new')


        # store brewery data first or only retrieve brewery foreign key

        cur.execute('SELECT id, name FROM facts_brewery WHERE name=? LIMIT 1', (brewery,))

        try:
            row = cur.fetchone()
            brewery_id = row[0]
            print('brewery', brewery, 'already exists, fetching id:', str(brewery_id))

        except:
            print('brewery', brewery, 'is new, adding to DB')
            cur.execute(
                'INSERT OR IGNORE INTO facts_brewery (name, place, country) VALUES ( ?,?,? )',
                (brewery, place, country) )
            print("added DB entry in facts_brewery: ", brewery, place, country)
            conn.commit()
            #Fetching new brewery_id
            brewery_id = cur.lastrowid

        #now store the beer, after we have brewery_id
        cur.execute('''INSERT INTO facts_beer (beer_name, alcohol, brewery_id, code, page)
            VALUES ( ?, ?, ?, ? ,? )''',
            (beer_name, alcohol, brewery_id, code, page_count))
        conn.commit()
        print("added DB entry in facts_beer: ", beer_name, alcohol, brewery_id, code, page_count)

        many -= 1  # one beer less to fetch
        print(str(many), "left to retrieve")
        print(80 * "-")

        if many == 0 :
            conn.commit()
            break

    page_count += 1


