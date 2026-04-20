'''
Common data structures used for annotated data.
'''

import enum
import pydantic


##########################################################
class BoundingBox(pydantic.BaseModel):
    '''
    A rectangular bounding box.
    Assumes that the coordinate system has the origin (0, 0) in the top-left corner.
    '''

    x: int
    '''
    Top-left x-coordinate of the bounding box.
    '''

    y: int
    '''
    Top-left y-coordinate of the bounding box.
    '''

    width: int
    '''
    The width of the bounding box.
    '''

    height: int
    '''
    The height of the bounding box.
    '''

    ##########################################################
    def x2(self) -> int:
        '''
        Convenience function to compute the bottom-right x-coordinate of the bounding box.

        :return: The botton-right x-coordinate of the bounding box.
        '''
        return self.x + self.width

    ##########################################################
    def y2(self) -> int:
        '''
        Convenience function to compute the bottom-right y-coordinate of the bounding box.

        :return: The botton-right y-coordinate of the bounding box.
        '''
        return self.y + self.height


##########################################################
class Language(enum.Enum):
    '''
    Enumeration for specifying the language of a paragraph.
    '''

    MALTESE = 'Maltese'
    '''
    Used for paragraphs that are mainly Maltese.
    '''

    NON_MALTESE = 'Non-Maltese'
    '''
    Used for paragraphs that are mainly non-Maltese.
    '''

    MIXED = 'Mixed'
    '''
    Used for paragraphs that are split between Maltese and non-Maltese text (e.g. translation
    glosses).
    '''

    ##########################################################
    def __str__(
        self,
    ) -> str:
        '''
        String conversion override.

        :return: The enum name.
        '''
        return self.name


##########################################################
class Page(pydantic.BaseModel):
    '''
    Information about the page being described.
    '''

    page_fname: str
    '''
    The file name of the page image.
    '''

    document_id: str
    '''
    The unique ID of the document that the page belongs to.
    '''

    page_id: str
    '''
    The unique ID of the page within the document.
    '''


##########################################################
class OCRBox(pydantic.BaseModel):
    '''
    Information about a bounding box annotation in OCR data.
    '''

    box: BoundingBox
    '''
    The bounding box information.
    '''

    transcription: str
    '''
    The transcription of what is written inside the bounding box.
    '''

    language: Language
    '''
    The language of the text in the bounding box.
    '''


##########################################################
class OCRPageData(pydantic.BaseModel):
    '''
    OCR annotations for a whole page.
    '''

    page: Page
    '''
    Information about the page being described.
    '''

    boxes: list[OCRBox]
    '''
    A list of information about OCR boxes within the page.
    '''


##########################################################
class OCRData(pydantic.BaseModel):
    '''
    OCR data set.
    '''

    data: list[OCRPageData]
    '''
    A list of annotated pages.
    '''


##########################################################
class Point(pydantic.BaseModel):
    '''
    An x-y coordinate.
    Assumes that the coordinate system has the origin (0, 0) in the top-left corner.
    '''

    x: int
    '''
    X-coordinate of the point.
    '''

    y: int
    '''
    Y-coordinate of the point.
    '''


##########################################################
class LayoutLabel(enum.Enum):
    '''
    Enumeration for specifying the label of a page layout region according to DocLayNet classes.
    '''

    TEXT = 'Text'
    '''
    Used for Text regions.
    '''

    PICTURE = 'Picture'
    '''
    Used for Picture regions.
    '''

    FORMULA = 'Formula'
    '''
    Used for Formula regions.
    '''

    SECTION_HEADER = 'Section-header'
    '''
    Used for Section-header regions.
    '''

    PAGE_FOOTER = 'Page-footer'
    '''
    Used for Page-footer regions.
    '''

    PAGE_HEADER = 'Page-header'
    '''
    Used for Page-header regions.
    '''

    FOOTNOTE = 'Footnote'
    '''
    Used for Footnote regions.
    '''

    TABLE = 'Table'
    '''
    Used for Table regions.
    '''

    CAPTION = 'Caption'
    '''
    Used for Caption regions.
    '''

    LIST_ITEM = 'List-item'
    '''
    Used for List-item regions.
    '''

    TITLE = 'Title'
    '''
    Used for Title regions.
    '''


    ##########################################################
    def __str__(
        self,
    ) -> str:
        '''
        String conversion override.

        :return: The enum name.
        '''
        return self.name


##########################################################
class LayoutPolygon(pydantic.BaseModel):
    '''
    Information about a polygon annotation in page layout data.
    '''

    polygon: list[Point]
    '''
    The polygon information.
    '''

    label: LayoutLabel
    '''
    The label of the polygon.
    '''

    ##########################################################
    def get_topmost_y(
        self,
    ) -> int:
        '''
        Get the minimum y-coordinate from the vertices in the polygon.

        :return: The topmost y.
        '''
        return min(pt.y for pt in self.polygon)

    ##########################################################
    def get_leftmost_x(
        self,
    ) -> int:
        '''
        Get the minimum x-coordinate from the vertices in the polygon.

        :return: The leftmost x.
        '''
        return min(pt.x for pt in self.polygon)


##########################################################
class LayoutPageData(pydantic.BaseModel):
    '''
    Page layout annotations for a whole page.
    '''

    page: Page
    '''
    Information about the page being described.
    '''

    polygons: list[LayoutPolygon]
    '''
    A list of information about Page Layout polygons within the page.
    '''


##########################################################
class LayoutData(pydantic.BaseModel):
    '''
    Page layout data set.
    '''

    data: list[LayoutPageData]
    '''
    A list of annotated pages.
    '''


##########################################################
class PipelineChannel(enum.Enum):
    '''
    Enumeration for specifying the channel of a list of texts to be generated by a Layout-OCR
    pipeline.
    '''

    TEXT = 'Text'
    '''
    Used for Title, Section-header, Text, and List-item regions.
    '''

    FOOTNOTE = 'Footnote'
    '''
    Used for Footnote regions.
    '''

    CAPTION = 'Caption'
    '''
    Used for Caption regions.
    '''

    ##########################################################
    def __str__(
        self,
    ) -> str:
        '''
        String conversion override.

        :return: The enum name.
        '''
        return self.name


##########################################################
class PipelinePageData(pydantic.BaseModel):
    '''
    Pipeline annotations for a whole page.
    '''

    page: Page
    '''
    Information about the page being described.
    '''

    channels: dict[PipelineChannel, list[OCRBox]]
    '''
    The list of texts in the page separated into channels.
    '''


##########################################################
class PipelineData(pydantic.BaseModel):
    '''
    Layout-OCR pipeline data set.
    '''

    data: list[PipelinePageData]
    '''
    A list of annotated pages.
    '''


##########################################################
class BaselinePageData(pydantic.BaseModel):
    '''
    Baseline text extractions for a whole page.
    '''

    page: Page
    '''
    Information about the page being described.
    '''

    texts: list[str]
    '''
    The list of texts in the page.
    '''


##########################################################
class BaselineData(pydantic.BaseModel):
    '''
    Baseline text extraction data set.
    '''

    data: list[BaselinePageData]
    '''
    A list of annotated pages.
    '''
