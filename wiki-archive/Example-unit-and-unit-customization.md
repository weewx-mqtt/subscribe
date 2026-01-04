# Customizing units and unit groups

Experimental, maybe removed

Assumes understanding of this part of customizing WeewX
[https://weewx.com/docs/5.0/custom/units/#creating-a-new-unit-group](https://weewx.com/docs/5.0/custom/units/#creating-a-new-unit-group)

```

[MQTTSubscribeDriver or MQTTSubscribeService]
    [[weewx]]
        [[[observations]]]
            # Specify group. (Step 1)
            force = group_force

        [[[units]]]
            # Specify what unit is used to measure force in the three standard unit systems used by weewx. (Step 2)
            [[[[pound]]]]
                unit_system = us
                group = group_force

                # Specify format to use. (Step 3)
                format = '%.1f'
                # Specify label to use. (Step 3)
                label = pound
                # Specify how to convert. (Step 4)
                [[[[[conversion]]]]]
                    newton = lambda x : x * 4.44822
            
            # Specify what unit is used to measure force in the three standard unit systems used by weewx. (Step 2)
            [[[[newton]]]]
                unit_system = metric, metricwx
                group = group_force

                # Specify format to use. (Step 3)
                format = %.1f
                # Specify label to use. (Step 3)
                label = newton
                [[[[[conversion]]]]]
                    # Specify how to convert. (Step 4)
                    pound = lambda x : x * 0. 224809
```
