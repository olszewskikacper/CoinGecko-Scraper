
Instalacja Pythona i Poetry
1. Zainstaluj pyenv:
  WYWOLAJ TA KOMENDE W POWERSHELL (CALA):
  Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
  Dodaj C:\Users\<nazwa_użytkownika>\.pyenv do zmiennej PATH

2. Zainstaluj Pythona 3.12.1:
   
  Uruchom "pyenv install 3.12.1" w PowerShellu

3. Zainstaluj Poetry:

  Upewnij się, że masz Pythona 3.6+
  Uruchom "pip install poetry" w VSC/PyCharmie
  
4. Ustaw in-project venv w Poetry:

  Otwórz folder projektu
  Uruchom "poetry init" w folderze projektu
  W pyproject.toml dodaj: tool.poetry.virtualenvs = in-project

5. Wykonaj poetry install:

  Uruchom poetry install w folderze projektu
