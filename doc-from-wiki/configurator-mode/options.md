---
title: Options
parent: Configurator Mode
nav_order: 3
---

## Options

### --add-from ADD_FROM

The configuration that will and add to (but not update existing settings) the configuration specified with --conf.

For example, the configuration specified with --conf is:

```
[[topic]]
    [[[field-1]]]
        name = rename-1a
    [[[field-2]]]
```

And the configuration in ADD_FRON is

```
[[topic]]
    [[[field-1]]]
        name = rename-1b
    [[[field-3]]]
```

The resulting configuration will be

```
[[topic]]
    [[[field-1]]]
        name = rename-1a
    [[[field-2]]]
    [[[field-3]]]
```

### --conf CONF

The WeeWX configuration file. Typically weewx.conf.

### --export EXPORT_CONF

Export the configuration in EXPORT_CONF.

### --no-backup

When updating the configuration specified with --conf, do not back it up.

### --output OUTPUT

Instead of updating the WeeWX configuration the configuration specified with --conf write it to OUTPUT.

### --print-configspec PRINT_CONFIGSPEC

Write the configspec to a file.

### --replace-with REPLACE_WITH

The configuration that will replace the configuration specified with --conf.

For example, if the configuration specified with --conf is:

```
[[topic]]
    [[[field-1]]]
        name = rename-1a
    [[[field-2]]]
```

And the configuration in REPLACE_WITH is

```
[[topic]]
    [[[field-1]]]
        name = rename-1b
    [[[field-3]]]
```

The resulting configuration will be

```
[[topic]]
    [[[field-1]]]
        name = rename-1b
    [[[field-3]]]
```

### --remove

Remove the configuration from the configuration specified with --conf.

### --update-from UPDATE_FROM

The configuration that will update and add to the configuration specified with --conf.

For example, if the configuration specified with --conf is:

```
[[topic]]
    [[[field-1]]]
        name = rename-1a
    [[[field-2]]]
```

And the configuration in UPDATE_FROM is

```
[[topic]]
    [[[field-1]]]
        name = rename-1b
    [[[field-3]]]
```

The resulting configuration will be

```
[[topic]]
    [[[field-1]]]
        name = rename-1b
    [[[field-2]]]
    [[[field-3]]]
```

### --top-level

Use the complete input configuration as the MQTTSubscribeDriver/MQTTSubscribeService configuration section.

### --validate

Validate the configuration specified with --conf.
