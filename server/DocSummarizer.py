import numpy as np
from PIL import Image
import os
import json
from DocLayout import DocLayout
from collections import defaultdict

# TODO: Move the handling resources file to a route in the app.py or a separate file
# TODO: This class will be become to a service that will be called by the app.py to summarize the document
class DocSummarizer(object):
    def __init__(self, documents_path: str, resources_path: str):
        self.documents_path = documents_path
        self.resources_path = resources_path
        self.prompt_tail = {
            'authors': 'Who are the authors of this paper',
            'summary':"\n\nSummarize the above text, focus on key insights",
            'keyresults':'''\n\nGive me three key results in the format of "Key results:
                1.  Key result 1
                2. Key result 2
                3. Key result 3"''',
            'keyword':'\n\nGive me keywords in the format of "Keywords:  Keyword 1, Keyword 2, Keyword 3"',
            'limitations':'\n\nGive me 3 sentences describing the limitations of the text above.'
        }
        self.layout_model = DocLayout()
        
    def get_summary(self, file_name: str, reader):
        """
        Returns a summary of the document, this document is a pdf file that has been uploaded to the server.
        And save the summary to the database/resources.
        """
        title, Paper, tables, figures = self.layout_model.extract_pdf(self.documents_path + '/' + file_name)
        authors, summary, keywords, keyresults, limitations = self._read(Paper, reader)
        response = {
          'title': title,
          'authors': authors,
          'summary': summary,
          'key_concepts': keywords,
          'highlights': keyresults,
          'limitations': limitations,
          'figures': [],
          'tables': [],
        }
        
        if not os.path.exists(self.resources_path + '/' + file_name[:-4]):
            os.mkdir(self.resources_path + '/' + file_name[:-4])
        
        with open(self.resources_path + '/' + file_name[:-4] + '/info.json', 'w') as f:
            json.dump(response, f)
        
        with open(self.resources_path + '/' + file_name[:-4] + '/title.txt', 'w') as f:
            f.write(title)
        
        for idx, table in enumerate(tables):
            im = Image.fromarray(table)
            local_fn = file_name[:-4] + '*' + str(idx) + '_table.png'
            table_fn = self.resources_path + '/' + file_name[:-4] + '/' + str(idx) + '_table.png'
            im.save(table_fn)
            response['tables'].append(local_fn)
        
        for idx, fig in enumerate(figures):
            im = Image.fromarray(fig)
            local_fn = file_name[:-4] + '*' + str(idx) + '_fig.png'
            fig_fn = self.resources_path + '/' + file_name[:-4] + '/' + str(idx) + '_fig.png'
            im.save(fig_fn)
            response['figures'].append(local_fn)
        
        return response

    def retrieve_summary(self, file_name: str):
        """
        Returns a summary of the document (retrieve from resources), this document is a pdf file that already in the server.
        """
        if not os.path.exists(self.resources_path + '/' + file_name[:-4]):
            raise Exception('File not found')
        
        response = {
          'title': None,
          'authors': None,
          'summary': None,
          'key_concepts': None,
          'highlights': None,
          'limitations': None,
          'figures': [],
          'tables': [],
        }
        
        with open(self.resources_path + '/' + file_name[:-4] + '/title.txt', 'r') as f:
            response['title'] = f.read()
        
        response_js = json.load(open(self.resources_path + '/' + file_name[:-4] + '/info.json'))
        response['authors'] = response_js['authors']
        response['summary'] = response_js['summary']
        response['key_concepts'] = response_js['key_concepts']
        response['highlights'] = response_js['highlights']
        response['limitations'] = response_js['limitations']
          
        for fn in os.listdir(self.resources_path + '/' + file_name[:-4]):
            fn = file_name[:-4] + '*' + fn
            if 'fig' in fn:
                response['figures'].append(fn)
            else:
                response['tables'].append(fn)
        return response
    
    def _read(self, Paper, reader):
        """
        Read the text and returns the authors, summary, keywords, keyresults and limitations
        """
        # TODO: Currently we use the Doc Reader service to read the text, but we need to implement our own service
        response = defaultdict(str)
        for query_type, prompt in self.prompt_tail.items():
            ans_query = reader.predict(prompt + "".join(Paper[:500].split(" ")[:20]))
            response[query_type] = ans_query
        
        return response['authors'], response['summary'], response['keywords'], response['keyresults'], response['limitations']