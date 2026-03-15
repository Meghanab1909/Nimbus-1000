import random

def extract_text(file_path):
    """
    Mock text extraction (later replace with Textract)
    """
    text = """
    The borrower agrees to a floating interest rate which may increase after two years.
    A prepayment penalty of 5 percent will apply if the borrower closes the loan early.
    The borrower must pay a balloon payment at the end of the loan term.
    """
    return text


def split_clauses(text):
    clauses = [c.strip() for c in text.split(".") if c.strip()]
    return clauses


def retrieve_context(clause):
    knowledge = [
        "Typical personal loan interest rates range from 5 to 15 percent.",
        "Early repayment penalties are usually less than 2 percent.",
        "Balloon payments increase borrower financial risk."
    ]

    return random.choice(knowledge)


def analyze_clause(clause, context):

    risk_level = "Low"

    clause_lower = clause.lower()

    if "penalty" in clause_lower:
        risk_level = "High"

    elif "floating" in clause_lower:
        risk_level = "Medium"

    elif "balloon" in clause_lower:
        risk_level = "High"

    return {
        "clause": clause,
        "risk_level": risk_level,
        "reference": context
    }


def analyze_document(file_path):

    text = extract_text(file_path)

    clauses = split_clauses(text)

    results = []

    for clause in clauses:

        context = retrieve_context(clause)

        analysis = analyze_clause(clause, context)

        results.append(analysis)

    return {
        "risk_report": results
    }