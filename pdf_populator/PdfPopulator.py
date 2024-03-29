import logging
from pathlib import Path
from .util.Config import Config
from .util.Config import DefaultConfigKeys
from .util.WorkbookWrapper import WorkbookWrapper
from .util.PdfWrapper import PdfWrapper
from .util.PathHelper import PathHelper
from .util.MenuSelector import MenuSelector
from .exceptions.NoTemplateFolderFoundException import NoTemplateFolderFoundException
from .exceptions.NoTemplatesFoundException import NoTemplatesFoundException
from .exceptions.NoDataFolderFoundException import NoDataFolderFoundException
from .exceptions.NoExcelFilesFoundException import NoExcelFilesFoundException
from .exceptions.NoWbWrapperInitializedError import NoWbWrapperInitializedError
from .exceptions.NoPdfWrapperInitializedError import NoPdfWrapperInitializedError


menu = MenuSelector()

EXCEL_FOLDER_NAME = "data"
TEMPLATE_FOLDER_NAME = "templates"

class PdfPopulator:

    def __init__(self, path_helper: PathHelper, log: logging.Logger, config: Config):
        self.path_helper = path_helper
        self.log = log
        self.config = config

        self.data_path_base = None
        self.excel_files = []
        self.excel_file_name = None

        self.template_path_base = None
        self.template_files = []
        self.template_file_name = None

        self.wb_wrapper = None
        self.pdf_wrapper = None

        Path(f"./{EXCEL_FOLDER_NAME}/").mkdir(parents=True, exist_ok=True)
        Path(f"./{TEMPLATE_FOLDER_NAME}/").mkdir(parents=True, exist_ok=True)

    def LoadData(self):
        
        self.data_path_base = self.path_helper.findFolderPath(EXCEL_FOLDER_NAME)
        if self.data_path_base is None:
            raise NoDataFolderFoundException()
        
        self.excel_files = self.path_helper.loadFilesInFolder(self.data_path_base)
        if not self.excel_files:
            raise NoExcelFilesFoundException(self.data_path_base)

    def LoadTemplates(self):
        self.template_path_base = self.path_helper.findFolderPath(TEMPLATE_FOLDER_NAME)
        if self.template_path_base is None:
            raise NoTemplateFolderFoundException()
        
        self.template_files = self.path_helper.loadFilesInFolder(self.template_path_base)
        if not self.template_files:
            raise NoTemplatesFoundException(self.template_path_base)
    
    def SelectExcelFile(self):
        if self.data_path_base is None:
            raise NoDataFolderFoundException()
        if not self.excel_files:
            raise NoExcelFilesFoundException(self.data_path_base)
        
        self.excel_file_name = menu.SelectDataFile(self.excel_files)
        excel_file_path = f"{self.data_path_base}/{self.excel_file_name}"
        self.wb_wrapper = WorkbookWrapper(
            excel_file_path, 
            self.config.GetConfigValue(DefaultConfigKeys.DATA_SHEET_NAME), 
            self.log
        )

    def SelectTemplateFile(self):
        if self.template_path_base is None:
            raise NoTemplateFolderFoundException()
        if not self.template_files:
            raise NoTemplatesFoundException(self.template_path_base)
        
        self.template_file_name = menu.SelectTemplateFile(self.template_files)
        template_file_path = f"{self.template_path_base}/{self.template_file_name}"
        self.pdf_wrapper = PdfWrapper(template_file_path, self.log, self.config)

    def PopulatePdfTemplate(self):
        if self.wb_wrapper is None:
            error_msg = "No Workbook Wrapper initialized. Cannot load data to populate pdf template"
            raise NoWbWrapperInitializedError(error_msg)
        if self.pdf_wrapper is None:
            error_msg = "No PDF Wrapper initialized. No PDF template loaded to populate"
            raise NoPdfWrapperInitializedError(error_msg)
        
        for field in self.pdf_wrapper.GetAnnotationFields():
            value = self.wb_wrapper.GetValueFromKey(field)
            if value is None:
                continue
            self.pdf_wrapper.UpdateAnnotationField(field, value)

    def SavePopulatedTemplate(self):
        if self.pdf_wrapper is None:
            error_msg = "No PDF Wrapper initialized. No PDF template to be saved"
            raise NoPdfWrapperInitializedError(error_msg)
        
        output_pdf_file_name = self.GetNewPdfName()
        self.pdf_wrapper.SavePopulatedPdf(output_pdf_file_name)
        print(f"PDF {output_pdf_file_name} successfully generated")
        self.log.info(f"PDF {output_pdf_file_name} successfully generated")
        input("Press Enter to continue...")
        
    def GetNewPdfName(self):
        if self.wb_wrapper is None:
            error_msg = "No Workbook Wrapper initialized. Cannot load data client name."
            raise NoWbWrapperInitializedError(error_msg)
        client_name = self.wb_wrapper.GetValueFromKey(self.config.GetConfigValue(DefaultConfigKeys.CLIENT_FIELD_NAME))
        if client_name is None:
            client_name = ""
        template_name_lower = self.template_file_name.lower()
        output_pdf_file_name = template_name_lower.replace("template", client_name)
        return output_pdf_file_name
