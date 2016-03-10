Title: Upgrading www/nginx-devel to 1.9.12
Date: 2016-03-10 16:10
Category: How-Tos
Tags: Nginx, FreeBSD, Portmaster, Ports, Devel
Authors: Davide D'Amico
Summary: Changes I applied to nginx.conf while upgrading nginx-devel to 1.9.12

On a VM where I have few personal websites I use **www/nginx-devel** to act as a:
- webserver (with **php-fpm**)
- reverse proxy (for stuff like **grafana** and **opentsdb**)

Why? Because sometimes I like living on the edge (yey).

This morning after a:
```
sudo portsnap fetch && portsnap update
```
**nginx-devel-1.9.12** popped out from
```
sudo pkg_version -vL\=
```

Cool, let's give it a try with:
```
sudo portmaster www/nginx-devel
```

But hey, what's this *-nopcre* tag?
```
dave@srv1:~> pkg info | grep ^nginx
nginx-devel-nopcre-1.9.12      Robust and small WWW server
```

Well, we will take a look at it later on.

In case of nginx, after an upgrade I usually run a:
```
sudo service nginx configtest
```
and immediately after:
```
sudo service nginx upgrade
```
to check its configuration before upgrading it.

This time the configtest reported:
```
dave@srv1:~> sudo service nginx configtest                                                              
Performing sanity check on nginx configuration:                                                         
nginx: [emerg] unknown directive "more_set_headers" in /usr/local/etc/nginx/nginx.conf:26               
nginx: configuration file /usr/local/etc/nginx/nginx.conf test failed
```

Uhm... weird... let's investigate:
```
dave@srv1:/usr/ports/www/nginx-devel> sudo make showconfig | grep HEADERS                               
     HEADERS_MORE=on: 3rd party headers_more module
```
So the 3rd party module has been included and should have been compiled.

Time to ask this question to */usr/ports/UPDATING*:
```
[...]
20160217:                                                                                               
  AFFECTS: users of www/nginx-devel
  AUTHOR: osa@FreeBSD.org
  Dynamic modules support has been enabled for the following third-party
  modules, in case of usage of these modules please update nginx
  configuration file for load these modules:                                                            

  load_module "modules/ngx_dynamic_upstream_module.so";
  load_module "modules/ngx_http_small_light_module.so";
[...]
```

Oh, so let's fix */usr/local/etc/nginx/nginx.conf*:
```
dave@srv1:/usr/local/etc/nginx> sudo diff -uh nginx.conf nginx.conf.new                                 
--- nginx.conf  2016-03-10 11:25:00.034727000 +0100                                                     
+++ nginx.conf.new      2016-03-10 11:24:53.920473000 +0100                                             
@@ -1,3 +1,5 @@                                                                                         
+load_module /usr/local/etc/nginx/modules/ngx_http_headers_more_filter_module.so;
+
 worker_processes  1;
 events {

```
We should be good, then (yeah, why are modules installed under */usr/local/etc/nginx/modules*?).

```
dave@srv1:~> sudo service nginx configtest
Performing sanity check on nginx configuration:
nginx: [emerg] without PCRE library "gzip_disable" supports builtin "msie6" and "degradation" mask only
in /usr/local/etc/nginx/nginx.conf:46
nginx: configuration file /usr/local/etc/nginx/nginx.conf test failed
```
What's that, now?
```
dave@srv1:~> sed -n '46,46p' /usr/local/etc/nginx/nginx.conf
    gzip_disable "MSIE [1-6]\.";
```
Ok, this shouldn't be an issue but I want the old behaviour, so what module should I enable?
```
dave@srv1:/usr/ports/www/nginx-devel> grep -B 2 '\-\-with-pcre' Makefile
.if ${PORT_OPTIONS:MHTTP_REWRITE} || defined(USE_HTTP_REWRITE)
LIB_DEPENDS+=   libpcre.so:${PORTSDIR}/devel/pcre
CONFIGURE_ARGS+=--with-pcre
```
So after recompiling nginx-devel with HTTP_REWRITE everything went fine:
```
dave@srv1:~> sudo service nginx configtest
Performing sanity check on nginx configuration:
nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
dave@srv1:~> sudo service nginx upgrade
Performing sanity check on nginx configuration:
nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
Upgrading nginx binary:
Stopping old binary:
dave@srv1:~> 
```
