from . import PostgisDB
from qgis.PyQt.QtWidgets import QMessageBox
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
        try:
            self._number = self.setNumberFromDB()[0]
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
            postgis = PostgisDB.PostGisDB()
            results = postgis.getQueryResult("""select col2 from reference."15500009" where col1 like '%{}'""".format(self._number))
            return results[0]
        except Exception as e:
            QMessageBox.information(None, 'Ошибка', str(e))

        #нужна проверка на не пустой список


    def setNumberFromDB(self):
        try:
            postgis = PostgisDB.PostGisDB()
            results = postgis.getQueryResult("""select distinct leshos from forestbase.mainbase""")
            return results[0]
        except Exception as e:
            QMessageBox.information(None, 'Ошибка', str(e))
        #нужна проверка на не пустой список


    def getAllForestries(self):
        lesnichList = []
        postgis = PostgisDB.PostGisDB()
        rows = postgis.getQueryResult("""select distinct lesnich FROM forestbase.mainbase order by lesnich""")
        postgis.__del__()
        for row in rows:
            if row[0] < 10:
                query2 = """select col2 from reference."13000002" where col1 like '%{}'""".format(str(self.number) + '0' + str(row[0]))
            else:
                query2 = """select col2 from reference."13000002" where col1 like '%{}'""".format(str(self.number) + str(row[0]))
            postgis = PostgisDB.PostGisDB()
            row2 = postgis.getQueryResult(query2)[0]
            try:
                # ISSUE НЕСООТВЕТСТВИЕ КОЛИЧЕСТВА ЛЕСНИЧЕСТВ В БАЗЕ FORESTBASE И СПРАВОЧНИКЕ
                rr = row2[0]
                lesnichList.append(rr + ' ' + str(row[0]))
            except:
                pass
        return lesnichList

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

    def getAllForestries(self):
        lesnichList = []
        postgis = PostgisDB.PostGisDB()
        rows = postgis.getQueryResult("""select distinct lesnich FROM forestbase.mainbase order by lesnich""")
        postgis.__del__()
        for row in rows:
            if row[0] < 10:
                query2 = """select col2 from reference."13000002" where col1 like '%{}'""".format(str(self.leshoz_Number) + '0' + str(row[0]))
            else:
                query2 = """select col2 from reference."13000002" where col1 like '%{}'""".format(str(self.leshoz_Number) + str(row[0]))
            try:
                postgis = PostgisDB.PostGisDB()
                row2 = postgis.getQueryResult(query2)[0]
            except Exception as e:
                QMessageBox.information(None, 'Ошибка', str(e))
                return lesnichList
            try:
                # ISSUE НЕСООТВЕТСТВИЕ КОЛИЧЕСТВА ЛЕСНИЧЕСТВ В БАЗЕ FORESTBASE И СПРАВОЧНИКЕ
                rr = row2[0]
                lesnichList.append(rr + ' ' + str(row[0]))
            except:
                pass
        return lesnichList

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
        kv_list = []
        query_kvartal = """select num_kv from public."Кварталы" where num_lch = '{}' order by num_kv asc""".format(num_lch)
        try:
            postgis = PostgisDB.PostGisDB()
            rows = postgis.getQueryResult(query_kvartal)
            for row in rows:
                kv_list.append(str(row[0]))
            return kv_list
        except Exception as e:
            QMessageBox.information(None, 'Ошибка', str(e))
            return kv_list

class Stratum():

    def __init__(self):
        self._number = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    def getAllStratums(self, forestry, quarter):
        vd_list = []
        num_lch = forestry
        self.curKv = quarter
        query_vydel = """select num_vd from public."Выдела" where num_lch = '{}' and num_kv = '{}' order by num_vd""".format(num_lch, self.curKv)
        try:
            postgis = PostgisDB.PostGisDB()
            rows = postgis.getQueryResult(query_vydel)
            for row in rows:
                vd_list.append(str(row[0]))
            return vd_list
        except Exception as e:
            QMessageBox.information(None, 'Ошибка', str(e))
            return vd_list
