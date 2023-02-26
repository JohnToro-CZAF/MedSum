import pdf2image
import numpy as np
import layoutparser as lp
import torch
import gc
from PIL import Image
from collections import defaultdict
import os
import openai
import json

class DocSummarizer(object):
    def __init__(self, documents_path: str, resources_path: str):
        self.documents_path = documents_path
        self.resources_path = resources_path
        self.model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                    label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
        self.ocr_agent = lp.TesseractAgent(languages='eng')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.prompt_tail = {'summary':"\n\nSummarize the above text, focus on key insights",
                            'keyresult':'''\n\nGive me three key results in the format of "Key results:
                                          1.  Key result 1
                                          2. Key result 2
                                          3. Key result 3"''',
                            'keyword':'\n\nGive me keywords in the format of "Keywords:  Keyword 1, Keyword 2, Keyword 3"',
                            'limitations':'\n\nGive me 3 sentences describing the limitations of the text above.'}

    def get_summary(self, file_name: str):
        """
        Returns a summary of the document, this document is a pdf file that has been uploaded to the server.
        And save the summary to the database/resources.
        """
        title, author, summary, keywords, keyresults, limitations, tables, figures = self.blockify_pdf(self.documents_path + '/' + file_name)
        response = {
          'title': title,
          'authors': author,
          'summary': summary.choices[0].text,
          'key_concepts': keywords.choices[0].text,
          'highlights': keyresults.choices[0].text,
          'limitations': limitations.choices[0].text,
          'figures': [],
          'tables': [],
        }
        
        if not os.path.exists(self.resources_path + '/' + file_name[:-4]):
          os.mkdir(self.resources_path + '/' + file_name[:-4])
        
        with open(self.resources_path + '/' + file_name[:-4] + '/info.json', 'w') as f:
            json.dump(response, f)
        
        with open(self.resources_path + '/' + file_name[:-4] + '/title.txt', 'w') as f:
          f.write(title)
        
        for p in tables.keys():
            for idx, table in enumerate(tables[p]):
                im = Image.fromarray(table)
                local_fn = file_name[:-4] + '*' + str(p) +str(idx) + '_table.png'
                table_fn = self.resources_path + '/' + file_name[:-4] + '/' + str(p) +str(idx) + '_table.png'
                im.save(table_fn)
                response['tables'].append(local_fn)
        
        for p in figures.keys():
            for idx, fig in enumerate(figures[p]):
                im = Image.fromarray(fig)
                local_fn = file_name[:-4] + '*' + str(p) +str(idx) + '_fig.png'
                fig_fn = self.resources_path + '/' + file_name[:-4] + '/' + str(p) +str(idx) + '_fig.png'
                im.save(fig_fn)
                response['figures'].append(local_fn)
        print(response)
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
            # fn = os.path.abspath(fn)
            fn = file_name[:-4] + '*' + fn
            if 'fig' in fn:
                response['figures'].append(fn)
            else:
                response['tables'].append(fn)
            print(fn)
        print(response)
        return response
    
    def _detect_element(self, images):
        title_blocks = defaultdict(int)
        text_blocks = defaultdict(int)
        table_blocks = defaultdict(int)
        figure_blocks = defaultdict(int)

        for i in range(len(images)):
            # Detect and divide
            layout_result = self.model.detect(images[i])
            title_block = lp.Layout([b for b in layout_result if b.type=='Title'])
            text_block = lp.Layout([b for b in layout_result if b.type=='Text'])
            table_block = lp.Layout([b for b in layout_result if b.type=='Table'])
            figure_block = lp.Layout([b for b in layout_result if b.type=='Figure'])
            
            # Add result
            if len(title_block) != 0:
                title_blocks[i] = title_block
            if len(text_block) != 0:
                text_blocks[i] = text_block
            if len(table_block) != 0:
                table_blocks[i] = table_block
            if len(figure_block) != 0:
                figure_blocks[i] = figure_block
            
            # Garbage collection
            del title_block, text_block, figure_block, table_block
        if self.device == 'cuda':
            torch.cuda.empty_cache()
            gc.collect()
        return (title_blocks, text_blocks, table_blocks, figure_blocks)
    
    def _extract_title(self, image_width, images, title_blocks):
        # Extract for title
        first_page = min(title_blocks.keys())

        # Sort element ID of the left column based on y1 coordinate
        left_interval = lp.Interval(0, image_width/2, axis='x').put_on_canvas(images[first_page])
        left_blocks = title_blocks[first_page].filter_by(left_interval, center=True)._blocks
        left_blocks.sort(key = lambda b:b.coordinates[1])

        # Sort element ID of the right column based on y1 coordinate
        right_blocks = [b for b in title_blocks[first_page] if b not in left_blocks]
        right_blocks.sort(key = lambda b:b.coordinates[1])

        # Sort the overall element ID starts from left column
        title_block = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

        # Crop image around the detected layout
        segment_image = (title_block[0]
                            .pad(left=15, right=15, top=5, bottom=5)
                            .crop_image(images[first_page]))
            
        # Perform OCR
        title = self.ocr_agent.detect(segment_image)
        return title
    
    def _extract_key_text_info(self, image_width, images, text_blocks):
        first_page = min(text_blocks.keys())

        # Sort element ID of the left column based on y1 coordinate
        left_interval = lp.Interval(0, image_width/2, axis='x').put_on_canvas(images[first_page])
        left_blocks = text_blocks[first_page].filter_by(left_interval, center=True)._blocks
        left_blocks.sort(key = lambda b:b.coordinates[1])

        # Sort element ID of the right column based on y1 coordinate
        right_blocks = [b for b in text_blocks[first_page] if b not in left_blocks]
        right_blocks.sort(key = lambda b:b.coordinates[1])

        # Sort the overall element ID starts from left column
        text_block = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

        # Crop image around the detected layout
        segment_author = (text_block[0]
                            .pad(left=15, right=15, top=5, bottom=5)
                            .crop_image(images[first_page]))
        author = self.ocr_agent.detect(segment_author)
        prompt = ''

        for block in text_block[1:]:
            # Crop image around the detected layout
            segment_image = (block
                              .pad(left=15, right=15, top=5, bottom=5)
                              .crop_image(images[first_page]))
            # Perform OCR
            text = self.ocr_agent.detect(segment_image)
            # Save OCR result
            prompt += text
        
        long_prompt = ''
        for page in text_blocks:
            for block in text_blocks[page]:
                segment_image = (block
                              .pad(left=15, right=15, top=5, bottom=5)
                              .crop_image(images[first_page]))
                # Perform OCR
                text = self.ocr_agent.detect(segment_image)
                # Save OCR result
                long_prompt += text

        summary = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt + self.prompt_tail['summary'],
                    temperature=0.7,
                    max_tokens=60,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=1
                  )
        keywords = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt + self.prompt_tail['keyword'],
                    temperature=0.7,
                    max_tokens=200,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=1
                  )
        keyresults = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=prompt + self.prompt_tail['keyresult'],
                    temperature=0.7,
                    max_tokens=300,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=1
                  )
        limitations = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=long_prompt + self.prompt_tail['limitations'],
                    temperature=0.7,
                    max_tokens=300,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=1
                  )
        return author, summary, keywords, keyresults, limitations

    def _extract_table_n_figure(self, image_width, images, table_blocks, figure_blocks):
        table_by_page, figure_by_page = defaultdict(list), defaultdict(list)
        
        # Extract tables
        for page in table_blocks:
            left_interval = lp.Interval(0, image_width/2, axis='x').put_on_canvas(images[page])
            left_blocks = table_blocks[page].filter_by(left_interval, center=True)._blocks
            left_blocks.sort(key = lambda b:b.coordinates[1])

            # Sort element ID of the right column based on y1 coordinate
            right_blocks = [b for b in table_blocks[page] if b not in left_blocks]
            right_blocks.sort(key = lambda b:b.coordinates[1])

            # Sort the overall element ID starts from left column
            table_block = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

            # Crop image around the detected layout
            for block in table_block:
                segment_image = (block
                                    .pad(left=15, right=15, top=5, bottom=5)
                                    .crop_image(images[page]))
                table_by_page[page].append(segment_image)
        
        # Extract figures        
        for page in figure_blocks:
            left_interval = lp.Interval(0, image_width/2, axis='x').put_on_canvas(images[page])
            left_blocks = figure_blocks[page].filter_by(left_interval, center=True)._blocks
            left_blocks.sort(key = lambda b:b.coordinates[1])

            # Sort element ID of the right column based on y1 coordinate
            right_blocks = [b for b in figure_blocks[page] if b not in left_blocks]
            right_blocks.sort(key = lambda b:b.coordinates[1])

            # Sort the overall element ID starts from left column
            figure_block = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

            # Crop image around the detected layout
            for block in figure_block:
                segment_image = (block
                                    .pad(left=15, right=15, top=5, bottom=5)
                                    .crop_image(images[page]))
                figure_by_page[page].append(segment_image)
        
        return table_by_page, figure_by_page

    def blockify_pdf(self, file_name: str):
        list_of_pages = pdf2image.convert_from_path(file_name)
        images = [np.asarray(page) for page in list_of_pages]
        image_width = len(images[0][0])

        title_blocks, text_blocks, table_blocks, figure_blocks = self._detect_element(images)

        title = self._extract_title(image_width, images, title_blocks)
        table_by_page, figure_by_page = self._extract_table_n_figure(image_width, images, table_blocks, figure_blocks)
        author, summary, keywords, keyresults, limitations = self._extract_key_text_info(image_width, images, text_blocks)
        return title, author, summary, keywords, keyresults, limitations, table_by_page, figure_by_page