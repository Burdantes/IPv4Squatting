from collections import Counter
import re

def parse_documents(filename):
    """
    Reads a text file and returns a list of lines.
    """
    with open(filename, 'r') as f:
        return f.readlines()

parse_documents('as_with_customer_xaa.txt')

def count_occurences_of_regex(regex, documents):
    """
    Counts the number of occurences of a regex in a list of documents.
    """
    return len([line for line in documents if re.search(regex, line)])

def find_the_k_word_that_appears_the_most_often(documents,k):
    """
    Finds the top k word that appears the most often in a list of documents.
    """
    list_of_words = []
    for i in documents:
        i = i.replace('\n','')
        list_of_words.extend(i.split('.')[0:-1])
    count_of_words = Counter(list_of_words)
    return count_of_words.most_common(k)

def argparsing():
    """
    Parses the command line arguments.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Finds the word that appears the most often in a list of documents.')
    parser.add_argument('filename', help='The name of the file to read.')
    return parser.parse_args()


if __name__ == '__main__':
    args = argparsing()
    documents = parse_documents(args.filename)
    print(find_the_k_word_that_appears_the_most_often(documents,1000))
    print('End of script.')
