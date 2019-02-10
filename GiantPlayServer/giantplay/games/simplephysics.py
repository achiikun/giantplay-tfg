import pygame
from pygame.rect import Rect

from giantplay import cfg
from giantplay.utils import vectorutils


class CollisionCell:

    def __init__(self, panel, pos, size):
        self.panel = panel
        self.pos = pos
        self.size = size
        self.center = (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2)
        self.relation = self.size[0]/self.size[1]

    def get_bounce_direction(self, pos, dir):
        diff = (((pos[0]-self.center[0]) / self.relation), pos[1]-self.center[1])

        abs_diff = [abs(i) for i in diff]

        if abs_diff[0] == 0 and abs_diff[1] == 0:
            return dir

        if diff[1] < 0 and abs_diff[1] > abs_diff[0]:
            # up
            if dir[1] > 0:
                return dir[0], -dir[1]
            pass
        elif diff[1] > 0 and abs_diff[1] > abs_diff[0]:
            # down
            if dir[1] < 0:
                return dir[0], -dir[1]
            pass
        elif diff[0] > 0:
            #right
            if dir[0] < 0:
                return -dir[0], dir[1]
            pass
        else:
            #left
            if dir[0] > 0:
                return -dir[0], dir[1]
            pass

        return dir

    def on_render(self, g, rect):
        pass


