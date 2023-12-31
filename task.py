import shutil
import os
from nyposts import NyPosts
from directories import DIRS
from logger import logger
from workitems import workitems


class ProcessFlow:
    def __init__(self) -> None:
        self.workitems = workitems()

    def make_dirs(self) -> None:
        """
        Builds required DIRS.
        """
        if not os.path.exists(DIRS.OUTPUT):
            os.mkdir(DIRS.OUTPUT)
        if not os.path.exists(DIRS.IMAGE_DIR):
            os.mkdir(DIRS.IMAGE_DIR)

    def run_process(self):

        try:
            posts = NyPosts()
            flag = False

            logger.info('Opens the Website.')
            posts.open_website()
            logger.info('Website successfully opened.')

            logger.info(f'Searching for the phrase {posts.phrase}')
            news_available, message = posts.phrase_search()
            logger.info('Search completed.')

            logger.info(
                f'Applying filters for Section:{posts.section}  Month: {posts.months}')
            if news_available:

                posts.set_dates()
                logger.info("date seclected")
                posts.sort_by()
                logger.info("sorting....")
                posts.select_sections()
                logger.info('Filter is successfully applied')
                flag = True

            else:
                logger.info(message)
                logger.info('Ending the process.')

            if flag:

                logger.info(
                    'Intializing the fetching all data and uploading all the news in the excel file.')
                posts.get_required_data()
                logger.info(
                    'The news is successfully uploaded in the excel file.')
                logger.info("Ending the process.")
                shutil.make_archive(DIRS.ARCH_Path,
                                    'zip', DIRS.IMAGE_DIR)
                shutil.rmtree(DIRS.IMAGE_DIR)
                posts.close()

            else:
                logger.info('Applying filters not successful.')
                logger.info('Ending the process.')
                posts.close()
                posts.close()

        except Exception as e:
            posts.browser.screenshot(
                filename=DIRS.ERROR_SCREENSHOT_PATH)
            posts.close()
            raise e

    def start_process(self) -> None:
        self.run_process()


def tasks():
    """
    Initilize the process.
    """

    process = ProcessFlow()
    process.start_process()


if __name__ == "__main__":
    logger.info('Initializing the Process')
    tasks()
    logger.info("Done.")
