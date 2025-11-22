from string import Template

## Rag Prompts - English 
system_prompt = Template("\n".join([
    "You are an assistnat to generate a response for the user",
    "You will be provided by a set of documents assocaited with the user's query",
    "You have to generate a response based on the provided documents",
    "Ignore the documents that are not related to the user's query",
    "You can applogize to the user if you are not able to generate a response",
    "You have to generate reponse in the same language as the user's query",
    "Be polite and respectful to the user",
    "Be Precise and concise in your response,Avoid unnecessary information",

]))

## Document Prompt 
document_prompt=Template("\n".join([
"## Document No $doc_num",
"### Content: $chunk_text",
]))
## Footer 

footer_prompt = Template("\n".join([
    "Based only on the above documents,please generate an answer for the user",
    "## Answer: ",
]))