def unimplemented_error():
    raise Exception("Unimplemented")

def parse_error(category: str, msg : str = ""):
    raise Exception(f"Parse error in {category}, Error Msg: {msg}")