#!env python

# This script will query flickr with options for username and number of photos to process. 
# The script will query the flickr API for the number of comments and favorites for each photo. The script will then store the results in a sqlite database.

# import the necessary packages
import flickrapi, os, time, sqlite3, sys

# Get options from the command line
import argparse
parser = argparse.ArgumentParser(description='Query Flickr')
parser.add_argument('-u', '--username', help='Flickr username', required=True)
parser.add_argument('-n', '--numphotos', help='Number of photos to query', required=True)
# Add option to dispay all photos in the database
parser.add_argument('-s', '--show', help='Display all photos in the database', action='store_true')
# Add option to add photos to the database
parser.add_argument('-p', '--addphotos', help='Add photos to the database', action='store_true')
# Add option to count number of photos in flickr and the database
parser.add_argument('-c', '--count', help='Count number of photos with number of photos in the database', action='store_true')
args = parser.parse_args()

# Check if key and secret environment variables are set
if not 'FLICKR_KEY' in os.environ:
    print("Error: FLICKR_KEY environment variable not set")
    sys.exit(1)
if not 'FLICKR_SECRET' in os.environ:
    print("Error: FLICKR_SECRET environment variable not set")
    sys.exit(1)

# connect to flickr
flickr = flickrapi.FlickrAPI(os.environ['FLICKR_KEY'], os.environ['FLICKR_SECRET'], format='parsed-json')

# get the user id
user = flickr.people.findByUsername(username=args.username)

# Get a list of photos
photos = flickr.people.getPhotos(user_id=user['user']['id'])

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


def retrive_photos():
    # loop through the photos
    # limit the number of photos as per args
    num_photos = int(args.numphotos)  # number of photos to query
    counter = 0  # initialize the counter variable
    for photo in photos['photos']['photo']:
        if counter == num_photos:  # break the loop when the counter reaches the desired number of photos
            break
        photo_id = photo['id']  # get the photo id
        # check if the photo is already in the database, if not, add it to the matrix
        c.execute('SELECT COUNT(*) FROM flickrstats WHERE photo_id=?', (photo_id,))
        if c.fetchone()[0] == 0:
            # get the number of comments
            comments = flickr.photos.comments.getList(photo_id=photo_id)
            num_comments = len(comments['comments'])
            # get the number of favorites
            favorites = flickr.photos.getFavorites(photo_id=photo_id)
            num_favorites = len(favorites['photo'])
            # print the photo id being added to the database
            print("Adding photo id: " + photo_id)
            # add the photo id, number of comments, and number of favorites to the sqlite database
            c.execute('INSERT INTO flickrstats VALUES (?,?,?)', (photo_id, num_comments, num_favorites))
            conn.commit()
            counter += 1

# Check if the show option is set
if args.show:
    display_all_photos()
    sys.exit(0)

# Check if the photos option is set
if args.addphotos:
    retrive_photos()
    sys.exit(0)

# Check if the count option is set
if args.count:
    # Display the number of photos in flickr and the database
    print("Number of photos in flickr: " + str(photos['photos']['total']))
    c.execute('SELECT COUNT(*) FROM flickrstats')
    print("Number of photos in the database: " + str(c.fetchone()[0]))
    sys.exit(0)

