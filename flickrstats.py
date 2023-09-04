#!env python

# This script will query flickr with options for username and number of photos to process.
# The script will query the flickr API for the number of comments and favorites for each photo. The script will then store the results in a sqlite database.

# import the necessary packages
import argparse, flickrapi, sys, os, sqlite3, math

username = 'hentismith'

# Get options from the command line
parser = argparse.ArgumentParser(description='Query Flickr')
parser.add_argument('-s', '--show', help='Display all photos in the database', action='store_true')
# Add option to check for photos with no comments or favorites
parser.add_argument('-k', '--check', help='Check for photos with no comments or favorites', action='store_true')
# Add option to add photos to the database
parser.add_argument('-a', '--addphotos', help='Add photos to the database', action='store_true')
# Add option to count number of photos in flickr and the database
parser.add_argument('-c', '--count', help='Count number of photos with number of photos in the database', action='store_true')
args = parser.parse_args()

# Display the options if no options are set
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

# Check if key and secret environment variables are set
if not 'FLICKR_KEY' in os.environ:
    print("Error: FLICKR_KEY environment variable not set")
    sys.exit(1)
if not 'FLICKR_SECRET' in os.environ:
    print("Error: FLICKR_SECRET environment variable not set")
    sys.exit(1)

# connect to flickr
flickr = flickrapi.FlickrAPI(os.environ['FLICKR_KEY'], os.environ['FLICKR_SECRET'], format='parsed-json')

user = flickr.people.findByUsername(username=username)

# Get a list of photos
photos = flickr.people.getPhotos(user_id=user['user']['id'])

# calculate number of pages to query
num_pages = photos['photos']['pages']

# connect to the database
conn = sqlite3.connect('flickrstats.db')
c = conn.cursor()

# create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS flickrstats (photo_id text, num_comments integer, num_favorites integer)''')

# Create function to display all photos in the database
def display_all_photos():
    c.execute('SELECT * FROM flickrstats')
    for row in c:
        print(row)

def retrive_photos(page_num):
    # use pagenate to get all photos and then write to the database
    photos = flickr.people.getPhotos(user_id=user['user']['id'], per_page=100, page=page_num)
    # loop through the photos and get the number of comments and favorites
    for photo in photos['photos']['photo']:
        print("Processing photo: " + photo['id'])
        # get the number of comments
        photo_id=photo['id']
        # write to the database if the photo doesn't exist
        c.execute('SELECT COUNT(*) FROM flickrstats WHERE photo_id=?', (photo_id,))
        if c.fetchone()[0] == 0:
            print("Adding photo: " + photo_id)
            num_comments = flickr.photos.getInfo(photo_id=photo_id)['photo']['comments']['_content']
            # get the number of favorites
            favorites = flickr.photos.getFavorites(photo_id=photo_id)
            num_favorites = str(len(favorites['photo']['person']))
            c.execute("INSERT INTO flickrstats VALUES ('" + photo_id + "', " + num_comments + ", " + num_favorites + ")")
            # sleep for 1 second to avoid flickr api limits
            time.sleep(1)
        # commit the changes
        conn.commit()

# Check for photos with no comments and favorites
def check_photos():
    c.execute('SELECT * FROM flickrstats WHERE num_comments=0 AND num_favorites=0')
    for row in c:
        print(row)

# Check if the show option is set
if args.show:
    print("Displaying all photos in the database")
    display_all_photos()
    sys.exit(0)

# Check if the photos option is set
if args.addphotos:
    # Loop through the pages
    for page_num in range(1, int(run_pages) + 1):
        print("Processing page: " + str(page_num))
        retrive_photos(page_num)
    sys.exit(0)

# Check if the count option is set
if args.count:
    # Display the number of photos in flickr and the database
    print("Number of photos in flickr: " + str(photos['photos']['total']))
    c.execute('SELECT COUNT(*) FROM flickrstats')
    print("Number of photos in the database: " + str(c.fetchone()[0]))
    sys.exit(0)

# Check if the check option is set
if args.check:
    print("Checking for photos with no comments or favorites")
    check_photos()
    sys.exit(0)
