from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List, Tuple, Optional
import json
import logging


class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
        self.logger = logging.getLogger("uvicorn")

    def create_collection_name(self, project_id: str):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    
    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: manage items
        texts = [ c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in  chunks]
        vectors = self.embedding_client.embed_text(text=texts, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)

        # step3: create collection if not exists
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True

    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # step1: get collection name
        query_vector = None
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)

        if not vector or len(vector) == 0:
            return False
        if isinstance(vector, list) and len(vector)>0:
            query_vector = vector[0]
        if not query_vector:
            return False
        # step3: do semantic search
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        if not results:
            return False

        return results
    
    async def answer_rag_question(self, project: Project, query: str, limit: int = 10, 
                                   chat_history: List[dict] = None) -> Tuple[Optional[str], Optional[str], Optional[List[dict]]]:
        """
        Answer user question using RAG
        
        Returns:
            Tuple of (answer, full_prompt, chat_history)
        """
        answer, full_prompt = None, None
        search_query = query

        try:
            # step0: Refine search query if there is history
            if chat_history and len(chat_history) > 1:
                try:
                    refinement_history = [h.copy() for h in chat_history]
                    refinement_prompt = f"Given the following conversation history and the latest user message, rephrase the user message to be a standalone search query that can be used to retrieve relevant documents. Only return the search query and nothing else.\n\nLatest message: {query}"
                    
                    refined_query = self.generation_client.generate_text(
                        prompt=refinement_prompt,
                        chat_history=refinement_history,
                        max_output_tokens=100
                    )
                    if refined_query:
                        search_query = refined_query.strip().strip('"').strip("'")
                        self.logger.info(f"Refined search query: {search_query}")
                except Exception as e:
                    self.logger.error(f"Error refining query: {e}")

            # step1: retrieve related documents
            retrieved_documents = await self.search_vector_db_collection(
                project=project,
                text=search_query,
                limit=limit,
            )

            if not retrieved_documents or len(retrieved_documents) == 0:
                self.logger.error(f"No documents retrieved for query: {search_query}")
                return self._construct_no_data_response(query), None, chat_history
            
            self.logger.info(f"Retrieved {len(retrieved_documents)} documents")
            
            # step2: Construct LLM prompt
            system_prompt = self.template_parser.get("rag", "system_prompt")

            # Build document prompts with clear numbering
            actual_doc_count = len(retrieved_documents)
            documents_prompts = "\n".join([
                self.template_parser.get("rag", "document_prompt", {
                        "doc_num": idx + 1,
                        "chunk_text": self.generation_client.process_text(doc.text),
                })
                for idx, doc in enumerate(retrieved_documents)
            ])
            
            # Add document count context
            doc_count_info = f"[You have access to {actual_doc_count} document(s). Reference them as Document No: 1 through {actual_doc_count}.]"

            footer_prompt = self.template_parser.get("rag", "footer_prompt", {
                "query": query
            })

            # step3: Construct Generation Client Prompts
            if not chat_history:
                chat_history = [
                    self.generation_client.construct_prompt(
                        prompt=system_prompt,
                        role=self.generation_client.enums.SYSTEM.value,
                    )
                ]

            full_prompt = "\n\n".join([doc_count_info, documents_prompts, footer_prompt])

            # step4: Generate the Answer
            answer = self.generation_client.generate_text(
                prompt=full_prompt,
                chat_history=chat_history,
                max_output_tokens=4000
            )
            
            if not answer:
                self.logger.error("Generated empty answer")
                return self._construct_no_data_response(query), full_prompt, chat_history
            
            self.logger.info(f"Generated answer successfully")

            # Update chat history with the new turn
            chat_history.append(self.generation_client.construct_prompt(
                prompt=query,
                role=self.generation_client.enums.USER.value,
            ))
            chat_history.append(self.generation_client.construct_prompt(
                prompt=answer,
                role=self.generation_client.enums.ASSISTANT.value,
            ))

            return answer, full_prompt, chat_history
            
        except Exception as e:
            self.logger.error(f"Error in answer_rag_question: {str(e)}", exc_info=True)
            return None, full_prompt, chat_history

    def _construct_no_data_response(self, query: str) -> str:
        """Construct 'no data found' response"""
        return f"""I cannot find relevant information in the provided documents to answer your query.

**Query:** {query}

**Recommendation:** 
Please try:
- Rephrasing your question
- Using different keywords
- Ensuring the relevant log files have been uploaded and processed
- Uploading additional log files

I can only answer based on the log data that has been uploaded and indexed."""
