from matplotlib import mlab
import numpy as np 
import hashlib


def generate_fingerprint(channel):
    window_size = 2**12 #should be a power of 2
    window_overlap = int (window_size * 0.5)
    #generate spectrogram
    spectrogram, freqs, times = mlab.specgram(channel,NFFT=window_size, Fs=SAMPLE_RATE, window=mlab.window_hanning, noverlap=window_overlap)
    spectrogram = 10 * np.log10(spectrogram)  # transmorm linear output to dB scale 
    # spectrogram[spectrogram == -np.inf] = 0  # replace infs with zeros
    peak_points=generate_robust_constellation(spectrogram, freqs, times)
    hashes, offsets=fast_combinatorial_hashing(peak_points)
    return hashes, offsets



def generate_robust_constellation(spectrogram, freqs, times):
    # Find points with higher amplitude within each block
    peak_points = []

    # Iterate over the spectrogram using block-wise steps
    for i in range(0, len(times), BLOCK_SIZE):
        for j in range(0, len(freqs), BLOCK_SIZE):
            # Get the block of amplitudes
            block_amplitudes = spectrogram[j:j+BLOCK_SIZE, i:i+BLOCK_SIZE]
            
            # Find the maximum amplitude within the block
            max_amplitude = np.max(block_amplitudes)
            
            # Find the indices of the maximum amplitude within the block
            indices = np.where(block_amplitudes == max_amplitude)
            
            # Convert the indices to frequency and time coordinates
            max_freq = freqs[j + indices[0]]
            max_time = times[i + indices[1]]
            
            # Store the peak point with maximum amplitude within the block
            peak_points.extend(list(zip(max_freq, max_time)))
    return peak_points


def fast_combinatorial_hashing(peak_points):
    hashes = []
    offsets = []
    for i in range(len(peak_points)):   #select anchor point
        for j in range(1, TARGET_ZONE): #select points in target zone
            if (i + j) < len(peak_points):  #if we are not out of range
                time1 = peak_points[i][1]   #get times of anchor point and point in target zone
                time2 = peak_points[i + j][1]
                freq1 = peak_points[i][0]   #get frequencies of anchor point and point in target zone
                freq2 = peak_points[i + j][0]
                t_delta = time2 - time1 #calculate time difference
                string_to_hash = f"{freq1}|{freq2}|{t_delta}"   #create a string to hash
                offsets.append(time1)   #add offset to the list
                # Generate a hash and add it to the list
                hashes.append(hashlib.sha256(string_to_hash.encode()).hexdigest())
    return hashes, offsets




SAMPLE_RATE = 44100
TARGET_ZONE = 8
BLOCK_SIZE = 50  # Adjust this value?
