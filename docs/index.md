---
title: readme
nav_exclude: true
layout: no_footer
---

<!-- 
This 'wraps' a `readme.md` so that the readme can be displayed in the repository and github pages.
It turns off the processing that would include the common footer by using a 'layout' that does not have a footer.
The footer is 'included' directly in the `readme.md` because the readme needs to be only markdown (or html).
-->

{% include_relative readme.md %}
