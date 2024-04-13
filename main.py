import os
import sys
import json
from typing import Any, Dict
import dill
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pprint import pprint

questionsToAsk : list = []
questionToAnswerMap : Dict[str, str] = {}
additionalQuestions : list = []


def main ():

    if len(sys.argv) < 2:
        print("Provide a question")
        quit()

    questionToAsk : str = sys.argv[1]

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    questionsToAsk.append(questionToAsk)

    counter: int = 3
    while counter >= 0 :
        callOpenAiForAllQuestions(client)
        counter = counter - 1

    writeOutputFile()
    

def callOpenAiForAllQuestions(client: OpenAI) :
    additionalQuestions : list = []
    for question in questionsToAsk:
        openAiResponse = callOpenAi(client, question)
        # openAiResponse = loadStoredResponse("chat_completion.pickle")
        questionToAnswerMap[question] = openAiResponse['answer']
        questionsToAsk.remove(question)
        processOpenAiResponse(openAiResponse, additionalQuestions)
    
    copyListAtoB(additionalQuestions, questionsToAsk)
    

def processOpenAiResponse(openAiMessage, additionalQuestions: list) :
    for question in openAiMessage['follow_up_questions']:
        additionalQuestions.append(question)


def callOpenAi(client: OpenAI, question :str) -> Any :
    chat_completion : ChatCompletion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a philosopher that contemplates on questions by answering the question asked and asking additional questions about the initial question, you respond with a JSON object containing your answer to the question and a string array of follow up questions."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
    )

    return json.loads(chat_completion.choices[0].message.content)

def loadStoredResponse(fileName: str) -> Any : 
    chatCompletionObj: ChatCompletion = dill.load(open(fileName, "rb"))

    return json.loads(chatCompletionObj.choices[0].message.content)

def copyListAtoB(fromList: list, toList: list):
    for item in fromList:
        toList.append(item)

def writeOutputFile(): 
    f = open("aismart.md", "w")
    f.write("Look at this amazing content written by AI.")
    f.write("\n\n")
    for item in questionToAnswerMap:
        f.write("# " + item)
        f.write("\n")
        f.write(questionToAnswerMap[item])
        f.write("\n")
        f.write("\n")
    
    f.close()

main()


