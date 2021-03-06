import torch
import librosa
import platform
import numpy as np

# torchaudio is only supported on Linux
if platform.system() == 'Linux':
    try:
        import torchaudio
    except ImportError:
        raise ImportError("SpectrogramPaser requires torchaudio package.")


class Spectrogram(object):
    """
    Create a spectrogram from a audio signal.

    Args: sample_rate, window_size, stride, feature_extract_by
        sample_rate (int): Sample rate of audio signal. (Default: 16000)
        window_size (int): window size (ms) (Default : 20)
        stride (int): Length of hop between STFT windows. (ms) (Default: 10)
    """
    def __init__(self, sample_rate=16000, window_size=20, stride=10):
        self.sample_rate = sample_rate
        self.n_fft = int(sample_rate * 0.001 * window_size)
        self.hop_length = int(sample_rate * 0.001 * (window_size - stride))

    def __call__(self, signal):
        spectrogram = torch.stft(
            torch.FloatTensor(signal),
            self.n_fft,
            hop_length=self.hop_length,
            win_length=self.n_fft,
            window=torch.hamming_window(self.n_fft),
            center=False,
            normalized=False,
            onesided=True
        )
        spectrogram = (spectrogram[:, :, 0].pow(2) + spectrogram[:, :, 1].pow(2)).pow(0.5)
        spectrogram = np.log1p(spectrogram.numpy())

        return spectrogram


class MelSpectrogram(object):
    """
    Create MelSpectrogram for a raw audio signal. This is a composition of Spectrogram and MelScale.

    Args: sample_rate, n_mels, window_size, stride, feature_extract_by
        sample_rate (int): Sample rate of audio signal. (Default: 16000)
        n_mels (int):  Number of mfc coefficients to retain. (Default: 80)
        window_size (int): window size (ms) (Default : 20)
        stride (int): Length of hop between STFT windows. (ms) (Default: 10)
        feature_extract_by (str): which library to use for feature extraction(default: librosa)
    """
    def __init__(self, sample_rate=16000, n_mels=80, window_size=20, stride=10, feature_extract_by='librosa'):
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.n_fft = int(sample_rate * 0.001 * window_size)
        self.hop_length = int(sample_rate * 0.001 * stride)
        self.feature_extract_by = feature_extract_by.lower()

        if self.feature_extract_by == 'torchaudio':
            self.transforms = torchaudio.transforms.MelSpectrogram(
                sample_rate=sample_rate,
                win_length=window_size,
                hop_length=self.hop_length,
                n_fft=self.n_fft,
                n_mels=n_mels
            )
            self.amplitude_to_db = torchaudio.transforms.AmplitudeToDB()

    def __call__(self, signal):
        if self.feature_extract_by == 'torchaudio':
            melspectrogram = self.transforms(torch.FloatTensor(signal))
            melspectrogram = self.amplitude_to_db(melspectrogram)
            melspectrogram = melspectrogram.numpy()

        elif self.feature_extract_by == 'librosa':
            melspectrogram = librosa.feature.melspectrogram(
                y=signal,
                sr=self.sample_rate,
                n_mels=self.n_mels,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            melspectrogram = librosa.amplitude_to_db(melspectrogram, ref=np.max)

        else:
            raise ValueError("Unsupported library : {0}".format(self.feature_extract_by))

        return melspectrogram


class MFCC(object):
    """
    Create the Mel-frequency cepstrum coefficients (MFCCs) from an audio signal.

    Args: sample_rate, n_mfcc, window_size, stride, feature_extract_by
        sample_rate (int): Sample rate of audio signal. (Default: 16000)
        n_mfcc (int):  Number of mfc coefficients to retain. (Default: 40)
        window_size (int): window size (ms) (Default : 20)
        stride (int): Length of hop between STFT windows. (ms) (Default: 10)
        feature_extract_by (str): which library to use for feature extraction(default: librosa)
    """
    def __init__(self, sample_rate=16000, n_mfcc=40, window_size=20, stride=10, feature_extract_by='librosa'):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_fft = int(sample_rate * 0.001 * window_size)
        self.hop_length = int(sample_rate * 0.001 * stride)
        self.feature_extract_by = feature_extract_by.lower()

        if self.feature_extract_by == 'torchaudio':
            self.transforms = torchaudio.transforms.MFCC(
                sample_rate=sample_rate,
                n_mfcc=n_mfcc,
                log_mels=True,
                win_length=window_size,
                hop_length=self.hop_length,
                n_fft=self.n_fft
            )

    def __call__(self, signal):
        if self.feature_extract_by == 'torchaudio':
            mfcc = self.transforms(torch.FloatTensor(signal))
            mfcc = mfcc.numpy()

        elif self.feature_extract_by == 'librosa':
            mfcc = librosa.feature.mfcc(
                y=signal,
                sr=self.sample_rate,
                n_mfcc=self.n_mfcc,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )

        else:
            raise ValueError("Unsupported library : {0}".format(self.feature_extract_by))

        return mfcc
