#!/bin/bash

export PATH=/share/dev/tofu/venv/bin:$PATH

cd /share/dev/tofu/
scrapy crawl shf
scrapy crawl ine
scrapy crawl czc
scrapy crawl dce
scrapy crawl cfe
scrapy crawl sse
scrapy crawl szse
scrapy crawl swindex -a t1=today

# update symbol_temp for CZC exchange
./manage.py update_symbol_temp

./manage.py minutebar_tqsdk --e=shf
./manage.py minutebar_tqsdk --e=ine
./manage.py minutebar_tqsdk --e=czc
./manage.py minutebar_tqsdk --e=dce
./manage.py minutebar_tqsdk --e=cfe

# update whether contract is active
./manage.py update_active
