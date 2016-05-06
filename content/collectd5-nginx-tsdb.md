Title: Use NGINX+LUA to proxy collectd5 requests to OpenTSDB
Date: 2016-05-06 00:10
Category: How-Tos
Tags: Collectd, FreeBSD, Ports, Net-Mgmt, Patch, Collectd, OpenTSDB, NginX, LUA
Status: published
Summary: Use NGINX+LUA to proxy Collectd5 requests to OpenTSDB

If you, like me, are using **net-mgmt/collectd5** and **databases/opentsdb** to collect
your metrics, you probably are using **write_tsdb** to push your metrics to OpenTSDB.

Sometimes you, like me, find frustrating how collectd set its metrics' names and you would
like to move part of the metric's name (i.e. network interface name) to a tag
(so that you can aggregate using it).

Keeping this as simple as possible we can let NginX (using its Lua engine) to do this job for us, let's see how.

First of all, we need to enable WITH_CURL in **net-mgmt/collectd5** because of write_http
and we have to enable write_http output plugin in **/usr/local/etc/collectd.conf**:
```apache
LoadPlugin write_http

<Plugin "write_http">
    <Node "tsdb">
        URL "http://127.0.0.1:9090/tsdb"
        Format "JSON"
    </Node>
</Plugin>
```

As you can see we are instructing collectd to publish metrics via HTTP using a JSON format to
127.0.0.1:9090/tsdb, where there is a nginx listening with this config file:
```nginx
server {
  listen                *:9090;
  access_log /var/log/nginx/tsdb_access.log main;
  error_log  /var/log/nginx/tsdb_error.log;

  location /tsdb {
    rewrite_by_lua_file /usr/local/etc/nginx/sites/tsdb_proxy.lua;
  }

  location / {
    return 405;
  }
}
```

where */usr/local/etc/nginx/sites/tsdb_proxy.lua* is translating our metrics:
```
local cjson = require( "cjson" )

if ngx.req.get_method() == "POST" then
    ngx.req.read_body()
    local params = ngx.req.get_post_args()

    -- Define a prefix
    local metric_prefix = "my.own.metric"

    -- Connect to OpenTSDB
    local sock = ngx.socket.connect("127.0.0.1", 4242)

    local tsdb_payload = ""
    for k,v in pairs(params) do
        local k_tbl = cjson.decode(k)
        local count_tbl = 1
        for _ in pairs(k_tbl) do
            local metric_host = k_tbl[count_tbl]['host']
            local metric_name_tmp = k_tbl[count_tbl]['plugin']
            local metric_tstamp = math.floor(k_tbl[count_tbl]['time'])
            local metric_name = ""
            local metric_value = 0
            local metric_tags = "host=" .. metric_host

            if metric_name_tmp == "cpu" or metric_name_tmp == "memory" then
                metric_name = metric_name_tmp .. "." .. k_tbl[count_tbl]['type_instance'] .. "." .. k_tbl[count_tbl]['type']
                metric_value = k_tbl[count_tbl]['values'][1]
                tsdb_payload = tsdb_payload .. "put " .. metric_prefix .. "." .. metric_name .. " " .. metric_tstamp .. " " .. metric_value .. " " .. metric_tags .. "\r\n"
            elseif metric_name_tmp == "interface" then
                local interface_name = k_tbl[count_tbl]['plugin_instance']
                metric_tags = metric_tags .. " interface=" .. interface_name
                for i, v in ipairs(k_tbl[count_tbl]['dsnames']) do
                    metric_name = metric_name_tmp .. "." .. k_tbl[count_tbl]['type'] .. "." .. v
                    metric_value = k_tbl[count_tbl]['values'][i]
                    tsdb_payload = tsdb_payload .. "put " .. metric_prefix .. "." .. metric_name .. " " .. metric_tstamp .. " " .. metric_value .. " " .. metric_tags .. "\r\n"
                end
            elseif metric_name_tmp == "load" then
                for i, v in ipairs(k_tbl[count_tbl]['dsnames']) do
                    metric_name = metric_name_tmp .. "." .. k_tbl[count_tbl]['type_instance'] .. "." .. v
                    metric_value = k_tbl[count_tbl]['values'][i]
                    tsdb_payload = tsdb_payload .. "put " .. metric_prefix .. "." .. metric_name .. " " .. metric_tstamp .. " " .. metric_value .. " " .. metric_tags .. "\r\n"
                end
            elseif metric_name_tmp == "statsd" then
                --[[ 

                      Here we will include logic for metrics from statsd

                --]]
            else
                ngx.log(ngx.STDERR, "[WARNING]: Unknown metric_name " .. metric_name)
            end
            count_tbl = count_tbl + 1
        end
    end

    if tsdb_payload ~= "" then
        sock:send(tsdb_payload)
        sock:setkeepalive()
    end
end

-- All safe, let's get out of here
ngx.exit(200)
```

This will translate this JSON:
```
[{"values":[6584721,4633500],"dstypes":["derive","derive"],"dsnames":["rx","tx"],"time":1460360931.658,"interval":10.000,"host":"my.own.host","plugin":"interface","plugin_instance":"vtnet0","type":"if_packets","type_instance":""},[...],{"values":[0,0],"dstypes":["derive","derive"],"dsnames":["rx","tx"],"time":1460360931.658,"interval":10.000,"host":"my.own.host","plugin":"interface","plugin_instance":"vtnet0","type":"if_errors","type_instance":""}]
```

into this:
```
put my.own.metric.interface.if_packets.rx 1460360931 6584721 host=my.own.host interface=vtnet0
put my.own.metric.interface.if_packets.tx 1460360931 4633500 host=my.own.host interface=vtnet0
put my.own.metric.interface.if_errors.rx 1460360931 0 host=my.own.host interface=vtnet0
put my.own.metric.interface.if_errors.tx 1460360931 0 host=my.own.host interface=vtnet0
```

That's better than:
```
put my.own.metric.interface.vtnet0.if_packets.rx 1460360931 6584721 host=my.own.host
put my.own.metric.interface.vtnet0.if_packets.tx 1460360931 4633500 host=my.own.host
put my.own.metric.interface.vtnet0.if_errors.rx 1460360931 0 host=my.own.host
put my.own.metric.interface.vtnet0.if_errors.tx 1460360931 0 host=my.own.host
```

As you may notice, we used the cjson library in tsdb_proxy.lua, so we need to install **devel/lua-cjson**, too.
