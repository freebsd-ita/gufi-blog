Title: ELK First part 
Date: 2015-12-16 08:25
Category: How-Tos
Tags: ELK, ElasticSearch, Kibana, Logstash, Logging, Graphs
Authors: Davide D'Amico
Summary: How to setup the ELK (ElasticSearch, Logstash, Kibana) stack on FreeBSD

### 0. Introduction

ELK is the new black, it seems, so let's give it a try.

Suppose that we have a bunch of servers where a simple application ir running smoothly:

```
operator@srv1 $ /usr/local/bin/myapp -c /usr/local/etc/myapp.cfg --log /var/log/myapp.log
```

I know, myapp is completely uncool (and boring), so let's make some noise.

Suppose that we want a dashboard to inspect _/var/log/myapp.log_ coming
from all servers so basically we need:

* to search within logfiles;
* to filter per host/datetime/colour_of_my_tshirt;
* to create some nice dashboard to see how our new iMac 5k will render it.

You have basically two choices:

1. convince your colleagues to help you logging on each server, learn to regexp and to dashboard (
then you'll spend a lot of money in beer for your colleagues), or
2. use an ELK stack (and buy beers only for yourself).

We will follow the second approach, because a real sysadmin doesn't have colleagues, only enemies.

ELK stands for ElasticSearch/Logstash/Kibana because well, we will need all of them.

### 1. Install Fest

Let's install our favourite FreeBSD 10.2, then:

1. textproc/elasticsearch
2. sysutils/logstash
3. textproc/kibana43
4. www/nginx

You know how to install a pkg/port, right?
If not, it's as easy as (as root):

1. cd /usr/ports/ports-mgmt/portmaster
2. make install clean
3. rehash    # if you are using (t)csh
4. portmaster elasticsearch logstash kibana43 nginx
5. spend some time on seeing a black terminal (this is the time you can post some screenshot on facebook
saying something like 'OMG, I'm so nerd')

Ok, now we need to enable them (in order to start or restart):

```
operator@elk:~ % echo 'elasticsearch_enable="YES"' > /etc/rc.conf.d/elasticsearch
operator@elk:~ % printf 'logstash_enable="YES"\nlogstash_log="YES"\nlogstash_log_file="/var/log/logstash.log"' > /etc/rc.conf.d/logstash
operator@elk:~ % echo 'kibana_enable="YES"' > /etc/rc.conf.d/kibana
operator@elk:~ % echo 'nginx_enable="YES"' > /etc/rc.conf.d/nginx
```

Hold on, man. It's not time to start up anything yet.

### 2. ElasticSearch

Let's start with **ElasticSearch**: we will have a single node instance because, you know,
myapp is not logging so much (so no cluster for now, sorry).

Let's see what we have to change in _/usr/local/etc/elasticsearch/elasticsearch.yml_ (don't worry,
really a few things):

```
# ----------------------------------- Paths ------------------------------------
#
# Path to directory where to store the data (separate multiple locations by comma):
#
# path.data: /path/to/data
path.data: /var/db/elasticsearch
#
# Path to log files:
#
# path.logs: /path/to/logs
path.logs: /var/log/elasticsearch
#
[...]
# ---------------------------------- Network -----------------------------------
#
# Set the bind address to a specific IP (IPv4 or IPv6):
#
network.host: 127.0.0.1
#
# Set a custom port for HTTP:
#
http.port: 9100
#
# For more information, see the documentation at:
# <http://www.elastic.co/guide/en/elasticsearch/reference/current/modules-network.html>
```

Basically we are changing where to save data, indexes and logs and to listen on 127.0.0.1:9100

Now we can finally start using our cpu cycles, so let's start ElasticSearch with:

```
root@elk $ service elasticsearch start
```

Check its logfile (and/or use ps/pgrep) to see if elasticsearch is happy.

### 3. LogStash

Time to run logstash, so let's open _/usr/local/etc/logstash/logstash.conf_ and replace all the content with:

```
input {
    lumberjack {
        port => 4433
        ssl_certificate => "/usr/local/etc/logstash/logstash-forwarder.crt"
        ssl_key => "/usr/local/etc/logstash/logstash-forwarder.key"
    }
}

filter {
  if [type] == "myapp" {
    grok {
      match => { message => "%{TIME:event_time} %{DATA:process}:%{GREEDYDATA:message}" }
    }
  }
}

output {
    elasticsearch { hosts => ["localhost:9100"] }
    stdout { codec => rubydebug }
}
```

What's that lumberjack thing? It's a protocol, used primarly via the logstash-forwarder.

On each server you will install and run a logstash-forwarder (i.e. https://github.com/didfet/logstash-forwarder-java)
that will 'take care' of our _/var/log/myapp.log_ sending it to our logstash server (the first time will send the entire file, then it will send only deltas).

On your servers you will have to start something like:

```
/usr/local/bin/java -jar logstash-forwarder-java-X.Y.Z.jar -config /usr/local/etc/logstash-agent.json
```

where logstash-agent.json is:

```
{
  "network": {
    "servers": [ "XXX.YYY.WWW.ZZZ:4433" ],
    "ssl ca": "/usr/local/etc/logstash/keystore.jks",
    "timeout": 15
  },
  "files": [
    {
      "paths": [ "/var/log/myapp.log" ],
      "fields": { "type": "myapp" }
    }
  ]
}
```

Here we are configuring our logstash endpoint (XXX.YYY.WWW.ZZZ), its port (4433), the keystore that will be used to encrypt the traffic, the file that will
be 'monitored' and we will associate a tag to each event sent.

Awesome, isn't it?

Unfortunately logstash-forwarder-java is not in the freebsd ports tree (you will find sysutils/logstash-forwarder, written in Go), but I don't want to compile and install
Go for this, so I'll use the java one.

A few words on the SSL stuff

1. Let's create key and cert on our elk server with:

	```
	openssl req -x509 -batch -nodes -newkey rsa:2048 -keyout /usr/local/etc/logstash/logstash-forwarder.key -out /usr/local/etc/logstash/logstash-forwarder.crt
	```

2. Create a keystore based on logstash-forwarder.crt:

	```
	keytool -importcert -trustcacerts -file /usr/local/etc/logstash/logstash-forwarder.crt -alias ca -keystore /usr/local/etc/logstash/keystore.jks
	```

	(keytool will ask for a password, this is a good moment to remember how much you hate systemd)

3. Distribute the jks on all clients
4. Grab a beer and relax

Now you can start logforwarder-java on your clients and logstash on your server with:

```
root@elk $ service logstash start
```

then take a look at _/var/log/logstash.log_, our planet should still be safe.


