import sys

# for visualizing the data 
# for opening the media file 
import scipy.io.wavfile as wavfile

import fingerprint as fp


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
print(f'Input folder: {input_folder}')
print(f'Output file: {output_file}')

audio_file = 'library/02.FortheBetter.wav' 

_, channels = wavfile.read(audio_file) #get audio data
channels = channels[:,0] # select left channel only
#TODO: dual channel
hashes=fp.generate_fingerprints(channels)



# Plot the spectrogram with peak points marked
# plt.figure()
# plt.imshow(spectrogram, origin='lower', aspect='auto', extent=[times.min(), times.max(), freqs.min(), freqs.max()])
# plt.colorbar(label='Amplitude (dB)')
# plt.scatter([p[1] for p in peak_points], [p[0] for p in peak_points], color='red', s=10, label='Peak Points')
# plt.xlabel('Time (s)')
# plt.ylabel('Frequency (Hz)')
# plt.title('Spectrogram with Peak Points')
# plt.legend()
# plt.show()

