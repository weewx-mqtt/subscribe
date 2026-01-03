---
title: Field Name Section
parent: Topic Name Section
nav_order: 1
---

### The `[[[[field-name]]]]` sections

Under each `[[[topic-name]]]` any fields that need configuring are designated via a `[[[[field-name]]]]` section.
This information maybe in a `sensor-map`, `label-map`, etc. in other drivers or services.

Some common configuration options for a field are:

#### contains_total

Set to `true` if the incoming data is cumulative value (for example, rain total) and the WeeWX field expects an increment value.. The default is `false`.

#### conversion_type

The conversion type (bool, float, or int) necessary for WeeWX compatibility.  The default is `float`.

#### ignore

Set to `true` if the field should be ignored. The default is `false`.

#### name

The WeeWX name.

#### total_wrap_around

To be used in conjunction with `contains_total`.

Set to `true` if the incoming cumulative value can wrap around (yearly rain for example). The default is `false`.

