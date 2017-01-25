'''
Created on May 9, 2016

@author: matiasbarcenas
'''


import universal
from competitor import Competitor


class Manager(universal.Manager):
    '''
    classdocs
    '''
    def updateRanks(self):
        with self._managerEntitiesLock:
            entities = sorted(self._managerEntities.values(), \
                              key=lambda competitor: competitor.score, \
                              reverse = True)
            for ith in range(len(entities)):
                entities[ith].rank = ith
            

    def __init__(self, newEntityType=Competitor):
        '''
        Constructor
        '''
        universal.Manager.__init__(self, newEntityType)