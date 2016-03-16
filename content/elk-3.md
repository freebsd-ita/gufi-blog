Title: ELK Stack (Elasticsearch, Logstash and Kibana) on FreeBSD - Part 3
Date: 2016-02-23 06:44
Category: How-Tos
Tags: ELK, ElasticSearch, Kibana, Logstash, FreeBSD, Logging, Graphs
Authors: Davide D'Amico
Summary: Third part on the series of how-to's on the ELK (ElasticSearch, Logstash, Kibana) stack on FreeBSD


> This article is the third of a three-piece how to.
>
> You can find the first part [here]({filename}/elk-1.md)
> and the second part [here]({filename}/elk-2.md)
>

To create alerts for our ELK setup, we can use different methods.
The one I will show you is based on ElastAlert from Yelp.


1. Let's install ElastAlert (no port is available, so I will install it manually in a virtualenv).


We need to be root (and use bash - for the virtualenv)

```bash

sudo su

```


Install py-virtualenv

```bash

portmaster devel/py-virtualenv

```

Create and use a virtualenv

```bash
virtualenv /usr/local/elastalert
source /usr/local/elastalert/bin/activate
mkdir -p /usr/local/elastalert/etc
```

Download and install the repo


```bash
mkdir /tmp/elastalert
cd /tmp/elastalert
git clone https://github.com/Yelp/elastalert.git
cd elastalert
python setup.py build
pip install setuptools --upgrade
python setup.py install
pip install -r requirements.txt
# the first time it will (probably) fail due to an error related to argparse
pip install -r requirements.txt

Create the elastalert config file in __/usr/local/elastalert/etc/config.yml__

```yaml
rules_folder: /usr/local/elastalert/etc/rules

# The unit can be anything from weeks to seconds
run_every:
  minutes: 1

# ElastAlert will buffer results from the most recent
# period of time, in case some log sources are not in real time
buffer_time:
  minutes: 15
# The elasticsearch hostname for metadata writeback
# Note that every rule can have it's own elasticsearch host
es_host: 127.0.0.1
# The elasticsearch port
es_port: 9100
# Optional URL prefix for elasticsearch
#es_url_prefix: elasticsearch
# Connect with SSL to elasticsearch
use_ssl: False

# The index on es_host which is used for metadata storage
# This can be a unmapped index, but it is recommended that you run

# elastalert-create-index to set a mapping
writeback_index: elastalert_status

# If an alert fails for some reason, ElastAlert will retry
# sending the alert until this time period has elapsed
alert_time_limit:
  days: 2
```

Create the rules directory

```bash
mkdir -p /usr/local/elastalert/etc/rules
```

Create an alert (frequency based) that will send an email if more than 9 events will happen in 1 hour with status: 404 and type: nginx

In __/usr/local/elastalert/etc/rules/frequency_nginx_404.yaml__

```yaml

name: Large Number of 404 Responses
es_host: 127.0.0.1
es_port: 9100
index: logstash-*
filter:
  - term:
      - status: 404
  - term:
      - type: nginx
type: frequency
num_events: 10
timeframe:
  hours: 1
alert:
  - "email"
email:
- "spaghetti.with.meatballs@are.not.italian.at.all"

```

Create an index for metadata storage

```bash


(elastalert)[dave@elk /usr/local/elastalert]$ ./bin/elastalert-create-index
Enter elasticsearch host: 127.0.0.1
Enter elasticsearch port: 9100
Use SSL? t/f: f
Enter optional basic-auth username:
Enter optional basic-auth password:
Enter optional Elasticsearch URL prefix:
New index name? (Default elastalert_status)
Name of existing index to copy? (Default None)
New index elastalert_status created
Done!

```

Test our rule

```bash
(elastalert)[dave@elk /usr/local/elastalert]# ./bin/elastalert-test-rule etc/rules/frequency_nginx_404.yaml
[...]
```

Launch ElastAlert (in a tmux session, maybe?)

```bash
(elastalert)[dave@elk /usr/local/elastalert]$ ./bin/elastalert --config etc/config.yml --debug
INFO:elastalert:Starting up
INFO:elastalert:Queried rule Large Number of 404 Responses from 2016-02-16 17:22 CET to 2016-02-16 17:37 CET: 9 hits
[...]
INFO:elastalert:Ran Large Number of 404 Responses from 2016-02-16 17:22 CET to 2016-02-16 17:37 CET: 9 query hits, 0 matches, 0 alerts sent
```

<evil>
Let's generate some **http/404** (again, it's time to let the world know how much you agree with the systemd architecture)
</evil>

```
INFO:elastalert:Sleeping for 59 seconds
INFO:elastalert:Queried rule Large Number of 404 Responses from 2016-02-16 17:23 CET to 2016-02-16 17:38 CET: 10 hits
[...]
INFO:elastalert:Alert for Large Number of 404 Responses at 2016-02-16T16:38:00.680Z:
INFO:elastalert:Large Number of 404 Responses

At least 10 events occurred between 2016-02-16 16:38 CET and 2016-02-16 17:38 CET

@timestamp: 2016-02-16T16:38:00.680Z
@version: 1
_id: AVLq8hzNIkvyITAb373u
_index: logstash-2016.02.16
_type: nginx
agent: "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
bytes: 564
file: /var/log/nginx/nginx.access.log
host: [
    "blog.gufi.org"
]
message: xxx.xxx.xxx.xxx - blog.gufi.org [16/Feb/2016:17:37:57 +0100] "GET /test/foo/bar HTTP/1.1" 404 564 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36" "141.101.98.223" [-] "-" "-" "0.000"
offset: 1853436
remote_addr: xxx.xxx.xxx.xxx
request_httpversion: 1.1
request_time: 0.000
request_url: /test/foo/bar
request_verb: GET
status: 404
time_local: 16/Feb/2016:17:37:57 +0100
type: nginx
upstream_addr: -
xforwardedfor: "xxx.xxx.xxx.xxx"
```

Once removed the **--debug** parameter, we will start receiving e-mails. (yay!)


Before leaving
--------------

Few words to answer the question *'Ok, so how can this be useful to me/my company/my fiancee?'*

Many of us, sysadmins (or gods), have used **Nagios** and its derivatives (Zabbix/Icinga) for years but it's time now to say Nagios goodbye (and thanks for all the fish).


Tools like ELK or **OpenTSDB** (or InfluxDB/KairosDB) and **Bosun**/**Prometheus** have been created to give us a new generation of more suitable tools in environments that become bigger and bigger: I know, to create and manage an ELK stack (or a OpenTSDB/Grafana/Bosun stack) requires more effort than to manage a Nagios box, but it's an overhead you will soon get used to (and probably you already have an hadoop/hbase installation to manage, right?).

In this case, having an in house tool to parse your application logs will allow you:

* to blame developers if something goes wrong (just in case you need further reasons to)
* to not give them access to any production machines (yes, they will ask to, anyway)
* to be able to search all your logs at once (like grepping on a syslog-ng basedir with improved superpowers) or with a better semantics (i.e. spotting trends)
* to create dashboards (for your management, you know...) or alerts (because you need a good reason to skip that boring meeting, right?)

ELK engineers suggest to use ELK not only for **DEBUG**/**ERROR** messages, but also for the application ones: this will add a great value to your logs and, once again, the world will be a safer place thanks to you, too.

There were no screenshots in this article, so that's a potato for you [here](http://saibateku.net/potato/potato.jpg)
