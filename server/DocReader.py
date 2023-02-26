from gpt_index import SimpleDirectoryReader, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain import OpenAI
from collections import defaultdict

class DocReader(object):
    def __init__(self, directory_path, index_path):
        self.index_path = index_path
        self.directory_path = directory_path
        self.max_input_size = 8192
        self.num_outputs = 256
        self.max_chunk_overlap = 20
        self.chunk_size_limit = 600
        self.llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.75, model_name="text-davinci-003", max_tokens=self.num_outputs))
        self.prompt_helper = PromptHelper(self.max_input_size, self.num_outputs, self.max_chunk_overlap, chunk_size_limit=self.chunk_size_limit)

    def construct_index(self):
        """
        Reconstruct the index, and save it to the database
        """
        documents = SimpleDirectoryReader(self.directory_path).load_data()        
        index = GPTSimpleVectorIndex(
            documents, llm_predictor=self.llm_predictor, prompt_helper=self.prompt_helper
        )
        index.save_to_disk(self.index_path + '/index.json')

    def predict(self, query):
        index = GPTSimpleVectorIndex.load_from_disk(self.index_path + '/index.json')
        response = index.query(query, response_mode="default")
        return response.response