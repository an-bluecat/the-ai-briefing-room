from pydub import AudioSegment

def custom_bgm_loop_with_podcast_smooth_transitions(podcast_path, bgm_path):
    # Load the podcast and BGM
    podcast = AudioSegment.from_file(podcast_path)
    bgm = AudioSegment.from_file(bgm_path)

    # Extract intro (first 3 seconds), middle, and outro (last 10 seconds) of BGM
    bgm_intro = bgm[:3000]  # first 3 seconds
    bgm_outro = bgm[-10000:]  # last 10 seconds
    bgm_middle = bgm[3000:-10000]  # middle part, excluding first 3 and last 10 seconds

    # Apply a smooth fade out to the intro over the last 1500 milliseconds (1.5 seconds)
    bgm_intro = bgm_intro.fade_out(1500)

    # Apply fade in to the outro (fade from lower volume to normal over 10 seconds)
    bgm_outro = bgm_outro.fade_in(10000)

    # Reduce the volume of the middle part to keep it lower during the podcast
    bgm_middle = bgm_middle - 15  # Reduce volume by 15 dB

    # Calculate required length for the middle BGM to loop
    middle_duration = len(podcast) - len(bgm_intro) - len(bgm_outro)

    # Loop the middle part of the BGM to cover the podcast duration
    bgm_middle_loop = bgm_middle * (middle_duration // len(bgm_middle) + 1)
    bgm_middle_loop = bgm_middle_loop[:middle_duration]  # Trim to exact duration

    # Combine intro, looped middle, and outro of BGM
    bgm_full = bgm_intro + bgm_middle_loop + bgm_outro

    # Overlay the podcast onto the BGM starting right after the intro
    final_mix = bgm_full.overlay(podcast, position=len(bgm_intro))

    # Export the final mix to a new file
    final_mix.export("final_podcast_with_custom_bgm_smooth_transitions.mp3", format="mp3")

# Replace 'your_podcast.mp3' and 'your_bgm.mp3' with your actual file paths
custom_bgm_loop_with_podcast_smooth_transitions('output/speech_20240417220216.mp3', 'bgm.mp3')