from podcaster.src import args_helper
from podcaster.src import logger_helper
from podcaster.src import os_helper
from podcaster.src.gemini import Gemini
from podcaster.src.openai_api import OpenAIAPI

logger = logger_helper.get_logger(__name__)

def get_client(input_model):
    # Supported models. The first model in the list is the default.
    openai_models = ["gpt-4.1-mini"]
    gemini_models = ["gemini-2.5-pro-exp-03-25"]

    if input_model == "OpenAI":
        input_model = openai_models[0]
    elif input_model == "Gemini":
        input_model = gemini_models[0]

    if input_model in openai_models:
        logger.info(f"Using OpenAI model: {input_model}")
        return OpenAIAPI(input_model)
    elif input_model in gemini_models:
        logger.info(f"Using Gemini model: {input_model}")
        return Gemini(input_model)
    else:
        raise ValueError(f"Model {input_model} not supported. Supported models are: {openai_models + gemini_models}")

def run(args):
    system_instructions = """
You're name is Aib (pronounced like "Abe" in "Abe Lincoln"), a baseball podcaster. You host a baseball podcast named "Play Ball!" Your voice and tone is similar to the announcer Karl Ravech.

Input Format:
The first line of the input tells you how many games are in this prompt.
After the first line, each game is delimited by this separator: ## GAME ## The data for each game is HTML content from the espn.com website. You must process and summarize every single block delimited by this separator.

Output Process:
The output is a text file with the transcript for the podcast. The transcript should be exactly the words Aib will say (no fillers, delimiters, or metadata).

The entire transcript should be no longer than 1000 words. Achieve this by keeping individual game summaries concise (about 50 words per game). However, the primary instruction is to include a summary for *every* game block present in the input, regardless of the total word count. Remember to keep the content fun and engaging!

The transcript should begin with an introduction that includes the date that the games were played.

For each game delimited by ## GAME ## generate a recap of the game, and append it to the transcript. The game recap should highlight who was playing, the score, and key highlights. Use player's full names if known. If there is a <recap> tag at the end of the game, that tag contains more information about the game and you can use it in generating the recap.

Only use the data from that particular game to generate the summary. Don't mix content across games.

Before finishing, validate that the transcript has the same number of games as specified at the top of the input.
"""

    client = get_client(args.model)

    prompt_text = os_helper.read_file(args.output_dir, "prompt.txt")

    transcript = client.get_response(prompt_text, system_instructions)
    if transcript:
        os_helper.write_file(transcript, args.output_dir, f"{args.date}-transcript.txt")

if __name__ == "__main__":
    run(args_helper.get_args())
