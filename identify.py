import sqlite3
import sys
import warnings
import scipy.io.wavfile as wavfile
import fingerprint as fp


def get_input_values():
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 5:
        print("Invalid number of arguments.")
        print("Usage: python3 identify.py -d database-file -i sample")
        sys.exit(1)

    # Get the index of the '-d' argument
    try:
        db_index = sys.argv.index('-d')
    except ValueError:
        print("Missing DataBase file.")
        print("Usage: python3 identify.py -d database-file -i sample")
        sys.exit(1)

    # Get the index of the '-i' argument
    try:
        input_index = sys.argv.index('-i')
    except ValueError:
        print("Missing input song file.")
        print("Usage: python3 identify.py -d database-file -i sample")
        sys.exit(1)

    # Get the values of the input database and output file
    db_file = sys.argv[db_index + 1]
    input_file = sys.argv[input_index + 1]
    return db_file, input_file


def load_database(filename):
    # Connect to the existing database
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    # Return the connection and cursor
    return conn, cursor


def search_song(cursor, hashes):
    # Prepare placeholders for the search hashes
    placeholders = ', '.join(['?'] * len(hashes))

    # Construct the SQL query to retrieve matching song_name and offset
    query = """
        SELECT song_name, offset
        FROM songs
        WHERE hash IN ({})
    """.format(placeholders)

    # Execute the query with the search hashes as parameters
    cursor.execute(query, hashes)

    # Fetch all the results
    results = cursor.fetchall()

    # Return the results
    return results



#main starts here
db_file, input_file = get_input_values()
print(f'DataBase file: {db_file}')
print(f'Input file: {input_file}')

conn, cursor = load_database(db_file)

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning) #ignore warnings about metadata in wav files

_, channels = wavfile.read(input_file) #get audio data
channels = channels[:,0]
print("Creating fingerprint for: "+input_file+"...")
hashes, offsets=fp.generate_fingerprint(channels)   #generate hashes and offsets for the song
print("Searching for matches...")
relative_offsets = []
matches = search_song(cursor, hashes)
for i, (song_name, offset) in enumerate(matches):
    search_offset = offsets[i]
    relative_offsets.append((song_name, offset - search_offset))
conn.close()    #close the connection to the database
print("Possible hash matches= ",len(relative_offsets))            

candidates = {}
max_count=0
candidate_name=''
for song_name, offset in relative_offsets:
    if song_name not in candidates:
        candidates[song_name] = {}
    if offset not in candidates[song_name]:
        candidates[song_name][offset] = 0
    candidates[song_name][offset] += 1
    if candidates[song_name][offset] > max_count:
        max_count = candidates[song_name][offset]
        candidate_name = song_name

print("Best candidate: ", candidate_name, " with ", max_count, " matches")