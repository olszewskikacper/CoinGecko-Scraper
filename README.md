# Web Scraping Application

This project is a web scraping application built with Python. 
It features a Flask-based frontend.
Uses BeautifulSoup and Playwright for web scraping.
MySQL for database management. 
Poetry is used for dependency management.

## Table of Contents

- [Features](#features)
- [Preview of the app](#preview-of-the-app)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)

## Features

- **Web Scraping**: Extract data from CoinGecko using BeautifulSoup and Playwright.
- **Data Manipulation**: Reading and writing CSV Files with Pandas
- **Frontend Interface**: A simple web interface built with Flask, HTML, and CSS.
- **Database Management**: Store and retrieve data using MySQL.
- **Dependency Management**: Manage project dependencies with Poetry.

## Preview of the app

![HomePage](https://github.com/olszewskikacper/CoinGecko-Scraper/assets/128138029/65228820-b830-4d44-aad0-8c3c0672378a)

![AllCryptoPage](https://github.com/olszewskikacper/CoinGecko-Scraper/assets/128138029/509a61ba-2409-42e2-bba4-5d1d5f8f5545)

![ProfilePage](https://github.com/olszewskikacper/CoinGecko-Scraper/assets/128138029/c7efaa6f-87cf-4d2f-b182-2c977f148c79)


## Installation

Follow these steps to set up the project locally:

1. **Clone the repository**
    ```
    git clone https://github.com/your-username/CoinGecko-Scraper.git
    cd web-scraping-app
    ```
2. **Add C:\Users\<your_username>\.pyenv to the PATH variable**

3. **Install Python**
    ```
    pyenv install 3.12.1
    ```

4. **Install Poetry**
    ```
    pip install poetry
    ```

5. **Set up MySQL**
    - Install MySQL from [the official website](https://dev.mysql.com/downloads/).
    - Create a database for the application.
    - Update the database configuration in `app.py` and `main.py`.

6. **Set up the virtual environment **
    Open the project folder:
    Run this command in the project folder:
    ```
    poetry init   
    ```
    Then run this comamnd in the terminal:
    ```
    Poetry config virtualenvs.in-project true
    ```

7. **Install poetry dependencies**
    Run this command in the project folder:
    ```
    poetry install
    ```
    After that run this command in the terminal:
    ```
    poetry shell
    ```

9. **Installing playwright**
    In the poetry shell terminal run:
    ```sh
    playwright install
    ```
    Then:
    ```sh
   playwright install-deps
    ```
## Usage

Once the application is running, you can access the frontend at `http://127.0.0.1:5000`. 

## Testing

