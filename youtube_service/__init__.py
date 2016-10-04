#!/usr/bin/python

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDml0BqkOkiYZWEgtWTCbPmjXZLgfJDeYw"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(q, limit):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=q,
        part="id,snippet",
        maxResults=limit,
        type="video",
    ).execute()

    return ([search_result["id"]["videoId"] for search_result in search_response.get("items", [])])[0]

if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="as crazy as it is")
    argparser.add_argument("--max-results", help="Max results", default=1)
    args = argparser.parse_args()
    try:
        print youtube_search(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
