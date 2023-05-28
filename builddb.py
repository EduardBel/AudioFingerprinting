import sys
import scipy.io.wavfile as wavfile
import fingerprint as fp
import sqlite3
import os
import warnings


def create_database(filename):
    # Connect to the database or create a new one if it doesn't exist
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
    query = "INSERT INTO songs (hash, offset, song_name) VALUES (?, ?, ?)"

    # Execute the query in a batch
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

input_folder, output_file = get_input_values()
print(f'\nPopulating DB with the songs from: {input_folder}')
print(f'DB file name: {output_file}\n')
warnings.filterwarnings("ignore", category=wavfile.WavFileWarning)  #ignore warnings about metadata in wav files
conn, cursor=create_database(output_file)
# audio_file = 'library/02.FortheBetter.wav' 
for filename in os.listdir(input_folder):
    if filename.endswith('.wav'):
        audio_file = os.path.join(input_folder, filename)
        print("Creating fingerprint for: "+filename+"...")        
        _, channels = wavfile.read(audio_file) #get audio data
        hashes_LR = []
        offsets_LR = []
        for chan in range(0,2):
            hashes, offsets=fp.generate_fingerprint(channels[:,chan])
            hashes_LR.extend(hashes)
            offsets_LR.extend(offsets)
        
        # Prepare a list of tuples containing the values to insert
        values = [(hashes_LR[i], offsets_LR[i], filename) for i in range(len(hashes_LR))]
        insert_elements(conn, cursor, values)


save_database(conn) #117MB file if we only keep the left channel, block size 50, target zone 8
print("All songs have been fingerprinted and inserted into the DB!")