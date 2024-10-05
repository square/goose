{{summary}}

# Instructions

Prepare a plan that an agent will use to followup to the request described above. Your plan
will be carried out by an agent with access to the following tools:

{% for tool in tools %}
{{tool.name}}: {{tool.description}}{% endfor %}

If the request is simple, such as a greeting or a request for information or advice, the plan can simply be:
"reply to the user".

However for anything more complex, reflect on the available tools and describe a step by step
solution that the agent can follow using their tools.

Your plan needs to use the following format, but can have any number of tasks.

```json
[
    {"description": "the first task here"},
    {"description": "the second task here"},
]
```

# Examples

These examples show the format you should follow

```json
[
    {"description": "reply to the user"},
]
```

```json
[
    {"description": "create a directory 'demo'"},
    {"description": "write a file at 'demo/fibonacci.py' with a function fibonacci implementation"},
    {"description": "run python demo/fibonacci.py"},
]
```
