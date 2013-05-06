import threading


def wait_for_condition(condition, obj, trait, timeout=None):
    """
    Wait until the given condition is true, re-evaluating on trait change.

    Wait until `condition` is satisfied.  Raise a RuntimeError if
    `condition` is not satisfied within the given timeout.

    `condition` is a callback function that will be called with `obj`
    as its single argument.  It should return a boolean indicating
    whether the condition is satisfied or not.

    `timeout` gives the maximum time in seconds to wait for the
    condition to become true.  The default value of `None` indicates
    no timeout.

    (obj, trait) give an object and trait to listen to for indication
    of a possible change: whenever the trait changes, the condition is
    re-evaluated.  The condition will also be evaluated on entering
    this function.

    """
    condition_satisfied = threading.Event()

    def handler():
        if condition(obj):
            condition_satisfied.set()

    obj.on_trait_change(handler, trait)
    try:
        if condition(obj):
            # Catch case where the condition was satisfied before
            # the on_trait_change handler was active.
            pass
        elif timeout is None:
            # Allow a Ctrl-C to interrupt.  The 0.05 value matches
            # what's used by the standard library's Condition.wait.
            while not condition_satisfied.wait(timeout=0.05):
                pass
        elif not condition_satisfied.wait(timeout=timeout):
            raise RuntimeError("Timed out waiting for condition.")
    finally:
        obj.on_trait_change(handler, trait, remove=True)
