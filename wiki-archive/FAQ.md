<!-- markdownlint-disable first-line-heading no-inline-html  -->

<!-- MQTTSubscribe runtime  -->
<details>
<summary><b>Why do I have to initialize MQTTSubscribe’s runtime?</b></summary>

WeeWX has [3 installation](http://www.weewx.com/docs/5.0/#installation) methods, ‘package’, pip, and ‘git’.
Each of these methods puts WeeWX files in different [locations](http://www.weewx.com/docs/5.0/usersguide/where/).
WeeWX does not provide a mechanism to programmatically determine the location of files,
so it falls to the end user to provide this information.
Instead of writing 3 versions of instructions, 1 for each installation method, environment variables are set with location of the files.
This makes writing and supporting the documentation easier.
Hopefully it also makes reading the documentation easier.

</details>

<!-- WeeWX 4.x support  -->
<details>
<summary><b>Why does support for WeeWX 4.x start at WeeWX 4.6.1 and not 4.6.0 (or even 4.0.0)?</b></summary>

At 4.6.1 WeeWX fixed [737](https://github.com/weewx/weewx/issues/737).
In prior versions if there was no data a 0 was returned.
Now None is returned.

This resulted MQTTSubscribe having different test results for WeeWX 4.6.1 and later.
To keep things simple, the MQTTSubscribe tests were updated to work against 4.6.1 and later.
Since MQTTSubscribe is not tested against earlier versions, these are not supported.
But, if one is OK with the results WeeWX versions earlier than 4.6.1 returns, MQTTSubscribe *should* work.

</details>

<!-- WeeWX 5.x support  -->
<details>
<summary><b>Why does support for WeeWX 5.x start at WeeWX 5.0.1 and not 5.0.0?</b></summary>

At 5.0.1 WeeWX was updated to run as the `weewx` user and not as `root`.
All of MQTTSubscribe’s documentation has been updated to reflect this change.
See,
[https://groups.google.com/g/weewx-user/c/GR8Tmi8ud9g/m/ev6q2qOEAwAJ](https://groups.google.com/g/weewx-user/c/GR8Tmi8ud9g/m/ev6q2qOEAwAJ)
for additional information.

**Note**, it is not a good idea to be running WeeWX 5.0.0.
See, [https://groups.google.com/g/weewx-user/c/fa2y3wTr-AE](https://groups.google.com/g/weewx-user/c/fa2y3wTr-AE) for additional information.

</details>
