---
title: Options Removed
parent: Deprecated Documentation
nav_order: 2
---

Here are the options removed and the replacements.
| Option prior to 2.0.0 | Option in 2.0.0 |
| --------------------- | --------------- |
|`[MQTTSubscribeDriver]` or `[MQTTSubscribeService]`<br>&nbsp;&nbsp;`topic = topic-name`|`[[topics]]`<br>&nbsp;&nbsp;`[[[topic-name]]]`<br>For additional information [see](https://github.com/weewx-mqtt/subscribe/wiki/Configuring#the-topic-name-sections).|
|||
|`[MQTTSubscribeDriver]` or `[MQTTSubscribeService]`<br>&nbsp;&nbsp;`overlap = `|`[[topics]]`<br>&nbsp;&nbsp;`adjust_start_time = ` and/or `adjust_end_time = `<br>For additional information [see](https://github.com/weewx-mqtt/subscribe/wiki/Date-Time-processing).|
|||
|`[[archive_field_cache]]`<br>&nbsp;&nbsp;`[[[fields]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`expires_after = `|`[[topics]]`<br>&nbsp;&nbsp;`[[[topic-name]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`expires_after = `<br>For additional information [see](https://github.com/weewx-mqtt/subscribe/wiki/Configuring---additional-options#expires_after).|
|||
|`[[message_callback]]`<br>&nbsp;&nbsp;`full_topic_fieldname = True`|`[[topics]]`<br>&nbsp;&nbsp;`[[[topic-name]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`<br>With the field definition under the topic, name clashes across topics cannoy happen and therefore this option is no longer needed.|
|||
|`[[message_callback]]`<br>&nbsp;&nbsp;`contains_total = field-name`|`[[topics]]`<br>&nbsp;&nbsp;`[[[topic-name]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`contains_total = True`<br>For additional information [see](https://github.com/weewx-mqtt/subscribe/wiki/Configuring#contains_total).|
|||
|`[[message_callback]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[label_map]]]`<br>&nbsp;&nbsp;&nbsp;`field-name = WeeWX-name`|`[[topics]]`<br>&nbsp;&nbsp;`[[[topic-name]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`name = WeeWX-name`<br>For additional information [see](https://github.com/weewx-mqtt/subscribe/wiki/Configuring#name).|
|||
|`[[message_callback]]`<br>&nbsp;&nbsp;`[[[fields]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`|`[[topics]]`<br>&nbsp;&nbsp;`[[[topic-name]]]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`[[[[field-name]]]]`<br>For additional information [see](https://github.com/weewx-mqtt/subscribe/wiki/Configuring#the-field-name-sections). |
|||
|`[[topics]]`<br>&nbsp;&nbsp;`use_topic_as_fieldname = True`|In 2.0.0 this option is no longer needed. MQTTSubscribe will use the topic as the fieldname if there are no `[[[[field-name]]]]` sections and at least one field configuration option is found.|
|||
