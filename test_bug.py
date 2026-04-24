from typing import Any

def check_tags(node):
    tags_value: Any = node.get("tags", [])
    if isinstance(tags_value, list):
        has_tier1_tag: bool = any(
            isinstance(tag, dict)
            and (
                "tier1" in str(tag.get("tagFQN", "")).lower()
                or "tier1" in str(tag.get("name", "")).lower()
            )
            for tag in tags_value
        )
        return has_tier1_tag
    return False

# User's exact example
print(check_tags({"tags": [{"tagFQN": "Tier1", "source": "Classification"}]}))
