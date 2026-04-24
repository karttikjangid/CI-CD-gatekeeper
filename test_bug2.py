def test_tags(node):
    tags_value = node.get("tags", [])
    has_tier1_tag = False
    
    if isinstance(tags_value, str):
        import json
        try:
            tags_value = json.loads(tags_value)
        except Exception:
            pass

    if isinstance(tags_value, list):
        for tag in tags_value:
            if isinstance(tag, dict):
                tag_fqn = str(tag.get("tagFQN", "")).lower()
                tag_name = str(tag.get("name", "")).lower()
                if "tier1" in tag_fqn or "tier1" in tag_name:
                    has_tier1_tag = True
                    break
            elif isinstance(tag, str):
                if "tier1" in tag.lower():
                    has_tier1_tag = True
                    break
    elif isinstance(tags_value, dict):
        tag_fqn = str(tags_value.get("tagFQN", "")).lower()
        tag_name = str(tags_value.get("name", "")).lower()
        if "tier1" in tag_fqn or "tier1" in tag_name:
            has_tier1_tag = True

    return has_tier1_tag

print("Dict in List:", test_tags({"tags": [{"tagFQN": "Tier1", "source": "Classification"}]}))
print("Stringified JSON:", test_tags({"tags": '[{"tagFQN": "Tier1", "source": "Classification"}]'}))
print("String in List:", test_tags({"tags": ["Tier1"]}))
print("Direct Dict:", test_tags({"tags": {"tagFQN": "Tier1"}}))
