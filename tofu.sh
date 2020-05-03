#!/bin/bash

export PATH=/share/dev/tofu/venv/bin:$PATH

cd /share/dev/tofu/
scrapy crawl shf -a t1=20200428
scrapy crawl ine -a t1=20200428
scrapy crawl czc -a t1=20200428
scrapy crawl dce -a t1=20200428
scrapy crawl cfe -a t1=20200428

# update symbol_temp for CZC exchange
./manage.py update_symbol_temp

./manage.py minutebar_tqsdk

# update whether contract is active
./manage.py update_active
