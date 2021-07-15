import urllib
import requests
import schedule
import time
import os
import socket
import json
from picamera import PiCamera
from time import sleep
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image
from time import gmtime, strftime

import datetime
i = datetime.datetime.now()

interval = 60*60;

amazon_s3_bucket = "hydro-garden"
amazon_access_key_id = "AKIAIQJ2QJU3O7RHOLFQ"
amazon_secret_access_key = "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"

camera = PiCamera()
camera.start_preview()

def Still():

        millis = int(round(time.time() * 1000))
        file_name = '%s.png' % (millis)
        source_path = '/home/pi/captures/%s' % file_name
        final_path = '/home/pi/captures/final-%s' % file_name
        # camera.drc_strength = 'low'
        camera.capture( source_path )
        print "taking photo %s" % source_path

        # update image
        import datetime
        today = datetime.date.today()
        from subprocess import call
        call([
                "convert",
                "-pointsize",
                "32",
                source_path,
                "label:" + str(datetime.datetime.now()),
                "-gravity",
                "Center",
                "-append",
                source_path
        ])

        # get grafana snapshots
        resp = requests.get("https://api.hostedgraphite.com/api/v2/grafana/render/?target=temp&target=outside_temp&target=pump&target=lamp&target=humidity&target=outside_humidity&height=480&width=640&from=-48h", auth=('11b54d27-e4e9-4c1c-b40a-eeca65f453a9','' ) )
        metric_path = "/home/pi/captures/metrics.png"
        urllib.urlretrieve( resp.text, metric_path )

        # merge images
        images = map(Image.open, [source_path, metric_path])
        widths, heights = zip(*(i.size for i in images))

        total_width = max(widths)
        max_height = sum(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        y_offset = 0
        for im in images:
          new_im.paste(im, (0,y_offset))
          y_offset += im.size[1]

        new_im.save( final_path )

        # upload picture
        c = S3Connection( amazon_access_key_id, amazon_secret_access_key )
        b = c.get_bucket( amazon_s3_bucket )
        k = Key( b )
        k.key = "stills/" + file_name
        k.set_contents_from_filename( final_path )
        k.make_public()

        # cleanup
        os.remove( source_path )
        os.remove( metric_path )
        os.remove( final_path )

        conn = socket.create_connection(("94a66475.carbon.hostedgraphite.com", 2003))
        conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.camera.stillshot 1\n")
        conn.close()

        print( "Still processed: %s" % source_path )

while (True):
    try:
        schedule.every().hour.do( Still )
        while 1:
                schedule.run_pending()
                time.sleep(1)
    except Exception as err:
        print err

camera.stop_preview()