import os
from bs4 import BeautifulSoup, Comment
from podcaster.src import helper

logger = helper.get_logger()

class PromptGenerator:
    def __init__(self, args):
        self.output_dir = args.output_dir
        self.input_dir = os.path.join(args.output_dir, "data")
        self.prettyprint = args.prettyprint
        
    def process_boxscore_file(self, filename):
        with open(os.path.join(self.input_dir, filename), 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script, style, link, and img tags
        for tag in soup.find_all(['script', 'style', 'link', 'img']):
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

        # Get the HTML content
        if self.prettyprint:
            content = soup.prettify()
        else:
            content = str(soup)
            # Remove empty lines
            lines = [line for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
        return content
    
    def process_recap_file(self, filename):
        with open(os.path.join(self.input_dir, filename), 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        return soup.find(class_='Story__Body t__body').get_text()

    def process_file(self, filename):
        content = self.process_boxscore_file(filename)
        content += "<recap>" + self.process_recap_file(filename.replace("boxscore", "recap")) + "</recap>"
        
        prompt_filename = os.path.join(self.output_dir, "data", filename.replace("boxscore", "prompt"))
        with open(prompt_filename, 'w', encoding='utf-8') as f:
            f.write(content)

        return content
    
    def generate(self):
        files = [f for f in os.listdir(self.input_dir) if f.endswith('boxscore.html')]

        if not files:
            logger.error("No HTML files found in input directory.")
            return

        content = f"There are {len(files)} games in this prompt."
        for filename in files:
            content += f"\n\n## GAME ##\n\n"
            content += self.process_file(filename)
            
        with open(os.path.join(self.output_dir, "prompt.txt"), 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    a = helper.get_args()
    generator = PromptGenerator(a)
    generator.generate()

if __name__ == "__main__":
    main() 