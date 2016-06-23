import youtube_dl
import os
import urllib2
from wsgiref.simple_server import make_server
import urlparse


port = os.environ.get("PORT", "5000")


def video(video_id):
    ydl_opts = {
        'format': 'bestaudio/best'
    }
    ydl = youtube_dl.YoutubeDL()

    full_video_url = "%s%s" % ("https://www.youtube.com/watch?v=", video_id)

    with ydl:
        result = ydl.extract_info(
            full_video_url,
            download=False
        )

    formats = [{x['format_id'], x['format']} for x in result['formats']]

    for vid in result['formats']:
        if 'ext' in vid and 'abr' in vid and vid['ext'] == 'webm' and vid['abr'] == 160:
            return vid['url']

    for vid in result['formats']:
        if 'ext' in vid and 'abr' in vid and vid['ext'] == 'webm' and vid['abr'] == 128:
            return vid['url']

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result

    print video['url']
    return video['url']


def from_youtube(video_id):
    v = video(video_id)
    return v


def get_duration(duration):
    return video(duration).get('duration')


def stream(video_id, media_url, start_response):
    print "download from youtube"
    req = urllib2.Request(media_url, headers={'User-Agent': "Magic Browser"})
    u = urllib2.urlopen(req)
    print "request opened"

    meta = u.info()

    print "before file size"
    file_size = int(meta.getheaders("Content-Length")[0])
    print file_size
    file_size_dl = 0
    block_sz = 8192


    mp3file = urllib2.urlopen(media_url)

    headers = [('Content-type', 'audio/mp4'), ('Content-length', str(file_size)), ('Accept-Ranges', 'bytes')]
    write = start_response('200 OK', headers)

    # output = open('test','wb')
    # output.write(mp3file.read())
    # output.close()
    #
    # output = open('test','r')
    # yield mp3file.read()

    while True:
        chuck = mp3file.read(block_sz)
        if not chuck:
            print "break %s" % file_size_dl
            break
        yield chuck

    # print "2 way streaming..."



def hello_world_app(environ, start_response):
    d = urlparse.parse_qs(environ['QUERY_STRING'])
    video_id = d.get('yb', [False])[0]

    sig = d.get('sig', [False])[0]
    url = d.get('url', [False])[0]


    duration = d.get('duration', [False])[0]
    if sig and url:
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        # wo = youtube_dl.YoutubeDL().get_info_extractor('YoutubeIE')._decrypt_signature(sig, video_id, url);
        x = youtube_dl.YoutubeDL().get_ext(video_id)
        wo = x._decrypt_signature(sig, video_id, url)
        return [wo.encode("utf-8")]
    elif video_id:
        # print "got video id", video_id
        media_url = from_youtube(d.get('yb', [''])[0])
        return stream(video_id, media_url, start_response)
        # headers = [('Content-type', 'text/html')]
        # start_response('200 OK', headers)
        # return ["hello, world"]
    elif duration:
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return [str(get_duration(duration))]
    else:
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return ["hello, world"]

        # return ["hello, world"]


httpd = make_server('', int(port), hello_world_app)
print "Serving HTTP on port " + port + "..."

httpd.serve_forever()