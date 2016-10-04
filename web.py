from wsgiref.simple_server import make_server
import os
import urlparse
import youtube_dl
import urllib2
import json

from youtube_service import youtube_search

def youtube_dl_extract_info(video_id):

    full_video_url = "%s%s" % ("https://www.youtube.com/watch?v=", video_id)

    with youtube_dl.YoutubeDL() as ydl:
        result = ydl.extract_info(
            full_video_url,
            download=False
        )
    return result


def youtube_dl_extract(video_id, formats_ids):
    formats_ids_arr = formats_ids.split(',') if formats_ids else None
    info = youtube_dl_extract_info(video_id)
    url = info['formats'][0]['url']
    if formats_ids_arr:
        gen = (y['url'] for x in formats_ids_arr for y in info['formats'] if x == y['format_id'])
        try:
            url = next(gen)
        except StopIteration:
            url = info['formats'][0]['url']
    return url


def stream_media(media_url, start_response):
    req = urllib2.Request(media_url, headers={'User-Agent': "Magic Browser"})
    u = urllib2.urlopen(req)
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    file_size_dl = 0
    block_sz = 8192
    mp3file = urllib2.urlopen(media_url)

    headers = [('Content-type', 'audio/mp4'), ('Content-length', str(file_size)), ('Accept-Ranges', 'bytes')]
    write = start_response('200 OK', headers)

    while True:
        chuck = mp3file.read(block_sz)
        if not chuck:
            print "break %s" % file_size_dl
            break
        yield chuck


def hello_world_app(environ, start_response):
    params = urlparse.parse_qs(environ['QUERY_STRING'])

    video_id = params.get('id', [False])[0]
    formats = params.get('formats', [False])[0]

    info = params.get('info', [False])[0]
    q = params.get('q', [False])[0]

    sig = d.get('sig', [False])[0]
    url = d.get('url', [False])[0]

    if(not video_id and not q and not sig and not url):
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return ['youtube-dl heroku <a href="https://github.com/kobiburnley/youtube-dl/blob/heroku/README.md">read me</a>']

    try:
        if sig and url:
            headers = [('Content-type', 'text/html')]
            start_response('200 OK', headers)
            # wo = youtube_dl.YoutubeDL().get_info_extractor('YoutubeIE')._decrypt_signature(sig, video_id, url);
            x = youtube_dl.YoutubeDL().get_ext(video_id)
            wo = x._decrypt_signature(sig, video_id, url)
            return [wo.encode("utf-8")]
        elif(q):
            media_url = youtube_dl_extract(youtube_search(q, 1), formats)
            return stream_media(media_url, start_response)
        elif(info):
            result = youtube_dl_extract_info(video_id)
            headers = [('Content-type', 'text/html')]
            start_response('200 OK', headers)
            audio = [(x['format'], x['ext']) for x in result['formats']]
            return [json.dumps(audio)]
        else:
            media_url = youtube_dl_extract(video_id, formats)
            print media_url
            return stream_media(media_url, start_response)
    except:
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return ['An error occurred.']
    # print "2 way streaming..."



def xxhello_world_app(environ, start_response):
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

port = os.environ.get("PORT", "5000")
httpd = make_server('', int(port), hello_world_app)
print "Serving HTTP on port " + port + "..."

httpd.serve_forever()