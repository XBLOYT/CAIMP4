#!/usr/bin/python

from collections import namedtuple
import time
import sys

class Edge:
    def __init__(self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

class Airport:
    def __init__(self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0
        self.pageIndex = 0

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = []  # list of Edge
edgeHash = dict()  # hash of edge to ease the match
airportList = []  # list of Airport
airportHash = dict()  # hash key IATA code -> Airport

noconectats = 0

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r")
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp) < 5 or len(temp[4]) != 5:
                raise Exception('not an IATA code')
            a.name = temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code = temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print(f"Reading Routes file from {fd}")
    routesTxt = open(fd, "r")
    cont = 0
    for line in routesTxt.readlines():
        e = Edge()
        try:
            temp = line.split(',')
            if len(temp) < 5 or len(temp[2]) != 3 or len(temp[4]) != 3:
                raise Exception('not an IATA code')
            elif temp[2] not in airportHash or temp[4] not in airportHash:
                raise Exception('airport dont exists')
            e.origin = temp[2]
            e.weight = 1
        except Exception as inst:
            pass
        else:
            if temp[2] in airportHash[temp[4]].routeHash:
                airportHash[temp[2]].outweight += 1
                airportHash[temp[4]].routeHash[temp[2]] += 1
            else:
                cont += 1
                airportHash[temp[4]].routes.append(e)
                airportHash[temp[2]].outweight += 1
                airportHash[temp[4]].routeHash[temp[2]] = 1

    routesTxt.close()
    print(f"There were {cont} routes")

def sumaPesos(P, i):
    suma = 0

    for key, j in airportHash[i].routeHash.items():
        suma += P[key] * j / airportHash[key].outweight

    return suma

def ordenacio(val):
    return val.pageIndex

def computePageRanks():
    n = len(airportList)
    P = {key: 1 / n for key in airportHash.keys()}
    auxnoconectats = 1 / n
    L = 0.85
    stop = False
    it = 0

    while not stop:
        Q = {key: 0 for key in airportHash.keys()}
        for key in airportHash.keys():
            Q[key] = L * sumaPesos(P, key) + (1-L)/n + auxnoconectats * L/n * noconectats

        auxnoconectats = (1-L)/n + auxnoconectats * L/n * noconectats

        # Normalizar para asegurar que la suma sea 1
        total = sum(Q.values())
        Q = {k: v / total for k, v in Q.items()}

        stop = all(abs(a - b) < 1e-16 for a, b in zip(P.values(), Q.values()))
        P = Q
        it += 1

    for j in range(n):
        airportList[j].pageIndex = P[airportList[j].code]

    airportList.sort(reverse=True, key=ordenacio)
    return it

def outputPageRanks():
    n = len(airportList)
    res = 0
    for i in range(n):
        a = airportList[i]
        print(f"NOM: {a.name} CODI: {a.code} PES: {a.pageIndex}")
        res += a.pageIndex
    print(res)

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    global noconectats
    noconectats = len([n for n in airportList if n.outweight == 0])
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2 - time1)

if __name__ == "__main__":
    sys.exit(main())