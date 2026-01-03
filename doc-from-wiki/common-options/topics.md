---
title: Topics Section
parent: Common Options
nav_order: 1
---

## The `[[topics]]` section

This has the the MQTT topics that are to be subscribed to along with options used to control processing of the messages.
Most of the options control if the message should be ignored due to its timestamp.
See the [Date Time Processing](Date-Time-processing.md) page for a detailed explanation of these.

### ignore

Set to `true` if the field should be ignored. The default is `false`.

### unit_system

used to set the unit system. The default is `US`.
