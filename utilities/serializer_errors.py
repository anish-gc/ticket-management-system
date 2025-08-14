def custom_serializer_errors(errors_msg):
    try:
        return [
            error_message
            for error_message_list in errors_msg.values()
            for error_message in error_message_list
        ]
    except Exception as exe:
        raise Exception(exe)


def custom_list_serializer_errors(errors_msg):
    error_list = []

    # Ensure it's iterable
    if isinstance(errors_msg, list):
        for error_dict in errors_msg:
            if isinstance(error_dict, dict):
                for key, error_messages in error_dict.items():
                    error_list.extend(error_messages)  # Extract error messages

    return error_list
