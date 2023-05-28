import sys
from matplotlib import mlab
# for data transformation 
import numpy as np 
# for visualizing the data 
import matplotlib.pyplot as plt
# for opening the media file 
import scipy.io.wavfile as wavfile

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


SAMPLE_RATE = 44100
BITS_PER_SAMPLE = 16
CHANNELS = 2
window_size = 2**12
window_overlap = int (window_size * 0.5)


#main starts here
input_folder, output_file = get_input_values()
print(f'Input folder: {input_folder}')
print(f'Output file: {output_file}')

audio_file = 'library/02.FortheBetter.wav' 

_, channels = wavfile.read(audio_file) #get audio data
channels = channels[:,0] # select left channel only

spectrogram, freqs, times = mlab.specgram(channels,NFFT=window_size, Fs=SAMPLE_RATE, window=mlab.window_hanning, noverlap=window_overlap)

spectrogram = 10 * np.log10(spectrogram)  # transmorm linear output to dB scale 
# spectrogram[spectrogram == -np.inf] = 0  # replace infs with zeros
# fig, axes = plt.subplots() 
# axes.imshow(spectrogram) 
# axes.set_xlabel('Time')
# axes.set_ylabel('Frequency') 
# axes.set_title( 'Spectrogram') 
# plt.gca().invert_yaxis()
# plt.show()


block_size = 50  # Adjust this value?
# Find points with higher amplitude within each block
peak_points = []

# Iterate over the spectrogram using block-wise steps
for i in range(0, len(times), block_size):
    for j in range(0, len(freqs), block_size):
        # Get the block of amplitudes
        block_amplitudes = spectrogram[j:j+block_size, i:i+block_size]
        
        # Find the maximum amplitude within the block
        max_amplitude = np.max(block_amplitudes)
        
        # Find the indices of the maximum amplitude within the block
        indices = np.where(block_amplitudes == max_amplitude)
        
        # Convert the indices to frequency and time coordinates
        max_freqs = freqs[j + indices[0]]
        max_times = times[i + indices[1]]
        
        # Store the peak point with maximum amplitude within the block
        peak_points.extend(list(zip(max_freqs, max_times)))

# Plot the spectrogram with peak points marked
plt.figure()
plt.imshow(spectrogram, origin='lower', aspect='auto', extent=[times.min(), times.max(), freqs.min(), freqs.max()])
plt.colorbar(label='Amplitude (dB)')
plt.scatter([p[1] for p in peak_points], [p[0] for p in peak_points], color='red', s=10, label='Peak Points')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram with Peak Points')
plt.legend()
plt.show()

