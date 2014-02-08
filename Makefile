
all:

clean:
	rm -fr ve build dist *.egg-info

p:
	cat testdata/mail-001 \
	| python mail2json.py parse \
	| jq -M '.|keys'

t:
	@# {m.from.addr|sender_id}/{m.media[0].md5}.{m.media[0].suffix}
	cat testdata/mail-001 \
	| python mail2json.py parse \
	| jq -M '"\(.from[0])/\(.media[0].md5)\(.media[0].suffix)"'

s:
	cat testdata/mail-001 \
	| python mail2json.py save x.out

hoge:
	cat testdata/mail-001 \
	| python mail2json.py \
		hoge x.out mysql://root:pumpkin@localhost/hoge 'select addr,id from sender;'

test:
	python test.py

ve:
	virtualenv ve

install:
	ve/bin/python setup.py install
