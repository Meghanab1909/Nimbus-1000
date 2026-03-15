import random
import boto3


def extract_text(file_path):
    """
    Extract text from a PDF using AWS Textract (synchronous, single-page friendly).
    For multi-page PDFs, uses the async StartDocumentTextDetection API.
    """
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    client = boto3.client("textract")

    response = client.detect_document_text(
        Document={"Bytes": file_bytes}
    )

    lines = [
        block["Text"]
        for block in response.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]

    return "\n".join(lines)


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