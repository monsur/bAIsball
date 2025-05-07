import os
from bs4 import BeautifulSoup, Comment
from podcaster.src import args_helper
from podcaster.src import logger_helper
from podcaster.src import os_helper

logger = logger_helper.get_logger(__name__)

def run(args):

    def process_boxscore_file(filename):
        logger.info(f"Processing {filename}")
        content = os_helper.read_file(args.output_data_dir, filename)

        soup = BeautifulSoup(content, 'html.parser')

        # Remove script, style, link, and img tags
        for tag in soup.find_all(['script', 'style', 'link', 'img', 'svg']):
            tag.decompose()

        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove HeaderScoreboardWrapper div
        for div in soup.find_all('div', class_='HeaderScoreboardWrapper'):
            div.decompose()

        # Remove PageLayout page-container cf page-footer-container div
        for div in soup.find_all('div', class_='PageLayout page-container cf page-footer-container'):
            div.decompose()

        # Remove fittOverlayContainer div
        for div in soup.find_all('div', id='fittOverlayContainer'):
            div.decompose()

        # Remove fittBGContainer div
        for div in soup.find_all('div', id='fittBGContainer'):
            div.decompose()

        # Remove lightboxContainer div
        for div in soup.find_all('div', id='lightboxContainer'):
            div.decompose()

        # Remove Site Header Wrapper div
        for div in soup.find_all('header', class_='db Site__Header__Wrapper sticky'):
            div.decompose()

        # Remove all classes from all tags
        for tag in soup.find_all(True):  # True matches all tags
            if 'class' in tag.attrs:
                del tag.attrs['class']
            if 'data-react-helmet' in tag.attrs:
                del tag.attrs['data-react-helmet']
            if 'style' in tag.attrs:
                del tag.attrs['style']
            if 'lang' in tag.attrs:
                del tag.attrs['lang']

        # Prune meta tags
        for meta in soup.find_all('meta'):
            if 'charset' in meta.attrs:
                meta.decompose()
            elif 'name' in meta.attrs and meta['name'] == 'viewport':
                meta.decompose()
            elif 'property' in meta.attrs and meta['property'] == 'fb:app_id':
                meta.decompose()
            elif 'property' in meta.attrs and meta['property'].startswith('og:'):
                meta.decompose()
            elif 'name' in meta.attrs and meta['name'].startswith('twitter:'):
                meta.decompose()
            elif 'name' in meta.attrs and meta['name'] == 'medium':
                meta.decompose()
            elif 'name' in meta.attrs and meta['name'] == 'title':
                meta.decompose()
            elif 'http-equiv' in meta.attrs:
                meta.decompose()

        # Get the HTML content
        if args.prettyprint:
            content = soup.prettify()
        else:
            content = str(soup)
            # Remove empty lines
            lines = [line for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)

        return content

    def process_recap_file(filename):
        logger.info(f"Processing {filename}")
        content = os_helper.read_file(args.output_data_dir, filename)
        soup = BeautifulSoup(content, 'html.parser')
        return soup.find(class_='Story__Body t__body').get_text()

    def process_file(filename):
        content = process_boxscore_file(filename)

        try:
            content += "<recap>" + process_recap_file(filename.replace("boxscore", "recap")) + "</recap>"
        except Exception as e:
            logger.info(f"No recap for {filename}")

        os_helper.write_file(content, args.output_data_dir, filename.replace("boxscore", "prompt"))

        return content

    files = [f for f in os.listdir(args.output_data_dir) if f.endswith('boxscore.html')]

    if not files:
        logger.error("No HTML files found in input directory.")
        return

    content = f"There are {len(files)} games in this prompt."
    for filename in files:
        content += "\n\n## GAME ##\n\n"
        content += process_file(filename)
    os_helper.write_file(content, args.output_dir, "prompt.txt")

if __name__ == "__main__":
    run(args_helper.get_args())
