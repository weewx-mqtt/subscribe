---
title: TLS Section
parent: Additional Options
nav_order: 1
---

## The `[[tls]]` section

The TLS options that are passed to tls_set method of the MQTT client. For additional information see, [https://eclipse.org/paho/clients/python/docs/strptime-format-codes](https://eclipse.org/paho/clients/python/docs/strptime-format-codes)

### ca_certs

Path to the Certificate Authority certificate files that are to be treated as trusted by this client.

### certfile

The PEM encoded client certificate and private keys. The default is `None`.

### certs_required

The certificate requirements that the client imposes on the broker. Valid values are, `none`, `optional`, `required`. The default is `required`

### ciphers

The encryption ciphers that are allowable for this connection. Specify `None` to use the defaults. The default is `None`.

### keyfile

The private keys. The default is `None`.

### tls_version

The version of the SSL/TLS protocol to be used. Valid values are,`sslv2`, `sslv23`, `sslv3`, `tls`, `tlsv1`, `tlsv11`, `tlsv12`. The default is `tlsv12`.
