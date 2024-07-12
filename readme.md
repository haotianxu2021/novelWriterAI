## Install Guide

You need to install Python before installing this application.

Open your terminal or cmd, open a location where you want to install this application, then type the following command:

'''
git clone https://github.com/haotianxu2021/novelWriterAI.git

cd novelWriterAI

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
'''

## Usage

1. Install the app
2. Run the server
3. Create an account
4. Login
5. Add your own api keys for corresponding language models
6. You can begin to generate your novels.
7. The first request in a new project will generate an outline. You can ask the model to revise the outline. But remember to save the outline after it is done. Only the saved outline will be used in the prompt for the future generation.
8. If you need to update the outline, you can still ask the model to revise it. Just put the most updated outline in the response and save it. The prompt will use the most updated one.
9. After the outline is done, you can generate and revise your chapters. Remember to save the chapter so that the next generation has access to it. The prompt will use the summaries of the last five chapters.
