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


#main starts here
db_file, input_file = get_input_values()
print(f'DataBase file: {db_file}')
print(f'Input file: {input_file}')

conn, cursor = load_database(db_file)

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning) #ignore warnings about metadata in wav files

_, channels = wavfile.read(input_file) #get audio data



conn.close()    #close the connection to the database