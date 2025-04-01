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
