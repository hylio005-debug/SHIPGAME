import pyglet

window = pyglet.window.Window(800, 600, "Тест")

@window.event
def on_draw():
    window.clear()
    label = pyglet.text.Label("Hello, World!",
                              font_name='Arial',
                              font_size=36,
                              x=window.width//2, y=window.height//2,
                              anchor_x='center', anchor_y='center')
    label.draw()
    print("Отрисовано")  # отладка

pyglet.app.run()