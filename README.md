# sns-core

Shared models and infrastructure helpers for SNS-related projects.

## Requirements

- Python 3.10+

## Install

```bash
pip install -e .
```

For type checking during development:

```bash
pip install -e .[dev]
```

## Recommended Imports

```python
from sns_core import (
    FirestoreSubscriptionStore,
    PostAuthor,
    SocialPlatform,
    SocialPost,
    decode_base64_json,
    get_domain_from_url,
)
```

## Typing

This package ships with a `py.typed` marker so downstream projects can consume its type hints.
