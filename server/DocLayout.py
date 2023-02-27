import pdf2image
import numpy as np
import layoutparser as lp
from collections import defaultdict

class DocLayout(object):
  def __init__(self) -> None:
    self.model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    self.ocr_agent = lp.TesseractAgent(languages='eng')

  def extract_pdf(self, file_name: str):
      """ From a local file pdf file, extract the title, text, tables and figures

      Args:
          file_name (str): path to the pdf file

      Returns:
          title (str): title of the paper
          Paper (str): text of the paper
          table_by_page (dict(list)): dictionary of tables by page, each page has a list of tables, represent by 3D numpy array
          figure_by_page (dict(list)): dictionary of figures by page, each page has a list of figures, represent by 3D numpy array
      """
      list_of_pages = pdf2image.convert_from_path(file_name)
      images = [np.asarray(page) for page in list_of_pages]
      image_width = len(images[0][0])

      header_blocks, text_blocks, table_blocks, figure_blocks = self._detect_element(images)

      title = self._extract_title(image_width, images, header_blocks)
      Paper = self._extract_text_info(image_width, images, text_blocks)
      table_by_page, figure_by_page = self._extract_table_n_figure(image_width, images, table_blocks, figure_blocks)
      # Currently we dont care about the order of the figures or tables returned
      tables = self._general_by_table_to_list(table_by_page)
      figures = self._general_by_table_to_list(figure_by_page)
      return title, Paper, tables, figures
  
  def _general_by_table_to_list(self, general_by_page: dict):
      return [general for i in general_by_page.keys() for general in general_by_page[i]]
  
  def _detect_element(self, images):
      types = ['Title', 'Text', 'Table', 'Figure']
      type_blocks = {
          t: defaultdict(list) for t in types
      }
      for i in range(len(images)):
          layout_result = self.model.detect(images[i])
          for t in types:
              type_block = lp.Layout([b for b in layout_result if b.type==t])
              if len(type_block) != 0:
                  type_blocks[t][i] = type_block
      return type_blocks.values()
  
  
  def _extract_title(self, image_width, images, header_blocks):
      """
      Extract the title of the article from several headers
      """
      first_page = min(header_blocks.keys())
      segment_title = self._extract_page(first_page, image_width, images, header_blocks)[0]
      title = self.ocr_agent.detect(segment_title)
      return title
  
  def _extract_text_info(self, image_width, images, text_blocks):
      """
      Returns all the text in the article
      """
      Paper = ""
      for page_id in text_blocks:
          text_block_images = self._extract_page(page_id, image_width, images, text_blocks)
          for block in text_block_images:
              text = self.ocr_agent.detect(block).strip()
              Paper += text + " "
      return Paper

  def _extract_table_n_figure(self, image_width, images, table_blocks, figure_blocks):
      """Extract 3D numpy array of tables and figures from deteced layout

      Args:
          image_width (int): width of image
          images (_type_): _description_
          table_blocks (_type_): _description_
          figure_blocks (_type_): _description_

      Returns:
          table_by_page, figure_by_page (dict(list)): 3D numpy array of tables and figures by page
      """
      
      table_by_page, figure_by_page = defaultdict(list), defaultdict(list)
      for page_id in table_blocks:
          results = self._extract_page(page_id, image_width, images, table_blocks )
          table_by_page[page_id] = results
      
      for page_id in figure_blocks:
          results = self._extract_page(page_id, image_width, images, figure_blocks)
          figure_by_page[page_id] = results
      
      return table_by_page, figure_by_page

  def _extract_page(self, page_id, image_width, images, general_blocks):
      """ 
      Get a list of 3D array numpy image of tables and figures, or text from a page
      """
      results = []
      left_interval = lp.Interval(0, image_width/2, axis='x').put_on_canvas(images[page_id])
      left_blocks = general_blocks[page_id].filter_by(left_interval, center=True)._blocks
      left_blocks.sort(key = lambda b: b.coordinates[1])

      # Sort element ID of the right column based on y1 coordinate
      right_blocks = [b for b in general_blocks[page_id] if b not in left_blocks]
      right_blocks.sort(key = lambda b: b.coordinates[1])

      # Sort the overall element ID starts from left column
      general_block = lp.Layout([b.set(id = idx) for idx, b in enumerate(left_blocks + right_blocks)])

      # Crop image around the detected layout
      for block in general_block:
          segment_image = (block
                              .pad(left=15, right=15, top=5, bottom=5)
                              .crop_image(images[page_id]))
          results.append(segment_image)

      return results