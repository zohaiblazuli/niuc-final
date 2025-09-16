"""Example usage of the Guardrail class."""

from pccniuc.guard import Guardrail, GuardResult


def positive_only(values):
    if any(v <= 0 for v in values):
        return GuardResult(False, "Found non-positive value")
    return GuardResult(True, "All values positive")


def main():
    guard = Guardrail(positive_only)
    dataset = [1, 2, 3]
    result = guard.evaluate(dataset)
    print(result.message)


if __name__ == "__main__":
    main()
