tags_value = [{"tagFQN": "Tier1", "source": "Classification"}]
has_tier1_tag = any(
    isinstance(tag, dict)
    and (
        "tier1" in str(tag.get("tagFQN", "")).lower()
        or "tier1" in str(tag.get("name", "")).lower()
    )
    for tag in tags_value
)
print("Result:", has_tier1_tag)
