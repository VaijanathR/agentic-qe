# Encodes deterministic validation of requirements, test cases, and results against approved baselines.
import re


SUPPORTED_COUNTRIES = {
    "india",
    "germany",
    "uk",
    "usa",
}


def validate_customer_name(customer_name):
    if customer_name is None:
        return False, "Customer name is missing"

    if not isinstance(customer_name, str):
        return False, "Customer name must be a string"

    if not customer_name.strip():
        return False, "Customer name is empty"

    return True, None


def validate_country(country):
    if country is None:
        return False, "Country is missing"

    if not isinstance(country, str):
        return False, "Country must be a string"

    normalized_country = country.strip().lower()

    if not normalized_country:
        return False, "Country is empty"

    if normalized_country not in SUPPORTED_COUNTRIES:
        return False, f"Unsupported country: {country}"

    return True, None


def validate_email(email):
    if email is None or email == "":
        return True, None

    if not isinstance(email, str):
        return False, "Email must be a string"

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_phone(phone):
    if phone is None or phone == "":
        return True, None

    if not isinstance(phone, str):
        return False, "Phone must be a string"

    phone_pattern = r"^\+?[0-9\-\s]{7,20}$"

    if not re.match(phone_pattern, phone):
        return False, "Invalid phone format"

    return True, None


def validate_customer(customer):
    errors = []

    checks = [
        validate_customer_name(customer.get("customerName")),
        validate_country(customer.get("country")),
        validate_email(customer.get("email")),
        validate_phone(customer.get("phone")),
    ]

    for valid, error in checks:
        if not valid:
            errors.append(error)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def is_duplicate_customer(candidate, existing_customers):
    candidate_name = candidate.get("customerName", "").strip().lower()
    candidate_country = candidate.get("country", "").strip().lower()

    for customer in existing_customers:
        existing_name = customer.get("customerName", "").strip().lower()
        existing_country = customer.get("country", "").strip().lower()

        if (
            candidate_name == existing_name
            and candidate_country == existing_country
        ):
            return True

    return False


if __name__ == "__main__":
    customer = {
        "customerName": "ABC Corp",
        "country": "India",
        "email": "contact@abccorp.example",
        "phone": "+91-9876500003",
    }

    print(validate_customer(customer))