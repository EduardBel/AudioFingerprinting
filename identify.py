import sqlite3
import sys
import warnings
import scipy.io.wavfile as wavfile
import fingerprint as fp
import time

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
        SELECT *
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
db_file, input_file = get_input_values()    #get the input values from the command line
print(f'DataBase file: {db_file}')
print(f'Input file: {input_file}')

conn, cursor = load_database(db_file)   #load the database

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning) #ignore warnings about metadata in wav files

start_time = time.time()    #start the timer

_, channels = wavfile.read(input_file) #get audio data

hashes_LR = []  #list of hashes for both channels
offsets_LR = [] #list of offsets(for each hash) for both channels

print("\nCreating fingerprint for: "+input_file+"...")
for chan in range(0,2): #iterate through both channels

    # ---------------------------------GENERATE FINGERPRINT---------------------------------
    hashes, offsets=fp.generate_fingerprint(channels[:,chan])   #generate hashes and offsets for the song (fingerprint)
    hashes_LR.extend(hashes)
    offsets_LR.extend(offsets)


print("Searching for matches...")

# ---------------------------------SEARCH FOR MATCHES---------------------------------
matches = search_song(cursor, hashes_LR)    #search for matches in the database (in a batch, way faster)
conn.close()    #close the connection to the database

#create a dictionary dict[hash]=offset
hashes_dict={}  #this is so we can find the sample offset for each match
for i, hash in enumerate(hashes_LR):
    hashes_dict[hash]=offsets_LR[i]


# ---------------------------------CALCULATE RELATIVE OFFSETS---------------------------------
relative_offsets = []
for i, (hash, offset, song_name) in enumerate(matches):   #calculate the relative offset for each match
    relative_offsets.append((song_name, offset - hashes_dict[hash]))    #calculate the relative offset and add it to the list with the song name
print("Possible hash matches= ",len(relative_offsets))            

# ---------------------------------FIND BEST MATCH---------------------------------
candidates = {}
max_count=0
candidate_name=''
for song_name, offset in relative_offsets:  #for all matches
    if song_name not in candidates: #if the song is not in the candidates dictionary, add it
        candidates[song_name] = {}
    if offset not in candidates[song_name]: #if the offset is not in the candidates dictionary for the song, add it
        candidates[song_name][offset] = 0
    candidates[song_name][offset] += 1  #increment the count for the song and offset
    if candidates[song_name][offset] > max_count:   #if the count is greater than the max_count, update the max_count and candidate_name
        max_count = candidates[song_name][offset]   #set the new max_count
        candidate_name = song_name  #set the new candidate_name

end_time = time.time()
elapsed_time = end_time - start_time

print("\nBest candidate: ", candidate_name, " with ", max_count, " matches")
print("Recognition time:", elapsed_time, "seconds")

if input_file.__contains__(candidate_name):
    print("\nCorrect identification of the sample!")
    exit(0)
else:    
    print("\nIncorrect identification! :-(")
    exit(1)