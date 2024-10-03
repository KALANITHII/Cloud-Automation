import argparse

from pydantic import BaseModel

from main import graph


class Query(BaseModel):
    user_query: str
    email: str


def process_query(query: Query):
    try:
        response = graph.invoke(query.user_query, config={"configurable": {"thread_id": query.email}})[-1].content
        return {'response': response}
    except Exception as e:
        return {'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Process user query and return a response from the AWS Agent.')
    parser.add_argument('--user_query', type=str, required=True, help='User query to process')
    parser.add_argument('--email', type=str, required=True, help='Email to use as thread_id')

    args = parser.parse_args()

    query = Query(user_query=args.user_query, email=args.email)
    response = process_query(query)

    print(response)


if __name__ == "__main__":
    main()
