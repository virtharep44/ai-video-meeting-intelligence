import os
import numpy as np
from pydub import AudioSegment

def diarize_audio(audio_path: str, segment_length: int = 10) -> list:
    try:
        audio = AudioSegment.from_wav(audio_path)
        duration = len(audio) / 1000
        
        speakers = []
        speaker_count = 0
        prev_energy = None
        threshold = 500
        
        for start in range(0, int(duration), segment_length):
            end = min(start + segment_length, int(duration))
            segment = audio[start*1000:end*1000]
            
            samples = np.array(segment.get_array_of_samples()).astype(np.float32)
            energy = np.sqrt(np.mean(samples**2))
            
            if prev_energy is None or abs(energy - prev_energy) > threshold:
                speaker_count = (speaker_count + 1) % 2
            
            speakers.append({
                "speaker": f"SPEAKER_{speaker_count}",
                "start": round(start, 2),
                "end": round(end, 2)
            })
            prev_energy = energy
        
        return speakers
        
    except Exception as e:
        print(f"Diarization error: {e}")
        return []