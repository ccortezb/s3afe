#!/usr/bin/env python
"""
S3afe stores a file on Amazon S3

The MIT License

Copyright (c) 2009 Fabian Topfstedt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import mimetypes, optparse, os, sys

try:
    from boto.exception import S3ResponseError
    from boto.s3.connection import S3Connection
except ImportError:
    sys.exit('Error: Please install boto first: "sudo easy_install boto"!')

def _get_envar_or_none(name):
    """
    Returns the environment variable with the given name or None.
    """
    if name in os.environ.keys():
        return os.environ[name]
    return None

def _guess_mimetype(filename, fallback='application/octet-stream'):
    """
    Tries to guess and return the correct mimetype for a filename, consulting
    the mimetypes module and (if needed) a hard coded dictionary of common
    mimetypes for audio/video/image.
    If every lookup fails, it returns the fallback mimetype.
    """
    mimetype = mimetypes.guess_type(filename)[0]
    if mimetype:
        return mimetype

    _av_mimetype_dict = {'.ra': 'audio/x-pn-realaudio',
        '.ecelp9600': 'audio/vnd.nuera.ecelp9600', '.dwg': 'image/vnd.dwg',
        '.h263': 'video/h263', '.h261': 'video/h261',
        '.ras': 'image/x-cmu-raster', '.h264': 'video/h264',
        '.mjp2': 'video/mj2', '.ram': 'audio/x-pn-realaudio',
        '.lvp': 'audio/vnd.lucent.voice', '.mid': 'audio/midi',
        '.ecelp7470': 'audio/vnd.nuera.ecelp7470', '.m1v': 'video/mpeg',
        '.mmr': 'image/vnd.fujixerox.edmics-mmr',
        '.xwd': 'image/x-xwindowdump','.avi': 'video/x-msvideo',
        '.bmp': 'image/bmp', '.aif': 'audio/x-aiff',
        '.fvt': 'video/vnd.fvt', '.wma': 'audio/x-ms-wma',
        '.wmx': 'video/x-ms-wmx', '.ico': 'image/vnd.microsoft.icon',
        '.wmv': 'video/x-ms-wmv', '.fst': 'image/vnd.fst',
        '.wbmp': 'image/vnd.wap.wbmp', '.fbs': 'image/vnd.fastbidsheet',
        '.jpe': 'image/jpeg', '.djv': 'image/vnd.djvu', '.jpg': 'image/jpeg',
        '.pct': 'image/x-pict', '.jpm': 'video/jpm', '.pcx': 'image/x-pcx',
        '.mpga': 'audio/mpeg', '.jpeg': 'image/jpeg',
        '.mdi': 'image/vnd.ms-modi', '.wav': 'audio/x-wav',
        '.m3u': 'audio/x-mpegurl', '.jp2': 'image/jp2',
        '.asx': 'video/x-ms-asf', '.mj2': 'video/mj2',
        '.asf': 'video/x-ms-asf', '.m3a': 'audio/mpeg',
        '.ecelp4800': 'audio/vnd.nuera.ecelp4800',
        '.pntg': 'image/x-macpaint', '.mp4v': 'video/mp4', '.ief': 'image/ief',
        '.mpg4': 'video/mp4', '.au': 'audio/basic',
        '.pbm': 'image/x-portable-bitmap', '.mp4a': 'audio/mp4',
        '.fpx': 'image/vnd.fpx', '.viv': 'video/vnd.vivo',
        '.kar': 'audio/midi', '.wax': 'audio/x-ms-wax',
        '.aiff': 'audio/x-aiff', '.aifc': 'audio/x-aiff',
        '.fli': 'video/x-fli', '.xpm': 'image/x-xpixmap',
        '.mpeg': 'video/mpeg', '.rmi': 'audio/midi',
        '.gif': 'image/gif', '.pic': 'image/x-pict', '.djvu': 'image/vnd.djvu',
        '.ppm': 'image/x-portable-pixmap',
        '.rmp': 'audio/x-pn-realaudio-plugin', '.mov': 'video/quicktime',
        '.cgm': 'image/cgm', '.qt': 'video/quicktime', '.mp2a': 'audio/mpeg',
        '.qti': 'image/x-quicktime', '.m2v': 'video/mpeg',
        '.npx': 'image/vnd.net-fpx', '.rlc': 'image/vnd.fujixerox.edmics-rlc',
        '.svgz': 'image/svg+xml', '.m2a': 'audio/mpeg',
        '.xbm': 'image/x-xbitmap', '.psd': 'image/vnd.adobe.photoshop',
        '.midi': 'audio/midi', '.tiff': 'image/tiff',
        '.btif': 'image/prs.btif', '.rgb': 'image/x-rgb',
        '.3g2': 'video/3gpp2', '.mxu': 'video/vnd.mpegurl',
        '.xif': 'image/vnd.xiff',
        '.tif': 'image/tiff', '.mpa': 'video/mpeg', '.mpg': 'video/mpeg',
        '.mpe': 'video/mpeg', '.pgm': 'image/x-portable-graymap',
        '.svg': 'image/svg+xml', '.g3': 'image/g3fax', '.cmx': 'image/x-cmx',
        '.dv': 'video/x-dv', '.dif': 'video/x-dv',
        '.eol': 'audio/vnd.digital-winds', '.3gp': 'video/3gpp',
        '.qtif': 'image/x-quicktime', '.wm': 'video/x-ms-wm',
        '.mac': 'image/x-macpaint', '.movie': 'video/x-sgi-movie',
        '.png': 'image/png', '.m4a': 'audio/mp4a-latm',
        '.pnm': 'image/x-portable-anymap', '.jpgm': 'video/jpm',
        '.snd': 'audio/basic', '.pnt': 'image/x-macpaint',
        '.m4v': 'video/mp4', '.m4u': 'video/vnd.mpegurl',
        '.pict': 'image/pict', '.dxf': 'image/vnd.dxf', '.jpgv': 'video/jpeg',
        '.m4p': 'audio/mp4a-latm', '.mp3': 'audio/mpeg', '.mp2': 'audio/mpeg',
        '.wvx': 'video/x-ms-wvx', '.mp4': 'video/mp4',
    }
    suffix = os.path.splitext(filename.lower())[-1]
    return _av_mimetype_dict.get(suffix, fallback)
    
def _upload(awskey, awssecret, filename, bucketname, keyname, acl, headers={}):
    """
    Uploads a file to S3
    """
    try: 
        conn = S3Connection(awskey, awssecret)
        bucket = conn.get_bucket(bucketname)
        key = bucket.new_key(keyname)
        headers['Content-Type'] = _guess_mimetype(filename)
        key.set_contents_from_filename(filename, headers)
        key.set_acl(acl)
    except S3ResponseError, exc:
        if exc.status == 403:
            sys.exit('Error: Please check your Amazon credentials!')
        elif exc.status == 404:
            sys.exit('Error: Your bucket does not exist (yet)')
    else:
        print 'Upload successful! Your file is now s3afe!'

def main():
    """
    Main method parses the options and triggers the upload.
    """
    optparser = optparse.OptionParser(prog='s3afe.py', version='0.1',
        description='S3afe stores a file on Amazon S3',
        usage='%prog -k [access key id] -s [secret access key] ' + \
            '-b [bucketname] -n [keyname] -f [file]')
    optparser.add_option('--aws_access_key_id', '-k', dest='awskey', 
        default=_get_envar_or_none('AWS_ACCESS_KEY_ID'))
    optparser.add_option('--aws_secret_access_key', '-s', dest='awssecret', 
        default=_get_envar_or_none('AWS_SECRET_ACCESS_KEY'))
    optparser.add_option('--filename', '-f', dest='filename')
    optparser.add_option('--bucketname', '-b', dest='bucketname')
    optparser.add_option('--keyname', '-n', dest='keyname')
    optparser.add_option('--acl', '-a', dest='acl', default='private',
        choices=['private', 'public-read', 'public-read-write', 
        'authenticated-read'])
    options, arguments = optparser.parse_args()
    if options.awskey and options.awssecret and options.filename and \
        options.bucketname and options.keyname and options.acl:
        if not os.path.isfile(options.filename):
            sys.exit('Error: The file does not exist!')
        _upload(options.awskey, options.awssecret, options.filename, 
            options.bucketname, options.keyname, options.acl)
    else:
        optparser.print_help()

if __name__ == '__main__':
    main()