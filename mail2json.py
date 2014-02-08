# -*- coding: utf-8 -*-
"""mail2json.py 
Convert email to json. Extract media files.

* todo: test on wide range of intput. parse all email in archive.

* an interesting possibility for naming output
        cat x.mail \
	     | python mail2json.py parse \
	     | jq -M '"\(.from[0])/\(.media[0].md5)\(.media[0].suffix)"'
        "hoge@example.com/xxxxxxxxxxxxxxxxxxxx.mov"

  Shape the json for saving, then pass it to generic saver
  [ [path, data], .. ]

"""
import sys,os
import hashlib
import urllib
import base64
import email.parser
import email.message
import email.utils
import mimetypes
import json
from pprint import pprint

def mkdir_p(dirpath):
    """ mkdir -p 
    """
    try:
        os.makedirs(dirpath)
    except OSError, e:
        if e.errno==17:
            pass
        else:
            raise

# xx where is the lib to parse header values?
def parse_header_value(header_val):
    """video/quicktime;\n\tname=FAIL.MOV --> video/quicktime, { name: fail.mov }
    """

    terms=map(str.strip, header_val.lower().split(';'))
    what=terms.pop(0)
    detail=dict([ t.split('=') for t in terms ])
    return what, detail

def media_filename(ent):
    """extract media file name
    """

    _,detail=parse_header_value(ent.get('content-disposition'))
    filename=detail.get('filename')
    if filename:
        return filename

    _,detail=parse_header_value(ent.get_content_type())
    filename=detail.get('filename')
    if filename:
        return filename

    suffix=mimetypes.guess_extension(ent.get_content_type())
    filename='{name}.{suffix}'.format(name=ent.get_content_maintype(), suffix=suffix)
    return filename

# xxx not really parse but convert to jsonable
def convert(ent, d=0):
    """map from mime tree to json tree
    { headers: .., content: .. }
    """

    header=dict((k.lower(),v) for k,v in ent.items())

    if 'from' in header:
        from_name,from_addr=email.utils.parseaddr(header['from'])
        header['from']=dict(name=from_name, addr=from_addr)

    node=dict(header=header)

    data=ent.get_payload(decode=not ent.is_multipart())

    if isinstance(data, basestring):
        if ent.get_content_maintype()=='text':
            # xx deal with encoding.
            content=data
        else:
            # binary data (media) xx a premature decision..
            content=dict(md5=hashlib.md5(data).hexdigest(),
                         name=media_filename(ent), 
                         suffix=mimetypes.guess_extension(ent.get_content_type()),
                         bytes=base64.b64encode(data),
                         encoding='base64',
                         media=True,
                         )

    elif isinstance(data, list):
        content=[ convert(c, d+1) for c in data ]

    elif isinstance(data, email.message.Message):
        content=convert(data)

    else:
        content=None
        print >>sys.stderr, ('expected string or list',
                             type(data),
                             data,
                             data.as_string(), 
                             )
    node['content']=content
    return node

def extract(node):
    """extract interesting fields from mail tree
    """

    if 'from' in node['header']:
        yield 'from', node['header']['from']['addr']

    if 'message-id' in node['header']:
        yield 'message-id', node['header']['message-id']


    c=node['content']
    if isinstance(c, list):
        for gc in c:
            for x in extract(gc):
                yield x
    elif isinstance(c, basestring):
        # text payload
        yield 'text', c
    elif isinstance(c, dict):
        if c.get('media')==True:
            yield 'media', c
    else:
        assert False, ('unexpected', type(c))


def convert_plus(ent):
    """convert from mime to jsonable and set useful fields at the top level.
    """

    converted=convert(ent)

    field={}
    for k,v in extract(converted):
        field.setdefault(k,[]).append(v)

    converted.update(field)

    return converted

def parse(lose_media=True):
    """parse email into json that parallels the mime structure

        cat ~/Mail/inbox/42 | python mail2json.py parse | jq -M '.|keys'
        [
          "content",
          "from",
          "header",
          "media",
          "message-id",
          "text"
        ]
    """

    msg=convert_plus(email.parser.Parser().parse(sys.stdin))
    if lose_media:
        for media in msg['media']:
            media.pop('bytes')
    print json.dumps(msg)


def save(out_dir='.'):
    """save incoming email as json and binary asset files.
    cat ~/Mail/inbox/42 | mail2json.py save
    <out_dir>/<b64encodeed-message-id>/<file>.<suffix>
    <out_dir>/<b64encodeed-message-id>/md.json
    """

    md=convert_plus(email.parser.Parser().parse(sys.stdin))

    # msg dir
    name=urllib.quote(md['message-id'][0])
    msg_dir=os.path.abspath(os.path.join(out_dir, name))
    mkdir_p(msg_dir)

    # save media files
    for media in md['media']:
        assert media['encoding']=='base64' # xx
        content=base64.b64decode(media.pop('bytes'))
        media_path=os.path.join(msg_dir, media['name'])
        file(media_path, 'w').write(content)
        print media_path

    # save md
    md_path=os.path.join(msg_dir, 'md.json') # xx could theoretically collide with media..
    file(md_path, 'w').write(json.dumps(md))
    print md_path

def main():

    import baker

    baker.command(parse)
    baker.command(save)

    baker.run()


if __name__=='__main__':

    main()
