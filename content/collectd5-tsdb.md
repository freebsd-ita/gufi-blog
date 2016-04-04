Title: Enabling write_tsdb in net-mgmt/collectd5
Date: 2016-04-04 16:10
Category: How-Tos
Tags: Collectd, FreeBSD, Portmaster, Ports, Net-Mgmt, Patch
Summary: Enabling write_tsdb output plugin in net-mgmt/collectd5

To collectd metrics from servers I use **databases/opentsdb** and **net-mgmt/collectd5**.
Collectd5 can natively use an OpenTSDB database as Output but when you use the FreeBSD port,
this output plugin isn't included (don't ask me why): here is how to include it.

Basically we need to apply to Makefile this patch:
```
--- Makefile.orig       2016-04-04 07:04:56.231162000 -0400
+++ Makefile    2016-04-04 06:58:51.146676000 -0400
@@ -24,7 +24,8 @@

 OPTIONS_DEFINE=                CGI DEBUG GCRYPT LOGSTASH VIRT
 OPTIONS_GROUP=         INPUT OUTPUT
-OPTIONS_GROUP_OUTPUT=  KAFKA MONGODB NOTIFYDESKTOP NOTIFYEMAIL RIEMANN RRDTOOL
+OPTIONS_GROUP_OUTPUT=  KAFKA MONGODB NOTIFYDESKTOP NOTIFYEMAIL RIEMANN RRDTOOL \
+                       TSDB
 OPTIONS_GROUP_INPUT=   CURL CURL_JSON CURL_XML DBI IPMI JSON MEMCACHEC \
                        MODBUS MYSQL NUTUPS OLSRD ONEWIRE OPENLDAP \
                        PERL PGSQL PINBA PING PYTHON RABBITMQ REDIS ROUTEROS \
@@ -67,6 +68,7 @@
 STATGRAB_DESC=         Enable statgrab-based plugins (interface, etc)
 STATSD_DESC=           Enable statsd plugin
 TOKYOTYRANT_DESC=      Enable tokyotyrant plugin
+TSDB_DESC=             Enable tsdb plugin
 VARNISH_DESC=          Enable varnish 4.x cache statistics
 VIRT_DESC=             Enable libvirt plugin (requires XML)
 XML_DESC=              Enable XML plugins
@@ -247,6 +249,8 @@
 TOKYOTYRANT_CONFIGURE_ENABLE=  tokyotyrant
 TOKYOTYRANT_CONFIGURE_WITH=    libtokyotyrant=${LOCALBASE}

+TSDB_CONFIGURE_ENABLE=         write_tsdb
+
 VARNISH_LIB_DEPENDS=           libvarnishapi.so:${PORTSDIR}/www/varnish4
 VARNISH_CONFIGURE_ENABLE=      varnish
 VARNISH_CONFIGURE_WITH=                libvarnish=${LOCALBASE}
```

and this to pkg-plist:
--- pkg-plist.orig      2016-04-04 07:04:41.492617000 -0400
+++ pkg-plist   2016-04-04 07:04:26.272999000 -0400
@@ -72,6 +72,7 @@
 %%SIGROK%%lib/collectd/sigrok.so
 %%SNMP%%lib/collectd/snmp.so
 %%STATSD%%lib/collectd/statsd.so
+%%TSDB%%lib/collectd/write_tsdb.so
 lib/collectd/swap.so
 lib/collectd/syslog.so
 lib/collectd/table.so
```

That't all, folks
