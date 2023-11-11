#!/usr/bin/python

from collections import namedtuple
import time
import sys

class Edge:
    def __init__ (self, origin=None, destination=None):
        self.origin = origin
        self.weight = 1
        self.destination = destination

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight, self.destination)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0
        self.position = -1
        self.pageIndex = 0
    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            a.position = cont-1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {0}".format(fd))
    routesTxt = open(fd, "r")
    cont = 0
    for line in routesTxt.readlines():
        e = Edge()
        try:
            temp = line.split(',')
            if len(temp[2]) != 3 or len(temp[4]) != 3:
                raise Exception('descartem aresta pq un aeroport no té codi IATA')
            elif not(temp[2] in airportHash) or not(temp[4] in airportHash):
                raise Exception('un dels dos aeroports no existeix!')
            e.origin = temp[2]
            e.destination = temp[4]
            nom = temp[2] + temp[4]
        except Exception as inst:
            pass
        else:
            if nom in edgeHash:
                edgeHash[nom].weight += 1
                airportHash[temp[4]].routeHash[temp[2]].weight += 1
            else:
                cont += 1
                edgeList.append(e)
                edgeHash[nom] = e
                airportHash[temp[4]].routeHash[temp[2]] = e
            airportHash[temp[2]].outweight += 1
    routesTxt.close()
    print(f"There were {cont} unique and correct Routes")


def sumaPesos(P, i):
    codia = airportList[i].code
    a = airportHash[codia]
    suma = 0
    for key, j in a.routeHash.items():
        nomorigen = j.origin
        origen = airportHash[nomorigen]
        k = origen.position
        suma += P[k] * j.weight/origen.outweight
    return suma

def ordenacio(val):
    return val.pageIndex

def computePageRanks():
    n = len(airportList)
    P = [1/n for i in range (n)]
    L = 0.85
    nits = 1000
    while(nits > 0):
        Q = [0 for i in range (n)]
        for i in range(n):
            Q[i] = L*sumaPesos(P, i)+(1-L)/n
        P = Q
        nits -= 1
    for j in range(n):
        airportList[j].pageIndex = P[j]
    airportList.sort(reverse=True, key=ordenacio)
    return 20

def outputPageRanks():
    n = len(airportList)
    res = 0
    for i in range(n):
        a = airportList[i]
        print("NOM: " + a.name + " CODI: " + a.code + " PES: " + str(a.pageIndex))
        res += a.pageIndex
    print(res)

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
