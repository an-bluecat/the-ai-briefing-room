from pydub import AudioSegment

def custom_bgm_loop_with_podcast_smooth_transitions(podcast_path, bgm_path):
    # Load the podcast and BGM
    podcast = AudioSegment.from_file(podcast_path)
    bgm = AudioSegment.from_file(bgm_path)

    # Extract intro (first 3 seconds), middle, and outro (last 10 seconds) of BGM
    bgm_intro = bgm[:3000] 
    bgm_outro = bgm[-13000:-5000]
    bgm_middle = bgm[3000:-13000] 

    bgm_intro = bgm_intro - 15 
    bgm_outro = bgm_outro - 18
    bgm_middle = bgm_middle - 22

    # Calculate required length for the middle BGM to loop
    middle_duration = len(podcast) - len(bgm_intro) - 1000

    # Loop the middle part of the BGM to cover the podcast duration
    bgm_middle_loop = bgm_middle * (middle_duration // len(bgm_middle) + 1)
    bgm_middle_loop = bgm_middle_loop[:middle_duration]  # Trim to exact duration

    # Combine intro, looped middle, and outro of BGM
    bgm_full = bgm_intro + bgm_middle_loop + bgm_outro

    # Overlay the podcast onto the BGM starting right after the intro
    final_mix = bgm_full.overlay(podcast, position=len(bgm_intro))

    # Export the final mix to a new file
    final_mix.export("final_podcast.mp3", format="mp3")

# Replace 'your_podcast.mp3' and 'your_bgm.mp3' with your actual file paths
custom_bgm_loop_with_podcast_smooth_transitions('output/speech_20240419133621.mp3', 'bgm.mp3')