# from aws_langchain.kendra import AmazonKendraRetriever #custom library
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain.chains.llm import LLMChain
import sys
import os
import boto3

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MAX_HISTORY_LENGTH = 5

BEDROCK_CLIENT = boto3.client("bedrock-runtime", 'us-east-1')

def build_chain(kendraIndexId):
  #region = os.environ["AWS_REGION"]
  #kendra_index_id = os.environ["KENDRA_INDEX_ID"]
  #credentials_profile_name = os.environ['AWS_PROFILE']
  region = 'us-east-1'
  kendra_index_id = kendraIndexId
  #print(credentials_profile_name)


  llm = Bedrock(
      region_name = region,
      model_kwargs={"max_tokens_to_sample":500,"temperature":1,"top_k":250,"top_p":0.999,"anthropic_version":"bedrock-2023-05-31"},
      model_id="anthropic.claude-v2",
      client = BEDROCK_CLIENT
  )
      
  retriever = AmazonKendraRetriever(index_id=kendra_index_id,top_k=5,region_name=region)


  prompt_template = """Human: This is a friendly conversation between a human and an AI. 
  The AI is talkative and provides specific details from its context but limits it to 500 tokens.
  If the AI does not know the answer to a question, it truthfully says it 
  does not know.

  Assistant: OK, got it, I'll be a talkative truthful AI assistant.

  Human: Here are a few documents in <documents> tags:
  <documents>
  {context}
  </documents>
  Based on the above documents, provide a detailed answer for, {question}.  You can provide other relevant details not based solely on the documents. 
  Answer "don't know" if not present in the document. 

  Assistant:
  """
  PROMPT = PromptTemplate(
      template=prompt_template, input_variables=["context", "question"]
  )

  condense_qa_template = """\n\nHuman: 
  Given the following conversation and a follow up question, rephrase the follow up question 
  to be a standalone question.
  \n\nAssistant: Go Ahead.
  Chat History:
  {chat_history}
  Follow Up Input: {question}
  Standalone question: 
  \n\nHuman:
  \n\nAssistant:"""
  standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)


  
  qa = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        condense_question_prompt=standalone_question_prompt, 
        return_source_documents=True, 
        combine_docs_chain_kwargs={"prompt":PROMPT},
        verbose=True)

  # qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, qa_prompt=PROMPT, return_source_documents=True)
  return qa


def run_chain(chain, prompt: str, history=[]):
  return chain({"question": prompt, "chat_history": history})


if __name__ == "__main__":
  chat_history = []
  qa = build_chain()
  print(bcolors.OKBLUE + "Hello! How can I help you?" + bcolors.ENDC)
  print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
  print(">", end=" ", flush=True)
  for query in sys.stdin:
    if (query.strip().lower().startswith("new search:")):
      query = query.strip().lower().replace("new search:","")
      chat_history = []
    elif (len(chat_history) == MAX_HISTORY_LENGTH):
      chat_history.pop(0)
    result = run_chain(qa, query, chat_history)
    chat_history.append((query, result["answer"]))
    print(bcolors.OKGREEN + result['answer'] + bcolors.ENDC)
    if 'source_documents' in result:
      print(bcolors.OKGREEN + 'Sources:')
      for d in result['source_documents']:
        print(d.metadata['source'])
    print(bcolors.ENDC)
    print(bcolors.OKCYAN + "Ask a question, start a New search: or CTRL-D to exit." + bcolors.ENDC)
    print(">", end=" ", flush=True)
  print(bcolors.OKBLUE + "Bye" + bcolors.ENDC)