import sys
import re
import math


def distance(x1, y1, x2, y2):
    res = math.fabs(x2 - x1) ** 2
    res = res + (math.fabs(y2 - y1) ** 2)
    res = math.sqrt(res)
    return int(math.ceil(res))


class Order:
    def __init__(self, index, x, y, number_of_products, productTypes):
        self.index = index
        self.x = x
        self.y = y
        self.number_of_products = number_of_products
        self.productTypes = productTypes
        if len(self.productTypes) != number_of_products:
            print "number of products in order does not match length of lis of product types"
            sys.exit()

    def isComplete(self):
        if self.productTypes == []:
            return True
        return False


class Warehouse:
    def __init__(self, index, x, y, products):
        self.index = index
        self.x = x
        self.y = y
        self.products = products

    def is_product_available(self, product, num=1):
        minimum = num
        if self.products[product.typ] >= minimum:
            return True
        return False


class Product:
    def __init__(self, typ, weight):
        self.typ = typ
        self.weight = weight


class Drone:
    def __init__(self, index, x, y, mpl,turns):
        self.index = index
        self.x = x
        self.y = y
        self.mpl = mpl
        self.carrying = []
        self.turns = turns

    def load(self, warehouse, product, number):
        self.turns += distance(self.x, self.y, warehouse.x, warehouse.y)
        self.x = warehouse.x
        self.y = warehouse.y
        if (warehouse.is_product_available(product, number) == False):
            print "drone %d is trying to load product %d which is unavailable in warehouse %d" % (self.index,
                                                                                                  product.typ,
                                                                                                  warehouse.index)
            return 0
        tweight = product.weight * number
        if self.mpl - tweight < 0:
            print "drone %d is trying to carry more weight than its max pay load" % self.index
            return 0
        for i in range(number):
            self.carrying.append(product)
            warehouse.products[product.typ] -= 1
            self.mpl -= product.weight

        self.turns += 1
        print "load successful"
        return self

    def deliver(self, order, product, number):
        self.turns += distance(self.x, self.y, order.x, order.y)
        self.x = order.x
        self.y = order.y
        if len(self.carrying) <= 0:
            # drone is carrying nothin
            print "drone %d is delivering nothing to order %d" % (self.index, order.index)
            return 0
        if (order.productTypes.count(product.typ) <= 0):
            # drone is delivering product that was not ordered
            print "drone %d is trying to deliver an unordered product to order %d" % (self.index, order.index)
            return 0
        if order.productTypes.count(product.typ) < number:
            # drone is delivering more products than ordered
            print "drone %d is delivering more than ordered to order %d" % (self.index, order.index)
            return 0
        if (self.carrying.count(product) < number):
            # drone is carrying less products than number it wants to deliver
            print "drone %d is trying to deliver more product of type %d than it is carrying" % (
                self.index, product.typ)
            return 0
        for i in range(number):
            self.carrying.remove(self.carrying[self.carrying.index(product)])
            self.mpl += product.weight
            order.productTypes.remove(order.productTypes[order.productTypes.index(product.typ)])
            order.number_of_products -= 1
        print "delivered"
        self.turns += 1
        return self

class Grid:
    def __init__(self, rows, cols, turns, drones, warehouses, orders, products):
        self.rows = rows
        self.cols = cols
        self.turns = float(turns)
        self.drones = drones
        self.warehouses = warehouses
        self.orders = orders
        self.products = products
        self.scores = []

    def getProduct(self, typ):
        for product in self.products:
            if product.typ == typ:
                return product
        return None

    def processCommand(self, command):
        mob = re.search(r'^(\d+)\s([LD])\s(\d+)\s(\d+)\s(\d+)$', command, re.M)
        if mob:
            din, com, wodin, pt, num = mob.groups()
            din = int(din)
            wodin = int(wodin)
            pt = int(pt)
            num = int(num)
            print din, com, wodin, pt, num
            if com == "L":
                # load from warehouse
                return self.drones[din].load(self.warehouses[wodin], self.getProduct(pt), num)
            if com == "D":
                # deliver to order
                return self.drones[din].deliver(self.orders[wodin], self.getProduct(pt), num)

        else:
            print "%s commmand is invalid" % command
            return 0

    def calculateScore(self):
        return int(sum(self.scores))

    def getNumberOfCompletedOrders(self):
        nocd = 0
        for order in self.orders:
            if order.isComplete():
                nocd += 1
        return nocd

    def simulate(self, solution):
        nocda = 0
        nocdb = 0
        sol = open(solution, "r")
        ncom = int(sol.readline().strip())
        for line in range(ncom):
            cline = sol.readline()
            cdrone = self.processCommand(cline)
            print "drone %d has used %d number of turns"%(cdrone.index,cdrone.turns)
            if (cdrone.turns > self.turns-1):
                print "number of turns exceeded"
                sys.exit()
            nocdb = self.getNumberOfCompletedOrders()
            if (nocdb - nocda) == 1:
                # new order has been completed
                z = ((self.turns - cdrone.turns) / self.turns) * 100
                self.scores.append(math.ceil(z))
                nocda = nocdb


def readFile(filename):
    products = []
    warehouses = []
    orders = []
    drones = []
    fi = open(filename, "r")
    r, c, d, t, p = [int(num) for num in fi.readline().split()]
    ptypes = int(fi.readline().strip())
    pweights = [int(num) for num in fi.readline().split()]
    for pt in range(ptypes):
        products.append(Product(pt, pweights[pt]))

    nowh = int(fi.readline().strip())
    for i in range(nowh):
        whx, why = [int(num) for num in fi.readline().split()]
        wprods = [int(num) for num in fi.readline().split()]
        warehouses.append(Warehouse(i, whx, why, wprods))

    nod = int(fi.readline().strip())
    for j in range(nod):
        odx, ody = [int(num) for num in fi.readline().split()]
        nops = int(fi.readline().strip())
        optypes = [int(num) for num in fi.readline().split()]
        orders.append(Order(j, odx, ody, nops, optypes))

    for dr in range(d):
        drones.append(Drone(dr, warehouses[0].x, warehouses[0].y, p,-1))

    return Grid(r, c, t, drones, warehouses, orders, products)


def main():
    grid = readFile(sys.argv[1]);
    grid.simulate(sys.argv[2])
    print(grid.calculateScore())


if __name__ == '__main__':
    main()
