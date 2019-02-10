
def layout1(game, constructor):
    pass


def layout2(game, constructor):

    xstart = int(game.background.xslices/4)
    xend = int(game.background.xslices*3/4)

    ystart = int(game.background.yslices / 4)
    yend = int(game.background.yslices * 3 / 4)

    for i in range(xstart, xend):
        game.background.set_build(i, ystart, constructor)
        game.background.set_build(i, yend, constructor)


def layout3(game, constructor):

    xstart = int(game.background.xslices / 4)
    xend = int(game.background.xslices * 3 / 4)

    ystart = int(game.background.yslices / 4)
    yend = int(game.background.yslices * 3 / 4)

    for i in range(ystart, yend):
        game.background.set_build(xstart, i, constructor)
        game.background.set_build(xend, i, constructor)


layouts = [
    layout1,
    layout2,
    layout3,
]