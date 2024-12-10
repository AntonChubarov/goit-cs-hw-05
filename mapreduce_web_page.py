import string
from argparse import ArgumentParser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import matplotlib.pyplot as plt
import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word.lower(), 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text):
    text = remove_punctuation(text)
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def visualize_top_words(word_counts, top_n=10):
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts)
    plt.title("Top Words by Frequency")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.png")
    plt.savefig(filename)
    print(f"plot saved as {filename}")


def parse_arguments():
    parser = ArgumentParser(description="analyze word frequency from a URL and visualize the top words")
    parser.add_argument("--url", required=True, help="URL of the text to analyze")
    parser.add_argument("--top", type=int, default=10, help="number of top words to visualize")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    url = args.url
    top_n = args.top

    text = get_text(url)
    if text:
        word_counts = map_reduce(text)
        visualize_top_words(word_counts, top_n)
    else:
        print("error: unable to fetch text from the provided URL")
