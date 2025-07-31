# Why?

Because [this](https://lukeplant.me.uk/blog/posts/avoid-django-genericforeignkey/), that's why


# Changes to subclass:

```python
# model_utils/models.py
# Line 79
if not subclass:
    selected_subclasses = [x['target_model_name'] for x in self.values('target_model_name').distinct('target_model_name').order_by('target_model_name')]
```
