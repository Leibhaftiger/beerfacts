# beerfacts
what's the strongest beers

beerfacts.py
------------
This file creates a new local database and fetches the content in form of JSON data from https://world.openfoodfacts.org/category/beers/
openfoodfacts offers its data on json pages, like 1.json, 2.sjson ... 150.json
each page contains up to 20 products

The python script first scans how many products are in the selection totally, then checks how many products are on the page,
product by product from 1 page, then requests the next page and retrieves the next 20 products.

The user can specify, if he wants to retrieve all products from the category beer, or just a number. The python script checks, until
which page it has already retrieved the products, and if yes, then continues from there.

The script produces two tables, one for the beernames with alcohol level, foreign key to brewery table, page numbers and scan codes.
The second table includes the brewery data, connected via primary key to the beer table.

The two drop table commands should be commented out, if you don't want to start from sratch with the data retrieval every time.

The process of retrieving everything from openfoodfacts can take around 20 minutes for this category (over 2000 beers).

beerwords.py
------------
This file produces a beer cloud choosing the most strongest beers in alcohol. It uses the beerfacts.sqlite database, 
produced before with beerfacts.py
To see the beercloud, open the fresh created gword.htm file in a browser.


All files are using code fragments and ideas from coursera's Python 4 everybody course by Professor Charles Severance.
This code is part of the capstone project of the above course.
