**WEB CRAWLER PROJECT**

This project is about a web crawler capable of extracting text by crawling through pages starting with a Base URL (https://quotes.toscrape.com/'). 
It also allows users to search for words or phrases after an inverted index has been built after the crawling process. (refer to the index.csv file)

**USER MANUAL**
There are 4 commands to use in this tool: 
1. build: Crawls through all web pages, starting from https://quotes.toscrape.com/'. It will also create an inverted index showcasing all URLs and individual words, saving it into a CSV file.
2. load: Loads the created inverted index into the program.
3. print: Prints out a ranked list of URLs containing the users queried word. This function works on single words only.
4. find: Prints out a ranked list of URLs containing the users queried phrase, followed by URLs of the individual words. 
   
The ‘load’ command would not work unless the ‘build’ command is run. The ‘print’ and ‘find’ 
command would not also work unless the ‘load’ command is run first. 

Users must run the ‘build’ command first, which crawls all web pages within the base URL 
and saves the inverted index into a CSV file. They should then run ‘load’ which loads the 
inverted index from the CSV file.  

When using the ‘print’ command, users must enter in the form of ‘print <word>’, where 
<word> is the word they intend to search for. It is limited to one word only so 2 arguments 
are required. An example would be ‘print hello’. 

When using the ‘find’ command, users must enter in the form of ‘find <word> <word>’, 
where the number of queried words are not limited. An example usage would be ‘find good 
books’.
