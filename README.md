# Why?

Because [this](https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/), that's why


# Thinkgs That Work

- [X] ChangeLog.objects.all() -> returns instances of the xChangeLog objects
- [X] ChangeLog.objects.filter() -> filters the pre-query as well
- [X] ChangeLog.objects.filter(normal_interfacechangelog__fktarget__name="Gi1/0/1")
- [ ] ChangeLog.objects.values("fktarget")