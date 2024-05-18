import os
import googleapiclient.discovery
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def youtube_search(query, max_results, api_key, region_code):
    # Build the YouTube service
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # Perform the search
    request = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        regionCode=region_code
    )
    response = request.execute()

    # Extract and return relevant data
    video_data = []
    for item in response.get("items", []):
        if item["id"]["kind"] == "youtube#video":  # Check if the item is a video
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_title = item["snippet"]["channelTitle"]

            # Fetch video statistics
            stats_request = youtube.videos().list(
                part="statistics",
                id=video_id
            )
            stats_response = stats_request.execute()
            if stats_response["items"]:
                stats = stats_response["items"][0]["statistics"]
                view_count = stats.get("viewCount", "0")
                like_count = stats.get("likeCount", "0")

                video_data.append({
                    "title": title,
                    "view_count": view_count,
                    "like_count": like_count
                })
    df = pd.DataFrame(video_data)
    return df

if __name__ == "__main__":
    # In case it doesn't work properly with environment variable
    # with open("API_KEY.txt", "r") as f:
    #     API_KEY = f.read()
    API_KEY = os.environ.get('API_KEY')

    if not API_KEY:
        raise ValueError("No API key found in environment variables")

    QUERY = 'programare'  # The chosen domain
    MAX_RESULTS = 5  # Maximum number of results
    REGION_CODE = 'RO'  # The region code (e.g., 'RO' for Romania)

    videos = youtube_search(QUERY, MAX_RESULTS, API_KEY, REGION_CODE)

    if videos is not None:
        print("Video report:")
        print(videos)
        videos.to_csv("video_report.csv", index=False)
    videos = pd.read_csv('video_report.csv')

    # Convert view_count and like_count to numeric values
    videos['view_count'] = pd.to_numeric(videos['view_count'])
    videos['like_count'] = pd.to_numeric(videos['like_count'])

    # Sort data by view count
    videos = videos.sort_values(by='view_count', ascending=False)

    # Plotting
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # Plot view counts
    axes[0].bar(videos['title'], videos['view_count'], color='blue')
    axes[0].set_title('View Count')
    axes[0].set_xlabel('Video Title')
    axes[0].set_ylabel('Views')
    axes[0].set_xticks([])
    axes[0].tick_params(axis='x', rotation=45)
    for index, value in enumerate(videos['view_count']):
        axes[0].text(index, value, str(value), ha='center', va='bottom')

    # Plot like counts
    axes[1].bar(videos['title'], videos['like_count'], color='red')
    axes[1].set_title('Like Count')
    axes[1].set_xlabel('Video Title')
    axes[1].set_ylabel('Likes')
    axes[1].tick_params(axis='x', rotation=45)
    for index, value in enumerate(videos['like_count']):
        axes[1].text(index, value, str(value), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

