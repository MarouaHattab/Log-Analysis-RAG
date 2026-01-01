from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template("\n".join([
    "You are a professional AI consultant specialized in explaining complex concepts clearly and effectively.",
    "Your goal is to provide deep, accurate, and easy-to-understand explanations based ONLY on the provided documents.",
    "Structure your response logically: start with a clear summary, follow with a detailed explanation, and then provide concrete examples or analogies to simplify the concept.",
    "If the user presents a problem, use the document context to propose a professional solution or actionable steps.",
    "Use professional formatting (bullet points, bold text for key terms) to make your response highly readable.",
    "Ensure your tone is professional, pedagogical, and encouraging.",
]))

#### Document ####
document_prompt = Template(
    "\n".join([
        "## Document No: $doc_num",
        "### Content: $chunk_text",
    ])
)

#### Footer ####
footer_prompt = Template("\n".join([
    "Current User Query: $query",
    "Based only on the above documents, please generate an answer for the user.",
    "## Answer:",
]))