import sys
import flask


def is_dev_machine() -> bool:
    return flask.current_app.config["ENV"] in ["test", "development"]


def confirm_if_not_dev(operation: str, exit_immediately=True):
    if not is_dev_machine():
        received = input(
            "Looks like you are *NOT* on development machine! Please type  "
            f"'{operation}' UPPERCASE to confirm you really want to do this: "
        )

        if received != operation.upper():
            msg = (
                f"Operation was not confirmed! You typed: '{received}'! No changes "
                "were executed."
            )

            if exit_immediately:
                sys.exit(msg)
            else:
                print(msg)
                return False

        return True

    return True