class CollisionGrid:

    def __init__(self, slicesize=8):
        self.slizesize = slicesize
        self.xslices = int(cfg.SCREEN_WIDTH/slicesize)
        self.yslices = int(cfg.SCREEN_HEIGHT/slicesize)
        self.board = [[None for i in range(self.xslices)] for i in range(self.yslices)]

    def cell(self, x, y):
        if x < 0 or y < 0 or x >= self.xslices or y >= self.yslices:
            return None

        return self.board[y][x]

    def set(self, x, y, cell):
        if x < 0 or y < 0 or x >= self.xslices or y >= self.yslices:
            return None

        self.board[y][x] = cell

    def get_rect(self, pos, size):
        return Rect(cfg.SCREEN_WIDTH/self.xslices*pos[0],
                    cfg.SCREEN_HEIGHT / self.yslices*pos[1],
                    cfg.SCREEN_WIDTH/self.xslices*size[0],
                    cfg.SCREEN_HEIGHT/self.yslices*size[1])

    def set_build(self, x, y, constructor):
        self.board[y][x] = constructor(self, (x * self.slizesize, y * self.slizesize), (self.slizesize, self.slizesize))

    def fill_borders(self, constructor):

        for i in range(self.xslices):
            self.board[0][i] = constructor(self, (i*self.slizesize, 0), (self.slizesize, self.slizesize))
            self.board[-1][i] = constructor(self, (i*self.slizesize, (len(self.board)-1)*self.slizesize), (self.slizesize, self.slizesize))

        for i in range(self.yslices):
            self.board[i][0] = constructor(self, (0, i*self.slizesize), (self.slizesize, self.slizesize))
            self.board[i][-1] = constructor(self, ((len(self.board[i])-1)*self.slizesize, i*self.slizesize), (self.slizesize, self.slizesize))

    def get_cell_path(self, pos, next_pos):

        '''first = int(pos[0] / self.slizesize), int(pos[1] / self.slizesize)
        last = int(last_pos[0] / self.slizesize)+1, int(last_pos[1] / self.slizesize)+1

        path = []
        for val in vectorutils.raytrace(first, last)[:-1]:
            try:
                path.append(self.board[val[1]][val[0]])
            except IndexError:
                pass'''

        first = int(pos[0]), int(pos[1])
        last = int(next_pos[0]) + 1, int(next_pos[1]) + 1

        path = []
        aux = None
        for val in vectorutils.raytrace(first, last)[:-1]:
            try:
                val = int(val[0] / self.slizesize), int(val[1] / self.slizesize)
                cell = self.cell(val[0], val[1])
                if not aux or val != aux:
                    path.append(cell)
                    aux = val
            except IndexError:
                pass

        return path

    def get_bounce_direction(self, pos, direction):

        first = int(pos[0]), int(pos[1])
        last = int(pos[0] + direction[0]), int(pos[1] + direction[1])

        last_cellidx = None
        last_cell = None

        value = None, None

        for val in vectorutils.raytrace(first, last):
            try:
                cellidx = int(val[0] / self.slizesize), int(val[1] / self.slizesize)

                cell = self.cell(cellidx[0], cellidx[1])

                if last_cellidx is None and cell is not None:
                    # You are inside a block
                    return direction, cell
                elif last_cell is None and cell is not None:

                    if cellidx[0] > last_cellidx[0]:
                        # pa derecha
                        if cellidx[1] == last_cellidx[1]:
                            # derecha
                            value = 'left', cell
                            break
                        elif cellidx[1] > last_cellidx[1]:
                            # borde izquierdo-superior
                            cell2 = self.cell(cellidx[0]-1, cellidx[1])
                            cell3 = self.cell(cellidx[0], cellidx[1]-1)

                            if cell2 and not cell3:
                                value = 'up', cell
                                break
                            elif cell3 and not cell2:
                                value = 'left', cell
                                break
                            else:
                                value = 'corner', cell
                                break

                            break
                        else:
                            # borde izquierdo-inferior
                            cell2 = self.cell(cellidx[0] - 1, cellidx[1])
                            cell3 = self.cell(cellidx[0], cellidx[1] + 1)

                            if cell2 and not cell3:
                                value = 'down', cell
                                break
                            elif cell3 and not cell2:
                                value = 'left', cell
                                break
                            else:
                                value = 'corner', cell
                                break

                            break

                    elif cellidx[0] == last_cellidx[0]:
                        # vertical
                        if cellidx[1] == last_cellidx[1]:
                            # quieto
                            break
                        elif cellidx[1] > last_cellidx[1]:
                            # pa abajo
                            value = 'up', cell
                            break
                        else:
                            # pa arriba
                            value = 'down', cell
                            break
                    else:
                        # pa izquierda
                        if cellidx[1] == last_cellidx[1]:
                            # izquierda
                            value = 'right', cell
                            break
                        elif cellidx[1] > last_cellidx[1]:
                            # borde derecho-superior
                            cell2 = self.cell(cellidx[0] + 1, cellidx[1])
                            cell3 = self.cell(cellidx[0], cellidx[1] - 1)

                            if cell2 and not cell3:
                                value = 'up', cell
                                break
                            elif cell3 and not cell2:
                                value = 'right', cell
                                break
                            else:
                                value = 'corner', cell
                                break

                            break
                        else:
                            # borde derecho-inferior
                            cell2 = self.cell(cellidx[0] + 1, cellidx[1])
                            cell3 = self.cell(cellidx[0], cellidx[1] + 1)

                            if cell2 and not cell3:
                                value = 'down', cell
                                break
                            elif cell3 and not cell2:
                                value = 'right', cell
                                break
                            else:
                                value = 'corner', cell
                                break

                            break

                last_cellidx = cellidx
                last_cell = cell
            except IndexError:
                pass

        return value

    def get_colliding_cells(self, rect_or_pos):

        if isinstance(rect_or_pos, Rect):
            minx = max(0, int(rect_or_pos.left / self.slizesize))
            miny = max(0, int(rect_or_pos.top / self.slizesize))

            maxx = min(self.xslices, int(rect_or_pos.right / self.slizesize) + 1)
            maxy = min(self.yslices, int(rect_or_pos.bottom / self.slizesize) + 1)

            for row in self.board[miny:maxy]:
                for col in row[minx:maxx]:
                    yield col
        else:
            try:
                yield self.board[int(rect_or_pos[1] / self.slizesize)][int(rect_or_pos[0] / self.slizesize)]
            except IndexError:
                return []

    def on_render(self, g):

        rect = Rect(0, 0, cfg.SCREEN_WIDTH/self.xslices, cfg.SCREEN_HEIGHT/self.yslices)

        for ir, row in enumerate(self.board):
            rect.top = rect.height * ir
            for ic, cell in enumerate(row):
                if cell:
                    rect.left = rect.width * ic
                    cell.on_render(g, rect)