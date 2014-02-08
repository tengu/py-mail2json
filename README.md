py-mail2json
============

convert email to json


        cat testdata/mail-001 \
        	| python mail2json.py parse \
        	| jq -M '.|keys'
        [
          "content",
          "from",
          "header",
          "media",
          "message-id",
          "text"
        ]
