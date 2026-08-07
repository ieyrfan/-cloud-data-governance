import re

# Regex Patterns
# Malaysian IC format: YYMMDD-PP-NNNN (e.g. 900101-14-5555)
# Year: 00-99, Month: 01-12, Day: 01-31, Place: 01-99, Unique: 0000-9999
MY_IC_PATTERN = re.compile(r'\b\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])-\d{2}-\d{4}\b')

# Malaysian Mobile Phone format: 01X-XXXXXXX or 01X-XXXXXXXX
MY_PHONE_PATTERN = re.compile(r'\b01\d-\d{7,8}\b')

# Standard Email
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

# Credit Card (Visa, MasterCard, Amex, Discover)
CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,16}\b')


def is_luhn_valid(cc_number: str) -> bool:
    """
    Validates a credit card number using the Luhn algorithm.
    """
    # Remove all non-digit characters
    digits = [int(c) for c in cc_number if c.isdigit()]
    if not digits:
        return False
        
    # Reverse the digits
    digits.reverse()
    
    # Double every second digit
    for i in range(1, len(digits), 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
            
    # Check if sum is divisible by 10
    return sum(digits) % 10 == 0


def find_sensitive_patterns(text: str) -> dict:
    """
    Scans text for sensitive patterns and returns the matches.
    """
    results = {
        'my_ic': MY_IC_PATTERN.findall(text),
        'my_phone': MY_PHONE_PATTERN.findall(text),
        'email': EMAIL_PATTERN.findall(text),
        'credit_card': []
    }
    
    # Process credit cards with Luhn validation
    potential_ccs = CREDIT_CARD_PATTERN.findall(text)
    for cc in potential_ccs:
        # Clean string to pass to validator
        clean_cc = re.sub(r'[\s-]', '', cc)
        if len(clean_cc) >= 13 and len(clean_cc) <= 16 and is_luhn_valid(clean_cc):
            results['credit_card'].append(clean_cc)
            
    return results

def redact_sensitive_data(text: str, results: dict) -> str:
    """
    Redacts the identified sensitive data from the original text.
    Replaces matches with [REDACTED - TYPE].
    """
    redacted_text = text
    for data_type, matches in results.items():
        for match in matches:
            if data_type == 'my_ic':
                # Preserve last 4 digits for verification if needed, or mask entirely
                mask = "[REDACTED - NRIC]"
            elif data_type == 'credit_card':
                mask = "[REDACTED - CC]"
            elif data_type == 'email':
                mask = "[REDACTED - EMAIL]"
            elif data_type == 'my_phone':
                mask = "[REDACTED - PHONE]"
            else:
                mask = "[REDACTED]"
            
            redacted_text = redacted_text.replace(match, mask)
            
    return redacted_text

