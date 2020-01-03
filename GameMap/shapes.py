class Rect:
    def __init__(self, x, y, w, h):
        self.type = 'Rect'
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        if (other.type == 'Rect'):
            return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                    self.y1 <= other.y2 and self.y2 >= other.y1)
        elif (other.type == 'Circle'):
            for coord in other.coords:
                for x in range (self.x1, self.x2):
                    for y in range (self.y1, self.y2):
                        if (x == coord[0] and y == coord[1]):
                            return True
                        elif (x == coord[0] + 1 and y == coord[1]):
                            return True
                        elif (x == coord[0] and y == coord[1] + 1):
                            return True
                        elif (x == coord[0] - 1 and y == coord[1]):
                            return True
                        elif (x == coord[0] and y == coord[1] - 1):
                            return True
            else:
                return False

class Circle:
    def __init__(self, x, y, r):
        self.type = 'Circle'
        self.center_x = x
        self.center_y = y
        self.r = r
        self.coords = self.fill()

    # Gets the coordinates for all points within the circle
    # It took way to long to get this algorithm working >_>
    def fill (self):
        coords = []
        for x in range(self.center_x, self.center_x + self.r):
            for y in range(self.center_y,  self.center_y + self.r):
                if self.in_circle(x, y):
                    change_x = (x - self.center_x)
                    change_y = (y - self.center_y)

                    coords.append( (x,y) )
                    coords.append( (self.center_x - change_x, y) )
                    coords.append( (x, self.center_y - change_y) )
                    coords.append( (self.center_x - change_x, self.center_y - change_y) )
                
        return coords

    def in_circle(self, x, y):
        square_dist = (self.center_x - x) ** 2 + (self.center_y - y) ** 2
        return square_dist <= self.r ** 2

    def center(self):
        return (self.center_x, self.center_y)

    def intersect(self, other):
        if (other.type == 'Rect'):
            for coord in self.coords:
                for x in range (other.x1, other.x2):
                    for y in range (other.y1, other.y2):
                        if (x == coord[0] and y == coord[1]):
                            return True
                        elif (x == coord[0] + 1 and y == coord[1]):
                            return True
                        elif (x == coord[0] and y == coord[1] + 1):
                            return True
                        elif (x == coord[0] - 1 and y == coord[1]):
                            return True
                        elif (x == coord[0] and y == coord[1] - 1):
                            return True
            else:
                return False
        elif (other.type == 'Circle'):
            for coord in self.coords:
                for other_coord in other.coords:
                    if coord == other_coord:
                        return True
            else:
                return False