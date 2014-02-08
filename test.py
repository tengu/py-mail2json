import sys,os
import unittest
from pprint import pprint
import json
from subprocess import Popen, PIPE

class Test(unittest.TestCase):
    
    def test_save(self):
        """save
        cat testdata/mail-001 | python mail2json.py save x.out
        """

        out,err=Popen("cat testdata/mail-001 | python mail2json.py save x.out", 
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        assert not err, err
        output=[ l.split('/x.out/')[1] for l in out.strip('\n').split('\n') ]
        # 
        # output: json file representing the mime structure of email and any attachments are printed.
        # 
        self.assertEqual(output, 
                         ['%3CDEADBEEF-F52B-4B36-85D0-A85CF7B02C40%40i.example.com%3E/img_1871.mov',
                          '%3CDEADBEEF-F52B-4B36-85D0-A85CF7B02C40%40i.example.com%3E/md.json'])
        # 
        # output directory layout
        # 
        self.assertEqual(
            list(os.walk('./x.out')),
            [('./x.out', 
              ['%3CDEADBEEF-F52B-4B36-85D0-A85CF7B02C40%40i.example.com%3E'], 
              []), 
             ('./x.out/%3CDEADBEEF-F52B-4B36-85D0-A85CF7B02C40%40i.example.com%3E', 
              [], 
              ['md.json', 'img_1871.mov'])])
        # 
        # json-ified mime message looks like this
        # 
        self.assertEqual(
            json.load(file('x.out/%3CDEADBEEF-F52B-4B36-85D0-A85CF7B02C40%40i.example.com%3E/md.json')),
            {u'content': [{u'content': u'\n\n',
                           u'header': {u'content-transfer-encoding': u'7bit',
                                       u'content-type': u'text/plain;\n\tcharset=us-ascii'}},
                          {u'content': {u'encoding': u'base64',
                                        u'md5': u'762bc5d5715b6102111346c6069c23e5',
                                        u'media': True,
                                        u'name': u'img_1871.mov',
                                        u'suffix': u'.mov'},
                           u'header': {u'content-disposition': u'attachment;\n\tfilename=IMG_1871.MOV',
                                       u'content-transfer-encoding': u'base64',
                                       u'content-type': u'video/quicktime;\n\tname=IMG_1871.MOV'}}],
             u'from': [u'tengu@example.com'],
             u'header': {u'content-transfer-encoding': u'7bit',
                         u'content-type': u'multipart/mixed; boundary=Apple-Mail-E670757C-566F-46A7-82A7-DEADBEEF',
                         u'date': u'Fri, 7 Feb 2014 09:07:23 +0900',
                         u'delivered-to': u'skydog@example.com',
                         u'from': {u'addr': u'tengu@example.com', u'name': u'Tengu'},
                         u'message-id': u'<DEADBEEF-F52B-4B36-85D0-A85CF7B02C40@i.example.com>',
                         u'mime-version': u'1.0 (1.0)',
                         u'received': u'from [10.0.1.4] ([100.100.100.100] [100.100.100.100])\n          by hoge.i.example.com with ESMTP\n          id <20140207000724308.PHJN.36465.hoge.i.example.com@hoge.mailsv.example.com>\n          for <skydog@example.com>; Fri, 7 Feb 2014 09:07:24 +0900',
                         u'return-path': u'<tengu@example.com>',
                         u'to': u'skydog@example.com',
                         u'x-mailer': u'iPhone Mail (11B554a)',
                         u'x-original-to': u'skydog@example.com',
                         u'x-sb-service': u'Virus-Checked'},
             u'media': [{u'encoding': u'base64',
                         u'md5': u'762bc5d5715b6102111346c6069c23e5',
                         u'media': True,
                         u'name': u'img_1871.mov',
                         u'suffix': u'.mov'}],
             u'message-id': [u'<DEADBEEF-F52B-4B36-85D0-A85CF7B02C40@i.example.com>'],
             u'text': [u'\n\n']}
            )

    def test_parse(self):
        """parse"""
        pass                    # implement me.

if __name__=='__main__':

    unittest.main()

