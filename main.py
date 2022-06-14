# Dummy container, used to preload empty lambda functions
def handler(event, context):
    return {"hello": "world"}
