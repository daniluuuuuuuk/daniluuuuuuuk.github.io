from . import PostgisDB
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsFeatureRequest

import re

class ForestObject:
    def __init__(self):
        # self._forestEnterprise = None
        self._forestry= None
        self._quartal = None
        self._stratum = None
        self._forestEnterprise = ForestEnterprise()
        self._mObservers = []

    @property
    def forestEnterprise(self):
        return self._forestEnterprise

    @property
    def forestry(self):
        return self._forestry

    @property
    def quartal(self):
        return self._quartal

    @property
    def stratum(self):
        return self._stratum

    @forestEnterprise.setter
    def forestEnterprise(self, forestEnterprise):
        self._forestEnterprise = forestEnterprise
        self.notifyObservers()
    
    @forestry.setter
    def forestry(self, forestry):
        self._forestry = forestry
        self.notifyObservers()

    @quartal.setter
    def quartal(self, quartal):
        self._quartal = quartal
        self.notifyObservers()
    
    @stratum.setter
    def stratum(self, stratum):
        self._stratum = stratum
        self.notifyObservers()

    def addObserver( self, inObserver ):
        self._mObservers.append(inObserver)

    def removeObserver( self, inObserver ):
        self._mObservers.remove(inObserver)

    def notifyObservers( self ):
        for x in self._mObservers:
            x.forestObjectChanged()

class ForestEnterprise:
    
    def __init__(self):
        layer = QgsProject.instance().mapLayersByName("Выдела")[0]
        idx = layer.fields().indexOf('num_lhz')
        num_lhz = list(layer.uniqueValues(idx))[0]
        print(num_lhz)
        try:
            self._number = num_lhz
            self._name = self.setNameFromDB()[0]
        except:
            self._number = -1
            self._name = ""

    @property
    def number(self):
        return self._number

    @property
    def name(self):
        return self._name

    @number.setter
    def number(self, number):
        self._number = number
    
    @name.setter
    def name(self, name):
        self._name = name

    def setNameFromDB(self):
        try:
            postgisConnection = PostgisDB.PostGisDB()
            result = postgisConnection.getQueryResult(
                """select name_organization 
                from "dictionary".organization
                where substring(code_organization::varchar(255) from 6 for 3) = '{}'""".format(self._number))[0]
            postgisConnection.__del__()
            return result
        except Exception as e:
            QMessageBox.information(None, 'Ошибка', str(e))

class Forestry(ForestObject):

    def __init__(self, lhnumber):
        self._number = None
        self.leshoz_Number = lhnumber

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    def prepareForestries(self, result):
        forestries = []
        for fr in result:
            forestries.append(str(fr[0])[-2:] + ' ' + fr[1])
        return forestries


    def getAllForestries(self):
        lesnichList = []
        postgisConnection = PostgisDB.PostGisDB()
        leshozId = postgisConnection.getQueryResult(
            """select id_organization 
                from "dictionary".organization
                where substring(code_organization::varchar(255) from 6 for 3) = '{}'""".format(self.leshoz_Number))[0][0]
        result = postgisConnection.getQueryResult(
            """select code_organization, name_organization from "dictionary".organization where parent_id_organization = {}""".format(leshozId))
        lesnichestva = self.prepareForestries(result)
        postgisConnection.__del__()
        return lesnichestva

class Quarter():

    def __init__(self):
        self._number = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    def getAllQuarters(self, num_lch):
        layer = QgsProject.instance().mapLayersByName("Выдела")[0]
        expression = "\"num_lch\" = '{}'".format(num_lch)
        request = QgsFeatureRequest().setFilterExpression(expression)
        features = layer.getFeatures(request)
        num_kvs = (int(feature['num_kv']) for feature in features)
        num_kvs = set(sorted(num_kvs))
        return map(str, num_kvs)

class Stratum():

    def __init__(self):
        self._number = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    def getAllStratums(self, num_lch, num_kv):
        layer = QgsProject.instance().mapLayersByName("Выдела")[0]
        expression = "\"num_lch\" = '{}' and \"num_kv\" = '{}'".format(num_lch, num_kv)
        request = QgsFeatureRequest().setFilterExpression(expression)
        features = layer.getFeatures(request)
        num_vds = (int(feature['num_vd']) for feature in features)
        num_vds = set(sorted(num_vds))
        print(num_kv)
        return map(str, num_vds)
