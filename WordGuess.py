import argparse
import operator
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import random
# import deepdiff
# import json
# from collections import Counter
import nltk
import os

try:
    import pygame
    pygame_inst = True
except ImportError:
    pygame_inst = False

def word_preprocess(text):
    '''
        Input: NLTK text object containing raw text.
        Output: Processed tokens and nouns from text.
        
        Processes text and selects only large tokens which are not stopwords and greater than length 5. After lemmatizing and getting set of unique lemmas, 
        they are tagged according to their POS and the noun tokens are selected.
    '''

    #Filtering tokens and selecting the ones that are alpha, not in the NLTK stopword list, and have length > 5

    filter_toks = [t.lower() for t in text if t.isalpha() and
        t not in stopwords.words('english') and len(t)>5]
    

    word_lem = WordNetLemmatizer()
    lemm_toks = [word_lem.lemmatize(t) for t in filter_toks]
    set_lemm_toks = set(lemm_toks)

    #POS Tagging

    tok_tags = nltk.pos_tag(set_lemm_toks)
    print(tok_tags[:20])

    #Filter noun tokens
    noun_toks = [pt[0] for pt in tok_tags if pt[1]=='NN']

    print(f"\nNumber of tokens:{len(filter_toks)}\nNumber of Nouns:{len(noun_toks)}\n")
    return filter_toks,noun_toks

def word_guess_game(noun_list,score = 5):
    '''
        Input: List of words/nouns to use. Should be 50 but will accept any non-empty list. Starting score is set to 5 by default 
        but can be passed as an optional argument. 
        Output: The final score of the player. Also can return error codes.
            -2 : Invalid List
            -3 : Invalid Score
    '''

    #Input checking 
    if(not noun_list):
        return -2
    if(not isinstance(score,int) or score < 0):
        return -3

    #Set up game
    print("\nLet's play a game! Press ! to end the game. The game ends when your score goes negative.\n")
    letter_input = "#"
    current_word = ""
    current_guesses = ['_']
                                    
    #Guessing loop
    while score > -1:

        #Word complete. FLag to replace with new word.
        if('_' not in current_guesses):
            if (pygame_inst):right_sound.play()
            letter_input = "#"
            print("You guessed the word correctly!\n")
        
        #Start new word guessing process.
        if(letter_input == "#"):
            current_word = list(random.choice(noun_list))
            current_guesses = ['_']*len(current_word)
            print("Start Guessing!\n")
        
        #Print text for each turn.
        format_guesses = ' '.join(map(str, current_guesses))
        print(format_guesses)
        letter_input = input("Guess a letter: ")

        #Stop in case of end character
        if(letter_input == '!'):
            break
        
        #Making sure guess is a single letter
        if(not letter_input.isalpha() or len(letter_input)>1):
            print("Invalid guess! Please enter a single letter.")
            continue
        
        #Set up
        guess = letter_input.lower()
        feed_text = ""

        #Check if letter in word
        if(guess in current_word):
            if (pygame_inst):correct_sound.play()
            score += 1
            feed_text = "Correct! Keep going. "
            guess_idx = current_word.index(guess)
            current_word[guess_idx] = '#'
            current_guesses[guess_idx] = guess
        else:
            if (pygame_inst):incorrect_sound.play()
            score -= 1
            feed_text = "Wrong! Try again. "
        
        #Give feedback
        print(f"{feed_text}Current score: {score}\n")

    if(score > -1):
        print(f"Well done! Your score is {score}")
    else:
        if (pygame_inst):wrong_sound.play()
        original_word = [max(i,j) for i,j in zip(current_guesses,current_word)]
        original_word = ''.join(original_word)
        print(f"You failed! The word was {original_word}.Try again.")

    return score


if __name__ == "__main__":

    #Get filename as arg
    parser = argparse.ArgumentParser("wordguess")
    parser.add_argument("filename", help="Please give the filename of the text to use", type=str)
    args = parser.parse_args()
    print(args.filename)

    #Create NLTK Text obj
    corpus0 = PlaintextCorpusReader(os.getcwd(), args.filename)
    corpus  = nltk.Text(corpus0.words())

    # Calculate Lexical Diversity

    # Note that the tokens are first converted to lowercase, the stopwords are removed and only alphabetical tokens are considered.
    lower_toks = [t.lower() for t in corpus if t.isalpha() and
           t not in stopwords.words('english')]
    set_toks = set(lower_toks)
    
    lex_diversity = len(set_toks)/len(lower_toks)

    print(f"\nLexical Diversity : {lex_diversity:0.2f}\n")

    toks, nouns = word_preprocess(corpus)

    #Compute token distribution using FreqDist and add noun freq to dictionary
    tok_dist = nltk.FreqDist(toks)
    noun_count_dict = {w:tok_dist[w] for w in nouns}

    sorted_noun_dict = sorted(noun_count_dict.items(), key=operator.itemgetter(1), reverse=True)

    print(f"Top 50 nouns in document:\n{sorted_noun_dict[:50]}")

    #Saving keys to list
    noun_list = [noun[0] for noun in sorted_noun_dict[:50]]
    
    #Game set up
    start_game = 'y'
    best_score = -1

    #Initialize pygame sounds if pygame installed
    if(pygame_inst):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)
        correct_sound = pygame.mixer.Sound(os.path.join(os.getcwd(),"effects","ding-sound-effect_1.mp3"))
        incorrect_sound = pygame.mixer.Sound(os.path.join(os.getcwd(),"effects","answer-wrong.mp3"))
        right_sound = pygame.mixer.Sound(os.path.join(os.getcwd(),"effects","the_price_is_right_ding.mp3"))   
        wrong_sound = pygame.mixer.Sound(os.path.join(os.getcwd(),"effects","jeopardy-incorrect-answer.mp3"))
        high_score_sound = pygame.mixer.Sound(os.path.join(os.getcwd(),"effects","nsmb-new-high-score.mp3"))

    #Starting game loop
    while start_game != 'n':
        start_game = input("\nStart new word guessing game? y/n: ")
        if(start_game not in 'yn'):
            print("Invalid input! Press either y or n.")
        if(start_game == 'y'):
            score = word_guess_game(noun_list)
            if(score > best_score):
                print("You beat your previous best!")
                if (pygame_inst):high_score_sound.play()
            else:
                print(f"Your best score is {best_score}!")
            best_score = max(best_score, score)
