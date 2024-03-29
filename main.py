from pdf_populator.util.PathHelper import PathHelper
from pdf_populator.util.VersionManager import VersionManager
from pdf_populator.util.MenuSelector import MenuSelector
from pdf_populator.util.MenuOptions import MainMenuOptions
from pdf_populator.exceptions.PdfFillerException import PdfFillerException
from pdf_populator.PdfPopulator import PdfPopulator
from pdf_populator.util.Logger import Logger
from pdf_populator.util.Config import Config


DEBUG_MODE = False
if DEBUG_MODE:
    print("RUNNING IN DEBUG MODE")

def main():
    VersionManager.isLatestVersion()

    log = Logger.create_logger(DEBUG_MODE)
    config = Config()
    path_helper = PathHelper(DEBUG_MODE)
    pdf_populator = PdfPopulator(path_helper, log, config)
    menu = MenuSelector()

    try:
        pdf_populator.LoadData()
        pdf_populator.LoadTemplates()
        pdf_populator.SelectExcelFile()

        exit_program = False
        while not exit_program:
            main_menu_selection = menu.GetMainMenuSelection()
            if main_menu_selection == MainMenuOptions.POPULATE_PDF:
                pdf_populator.SelectTemplateFile()
                pdf_populator.PopulatePdfTemplate()
                pdf_populator.SavePopulatedTemplate()

            elif main_menu_selection == MainMenuOptions.RELOAD:
                pdf_populator.LoadData()
                pdf_populator.LoadTemplates()
                pdf_populator.SelectExcelFile()

            elif main_menu_selection == MainMenuOptions.EXIT:
                exit_program = True
    except Exception as e:
        log.error(f"An error has occured: {e}")
        raise e

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
        input("Press Enter to exit...")
    except PdfFillerException as e:
        print(f"An error has occured: {e}")
        input("Press Enter to exit...")
