from graph import graph


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


# config = {"configurable": {"thread_id": "1"}}
while True:
    query = input("query- ")
    inputs = {"messages": [("user", query)]}
    response = graph.invoke(inputs)
    print(response)
