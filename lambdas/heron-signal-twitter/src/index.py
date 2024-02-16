import boto3
import os
import json
from string import Template


def lambda_handler(event, context):
    payload = json.loads(event["Records"][0]["body"])
    date = payload["date"]
    identityid = payload["identityID"]
    twitter_handle = payload["config"]["twitter-handle"]
    cam = payload["config"]["camera"]
    ssm = boto3.client("ssm")
    video_domain_param = ssm.get_parameter(
        Name="/heron/heron-video-domain", WithDecryption=False
    )
    video_domain = video_domain_param["Parameter"]["Value"]
    camtemplate = Template(
        "".join(
            (
                '<html><head><title>Live feed</title><meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                '<meta name="twitter:card" content="player" />',
                '<meta name="twitter:site" content="@$video_domain" />',
                '<meta name="twitter:title" content="Live Stream @$twitter_handle" />',
                '<meta name="twitter:description" content="@$twitter_handle is livestreaming $cam camera." />',
                '<meta name="twitter:image" content="https://$video_domain/live.png" />',
                '<meta name="twitter:player" content="https://$video_domain/$identityid/$date/$cam-container.html" />',
                '<meta name="twitter:player:stream" content="https://$video_domain/$identityid/$date/$cam-out.m3u8">',
                '<meta name="twitter:player:stream:content_type" content="video/mp4">',
                '<meta name="twitter:player:width" content="480" />',
                '<meta name="twitter:player:height" content="600" />',
                '<body><script src="https://${video_domain}/hls.js"></script>',
                '<center><video height="600" id="video" controls></video></center>',
                "<head>",
                "<script>",
                '  url = "https://${video_domain}/${identityid}/${date}/${cam}-out.m3u8";',
                '  var video = document.getElementById("video");',
                "  if (Hls.isSupported()) {",
                "    var hls = new Hls({",
                "      debug: true,",
                "    });",
                "    hls.loadSource(url);",
                "    hls.attachMedia(video);",
                "    hls.on(Hls.Events.MEDIA_ATTACHED, function () {",
                "      video.play();",
                "    });",
                "  }",
                '  else if (video.canPlayType("application/vnd.apple.mpegurl")) {',
                "    video.src = url;",
                '    video.addEventListener("canplay", function () {',
                "      video.play();",
                "    });",
                "  }",
                "  </script></body></html>",
            )
        )
    )
    camstring = camtemplate.substitute(
        date=date,
        identityid=identityid,
        twitter_handle=twitter_handle,
        cam=cam,
        video_domain=video_domain,
    )
    video_bucket_param = ssm.get_parameter(
        Name="/heron/video-bucket-name", WithDecryption=False
    )
    video_bucket = video_bucket_param["Parameter"]["Value"]
    indexobject.put(Body=indexstring, ContentType="text/html")
    camobject = s3.Object(
        bucket_name=video_bucket, key=identityid + "/" + date + "/" + cam + "-cam.html"
    )
    camobject.put(Body=camstring, ContentType="text/html")
