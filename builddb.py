import sys
import scipy.io.wavfile as wavfile
import fingerprint as fp
import sqlite3
import os
import warnings
import time


def create_database(filename):
    # create a DB
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    # Create a table to store the elements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            hash TEXT,
            offset REAL,
            song_name TEXT
        )
    ''')

    # Return the connection and cursor
    return conn, cursor


def insert_elements(conn, cursor, values):
    query = "INSERT INTO songs (hash, offset, song_name) VALUES (?, ?, ?)"  # SQL query to insert a new element

    # Execute the query in a batch, this way we avoid executing the query for each element and the commit is faster
    cursor.executemany(query, values)
    conn.commit()


def save_database(conn):
    # Close the connection to the database
    conn.close()


def get_input_values():
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 5:
        print("Invalid number of arguments.")
        print("Usage: python3 builddb.py -i songs-folder -o database-file")
        sys.exit(1)

    # Get the index of the '-i' argument
    try:
        input_index = sys.argv.index('-i')
    except ValueError:
        print("Missing input folder.")
        print("Usage: python3 builddb.py -i songs-folder -o database-file")
        sys.exit(1)

    # Get the index of the '-o' argument
    try:
        output_index = sys.argv.index('-o')
    except ValueError:
        print("Missing output file.")
        print("Usage: python3 builddb.py -i songs-folder -o database-file")
        sys.exit(1)

    # Get the values of the input folder and output file
    input_folder = sys.argv[input_index + 1]
    output_file = sys.argv[output_index + 1]
    return input_folder, output_file


#main starts here

input_folder, output_file = get_input_values()  #get the input folder and output file from the command line
print(f'\nPopulating DB with the songs from: {input_folder}')
print(f'DB file name: {output_file}\n')

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning)  #ignore warnings about metadata in wav files

try:
    os.remove(output_file)  #remove the database file if it already exists by the same name
except OSError:
    pass  # Ignore the error if the file doesn't exist or cannot be removed


start_time = time.time()    #start timer

# ---------------------------------CREATE THE DATABASE---------------------------------
conn, cursor=create_database(output_file)   

for filename in os.listdir(input_folder):   #iterate through all the files in the input folder  
    if filename.endswith('.wav'):   #only process .wav files
        audio_file = os.path.join(input_folder, filename)   #get the full path of the file
        filename=filename[4:-4].replace(" ", "_") #remove numbers and .wav extension (clean filename for comparison in identification process)
        print("Creating fingerprint for: "+filename+"...")        

        _, channels = wavfile.read(audio_file) #get audio data
        hashes_LR = []  #list of hashes for both channels
        offsets_LR = [] #list of offsets(for each hash) for both channels
        for chan in range(0,2): #iterate through both channels

            # ---------------------------------GENERATE FINGERPRINT---------------------------------
            hashes, offsets=fp.generate_fingerprint(channels[:,chan])   #generate hashes and offsets for the song (fingerprint)
            hashes_LR.extend(hashes)
            offsets_LR.extend(offsets)
        
        # Prepare a list of tuples containing the values to insert
        values = [(hashes_LR[i], offsets_LR[i], filename) for i in range(len(hashes_LR))]

        # ---------------------------------INSERT HASHES, OFFSETS AND SONG NAME INTO THE DATABASE---------------------------------
        insert_elements(conn, cursor, values)

# ---------------------------------SAVE THE DATABASE---------------------------------
save_database(conn) #117MB file if we only keep the left channel, block size 50, target zone 8
end_time = time.time()
elapsed_time = end_time - start_time
print("DB creation time:", elapsed_time, "seconds\n")
print("All songs have been fingerprinted and inserted into the DB!")