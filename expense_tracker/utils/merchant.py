import re
from expense_tracker.core.repository import MerchantCategoryRepository

def normalize_merchant(description: str) -> str:
    """Normalizing the description so that it can be matched against the merchant repository. This includes:
    - Converting to uppercase
    - Removing digits
    - Removing special characters like # and *
    - Removing common trailing city/state abbreviations
    - Removing common words like "PENDING", "MOBILE", "PURCHASE"

    Args:
        description (str): The raw description from the transaction.

    Returns:
        str: The normalized description.
    """
    description = description.upper()
    
    # Remove digits
    description = re.sub(r'\d+', '', description)

    # Remove just # and *
    description = re.sub(r'[#*]', '', description)

    # Remove PENDI or PENDING
    description = re.sub(r'\bPENDING\b', '', description).strip()
    description = re.sub(r'\bPENDI\b', '', description).strip()

    # Remove MOBILE
    description = re.sub(r'\bMOBILE\b', '', description).strip()

    # Remove PURCHASE
    description = re.sub(r'\bPURCHASE\b', '', description).strip()

    # Remove common trailing for cities
    description = re.sub(r"\b[A-Z]{2}\b$", "", description).strip()

    # Remove extra spaces
    description = re.sub(r'\s+', ' ', description).strip()

    return description

def categorize_merchant(description: str, amount: float, merchant_repo: MerchantCategoryRepository) -> str:
    """Categorizes the merchant based on the description and amount.

    Args:
        description (str): The raw description from the transaction.
        amount (float): The transaction amount.
        merchant_repo (MerchantCategoryRepository): The repository to look up merchant categories.

    Returns:
        str: The category of the merchant.
    """
    merchant = normalize_merchant(description)

    # If the amount is positive, it's likely an income, so we can categorize it as "Income"
    if amount > 0:
        return "Income"

    # First try exact match
    merchant_category = merchant_repo.get_category(merchant)
    if merchant_category:
        return merchant_category.category
    
    # If no exact match, try fuzzy matching
    fuzzy_match = fuzzy_lookup_merchant(merchant, merchant_repo=merchant_repo)
    if fuzzy_match:
        merchant_category = merchant_repo.get_category(fuzzy_match)
        if merchant_category:
            return merchant_category.category

    return "Uncategorized"

def fuzzy_lookup_merchant(merchant: str, threshold: int = 90, merchant_repo: MerchantCategoryRepository = None) -> str | None:
    """Attempts to find the closest matching merchant name using fuzzy string matching.

    Args:
        merchant (str): The normalized merchant name to look up.
        threshold (int, optional): The minimum score for a match to be considered valid. Defaults to 90.
        merchant_repo (MerchantCategoryRepository, optional): The repository to look up merchant names. Defaults to None.

    Returns:
        str | None: The best matching merchant name if found, otherwise None.
    """
    from rapidfuzz import process
    if merchant_repo is None:
        return None
    
    merchants = merchant_repo.get_all_merchants()
    if not merchants:
        return None
    
    merchant_keys = [m.merchant_key for m in merchants]
    
    match = process.extractOne(merchant, merchant_keys, score_cutoff=threshold)
    if match:
        return match[0]
    return None