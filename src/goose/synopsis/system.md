# System Status

```json
{{os}}
```


{% for file in files %}
{{file.path}}
```{{file.lang}}
{{file.content}}
```

{% endfor %}
