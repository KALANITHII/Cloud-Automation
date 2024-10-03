from IPython.display import Image


def draw_graph(app):
    image = Image(app.get_graph().draw_mermaid_png())

    with open("graph.png", "wb") as f:
        f.write(image.data)
