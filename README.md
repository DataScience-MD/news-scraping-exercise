# Data Science Tools and Techniques

(C) 2019 Mark M. Bailey

Modifications to the main repo by team Bad Ozone Grasshoppers 
## About
This repository contains code and supporting documents for the News Scraping exercise.  Modifications to this code were made by the Bad Ozone Grasshoppers.

## BLUF
**Usage:** Execute [Colab based Jupyter notebook](https://github.com/PurpleDin0/news-scraping-exercise/blob/master/Execution_Notebook.ipynb) to run code in online sandbox, or run [news_reuters.py](https://github.com/PurpleDin0/news-scraping-exercise/blob/master/news_reuters.py) from a python3 environment. 

**Requirements:** Construct a web scraping module to extract information from a U.S. News site.  

**Proposed Solution:** A python script that retrieves the top 100 articles from Reuters website.  A Colab notebook will then be used to load all relevant libraries, GitHub code, execute the python code, and then save the resulting information.  This approach is being performed as it enables execution of the code from any location regardless of client configuration.  Additionally, this code may assist other distance learning students that have issues with their local install of Python.

**Task List**
* [X] Primary task: Construct a web scraping module for a U.S. News site
  * [X] Secondary Task: Create [requirements.txt](https://github.com/PurpleDin0/news-scraping-exercise/blob/master/requirements.txt) file to facilitate dependency installation.
  * [X] Secondary Task: Build [Colab based Jupyter notebook](https://github.com/PurpleDin0/news-scraping-exercise/blob/master/Execution_Notebook.ipynb) that runs web scraping module.
  * [X] Secondary Task: Build section in Colab notebook that exports data to user's google drive.
* [X] Primary task: update [news_reuters.py](https://github.com/PurpleDin0/news-scraping-exercise/blob/master/news_reuters.py)
  * [X] Secondary Task: Add feature to execute selenium using chrome or Firefox based on a passed option
  * [X] Secondary Task: Updated to use pandas to read and save JSON files instead of pickle files 
  * [X] Secondary Task: update get_soup_links() function to remove duplicate links from links list prior to returning list
  * [X] Secondary task: On 19 May 2019 [news_reuters.py](https://github.com/PurpleDin0/news-scraping-exercise/blob/master/news_reuters.py) broke as https://www.reuters.com/theWire format changed.  Updated code to work on new webpage.
