import os
from qgis.core import QgsPrintLayout, QgsProject, QgsPageSizeRegistry, QgsLayoutItemPage
from qgis.core import QgsLayoutItemMap, QgsRectangle, QgsLayoutItemHtml, QgsLayoutMeasurement
from qgis.core import QgsLayoutFrame, QgsUnitTypes, QgsLayoutPoint, QgsLayoutItemPicture
from qgis.core import QgsLayoutSize, QgsLayoutItemLabel
from qgis.PyQt.QtCore import QSize, QRectF
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface
import math
from ...tools import config
from ... import util
from .tools import GeoOperations as geop

A4_PAGE_HEIGHT = 3700

class LayoutManager:

    def __init__(self, canvas, project, bindingPoint, uid=None, scale=None):
        self.project = project
        self.canvas = canvas
        self.bindingPoint = geop.convertToWgs(bindingPoint)
        if not uid:
            self.uid = self.getUid()
        else:
            self.uid = uid
        if not scale:
            self.scale = self.canvas.scale()
        else:
            self.scale = scale
        self.feature = self.getFeatureByUid()

    def getUid(self):
        try:
            layer = QgsProject.instance().mapLayersByName(
                "Лесосека временный слой")[0]
            features = []
            for feature in layer.getFeatures():
                features.append(feature)
            return features[0]['uid']
        except Exception as e:
            QMessageBox.information(None, "Ошибка модуля QGis", str(e))

    def getFeatureByUid(self):
        try:
            layer = QgsProject.instance().mapLayersByName("Лесосеки")[0]
            for feature in layer.getFeatures():
                if feature['uid'] == self.uid:
                    return feature
        except:
            QMessageBox.information(
                None, "Ошибка модуля QGis", "Лесосека с таким идентификатором не найдена " + str(self.uid))

    def removeLayoutIfExists(self, manager):
        layouts_list = manager.printLayouts()
        for ltdel in layouts_list:
            if ltdel.name() == 'PrintLayout':
                manager.removeLayout(ltdel)

    def prepareLayout(self, pageCount):
        layout = QgsPrintLayout(self.project)
        layout.initializeDefaults()
        layout.setName("PrintLayout")

        manager = self.project.layoutManager()
        self.removeLayoutIfExists(manager)
        manager.addLayout(layout)
        
        pc = layout.pageCollection()
        pc.pages()[0].setPageSize('A4', QgsLayoutItemPage.Portrait)

        if pageCount > 1:
            for x in range(1, pageCount):
                page = QgsLayoutItemPage(layout)
                page.setPageSize('A4', QgsLayoutItemPage.Portrait)
                layout.pageCollection().addPage(page)

        layout = manager.layoutByName('PrintLayout')

        return layout

    def getBaseLayers(self):
        layerNamesToShow = ["Кварталы", "Лесосека временный слой",
        "Привязка временный слой", "Пикеты", "Точка привязки", "Привязка", "Лесосека", "Выдела"]
        layers = []
        for name in layerNamesToShow:
            layer = QgsProject.instance().mapLayersByName(name)
            if layer:
                layers.append(layer[0])
        return layers

    def prepareMap(self, layout):
        mapItem = QgsLayoutItemMap(layout)
        mapItem.attemptSetSceneRect(QRectF(55, 70, 100, 100))
        # setup an initial extent to view in the map
        rectangle = self.canvas.extent()
        mapItem.setExtent(rectangle)
        mapItem.setScale(self.scale)
        mapItem.setLayers(self.getBaseLayers())
        layout.addLayoutItem(mapItem)
        return mapItem

    def generateTableHTML(self, rows):
        
        def parseHeader():
            th = ''
            for key in rows[0]:
                if key == 'GPS':
                    continue
                th += '<th>' + key + '</th>'
            return '<tr>' + th + '</tr>'
        
        def parseValues():
            values = ''
            for row in rows[1:]:
                tr = ''
                td = ''
                for data in row:
                    td += '<td>' + data + '</td>'
                tr = '<tr>' + td + '</tr>'
                values += tr
            return values

        htmlHeader = parseHeader()
        htmlValues = parseValues()
        
        return '<center><table>' + htmlHeader + htmlValues + '</table></center>'

    def prepareTableCss(self):
        return 'table {\
            font-size: 14px;\
            font-family: Times New Roman, Helvetica, sans-serif;\
            border-collapse: collapse;\
            }' + \
            'th { \
            text-align: center;\
            border: 1px solid black;\
            white-space: nowrap;\
            }' + \
            'td { \
            border: 1px solid black;\
            white-space: nowrap;\
            text-align: center;\
            }'  

    def composeHtmlLayout(self, layout, tableRows, topPosition):                   
        rows = len(tableRows)
        layout_html = QgsLayoutItemHtml(layout)
        html_frame = QgsLayoutFrame(layout, layout_html)
        html_frame.attemptSetSceneRect(QRectF(0, 0, 170, 5 + (rows + 1) * 5))
        html_frame.setFrameEnabled(True)
        layout_html.addFrame(html_frame)
        layout_html.setContentMode(QgsLayoutItemHtml.ManualHtml)
        layout_html.setHtml(self.generateTableHTML(tableRows))
        layout_html.loadHtml()
        layout_html.setUserStylesheet(self.prepareTableCss())
        layout_html.setUserStylesheetEnabled(True)
        html_frame.setFrameStrokeWidth(QgsLayoutMeasurement(0.01, QgsUnitTypes.LayoutPixels))
        html_frame.attemptMove(QgsLayoutPoint(200, topPosition, QgsUnitTypes.LayoutPixels))
        return layout_html

    def prepareHeader(self, layout):

        def getHeaderHtml():
            return '<center><b>КАРТА-СХЕМА <br>' \
            'с обозначенными границами участка лесного фонда, предоставляемого для лесопользования</b></center>'

        layout_html = QgsLayoutItemHtml(layout)
        html_frame = QgsLayoutFrame(layout, layout_html)
        html_frame.attemptSetSceneRect(QRectF(0, 0, 120, 20))
        html_frame.setFrameEnabled(True)
        layout_html.addFrame(html_frame)
        layout_html.setContentMode(QgsLayoutItemHtml.ManualHtml)
        layout_html.setHtml(getHeaderHtml())
        layout_html.loadHtml()
        # layout_html.setUserStylesheet(self.prepareTableCss())
        # layout_html.setUserStylesheetEnabled(True)
        html_frame.setFrameStrokeWidth(QgsLayoutMeasurement(0.01, QgsUnitTypes.LayoutPixels))
        html_frame.attemptMove(QgsLayoutPoint(600, 100, QgsUnitTypes.LayoutPixels))
        return layout_html

    def getLhType(self):
        cf = config.Configurer('enterprise')
        settings = cf.readConfigs()
        return settings.get('type')

    def getLocation(self):
        cf = config.Configurer('enterprise')
        settings = cf.readConfigs()
        return settings.get('location')

    def prepareDescription(self, layout):

        def getDescriptionHTML(attr, location, lhType):
            htmlStringLocation =  '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Месторасположение лесосеки: {} <br>'.format(location)
            htmlStringName = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Юридическое лицо, ведущее лесное хозяйство: {} "{}"<br>'.format((lhType), str(attr["leshos_text"]))
            
            htmlStringDescr = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Структурное подразделение юридического лица, ведущего лесное хозяйство: {} л-во' \
            ', лесной квартал №{}, таксационный выдел №{}, площадь лесосеки {} га.'.format(str(attr["lesnich_text"]),str(
                attr["num_kv"]), str(attr["num_vds"]), str(attr["area"]))
            return htmlStringLocation + htmlStringName + htmlStringDescr
        
        def setScaleLabel():           
            mainlabel = QgsLayoutItemLabel(layout)
            mainlabel.setText('Масштаб: 1:{}'.format(round(self.scale)))
            mainlabel.setFont(QFont('Times New Roman', 11))
            layout.addLayoutItem(mainlabel)
            mainlabel.adjustSizeToText()
            mainlabel.attemptMove(QgsLayoutPoint(1100, 750, QgsUnitTypes.LayoutPixels))

        layout_html = QgsLayoutItemHtml(layout)
        html_frame = QgsLayoutFrame(layout, layout_html)
        html_frame.attemptSetSceneRect(QRectF(0, 0, 175, 35))
        html_frame.setFrameEnabled(True)
        layout_html.addFrame(html_frame)
        layout_html.setContentMode(QgsLayoutItemHtml.ManualHtml)
        attr = self.getAreaAttributes()
        location = self.getLocation()
        lhType = self.getLhType()
        layout_html.setHtml(getDescriptionHTML(attr, location, lhType))
        layout_html.loadHtml()
        # layout_html.setUserStylesheet(self.prepareTableCss())
        layout_html.setUserStylesheetEnabled(True)        
        html_frame.setFrameStrokeWidth(QgsLayoutMeasurement(0.01, QgsUnitTypes.LayoutPixels))
        html_frame.attemptMove(QgsLayoutPoint(200, 340, QgsUnitTypes.LayoutPixels))
        setScaleLabel()
        return html_frame

    def getAreaAttributes(self):
        try:
            attrDict = {}
            attrDict["num_kv"] = self.feature["num_kv"]
            attrDict["num_vds"] = self.feature["num_vds"]
            attrDict["area"] = self.feature["area"]
            attrDict["num"] = self.feature["num"]
            attrDict["useType"] = self.feature["usetype"]
            attrDict["cuttingType"] = self.feature["cuttingtyp"]
            attrDict["fio"] = self.feature["fio"]
            attrDict["date"] = self.feature["date"]
            attrDict["info"] = self.feature["info"]
            attrDict["leshos_text"] = self.feature["leshos_text"]
            attrDict["lesnich_text"] = self.feature["lesnich_text"]

            return attrDict
        except Exception as e:
            QMessageBox.information(
                None, "Ошибка модуля QGis", "Сначала сохраните лесосеку " + str(e))

    def prepareLegend(self, layout):
        mainlabel = QgsLayoutItemLabel(layout)
        mainlabel.setText("Условные обозначения:")
        mainlabel.setFont(QFont('Times New Roman', 11))
        layout.addLayoutItem(mainlabel)
        mainlabel.adjustSizeToText()
        mainlabel.attemptMove(QgsLayoutPoint(200, 1970, QgsUnitTypes.LayoutPixels))

        labels = ['Точка привязки', 'Узел хода', 'Линия привязки', 'Лесосека']
        i = 0
        for labelText in labels:
            label = QgsLayoutItemLabel(layout)
            label.setText(labelText)
            label.setFont(QFont('Times New Roman', 11))
            layout.addLayoutItem(label)
            label.adjustSizeToText()
            label.attemptMove(QgsLayoutPoint(200 + (500 * i) + 120, 2050, QgsUnitTypes.LayoutPixels))
            i+= 1

    def prepareLegendImages(self, layout):
        images = [util.resolvePath("res\\binding_point.png"),
        util.resolvePath("res\\anchor_point.png"),
        util.resolvePath("res\\anchor_line.png"),
        util.resolvePath("res\\area.png")]
        i = 0
        for img in images:
            layoutItemPicture = QgsLayoutItemPicture(layout)
            layoutItemPicture.setPicturePath(img)
            layoutItemPicture.attemptResize(QgsLayoutSize(120, 100, QgsUnitTypes.LayoutPixels))
            layout.addLayoutItem(layoutItemPicture)
            layoutItemPicture.attemptMove(QgsLayoutPoint(200 + (500 * i), 2010, QgsUnitTypes.LayoutPixels))
            i += 1
        return images
    
    def getRowsChunked(self, tableRows):
        for i in range(0, len(tableRows), 45):
            yield tableRows[i:i + 45]
            
    def prepareTable(self, layoutPageCount, layout, tableRows):
        if layoutPageCount == 1:
            tableHtmlLayout = self.composeHtmlLayout(layout, tableRows, 2200)
        else:
            tableHtmlLayout = self.composeHtmlLayout(layout, tableRows[0:15], 2200)
            tableChunks = self.getRowsChunked(tableRows[15:])
            i = 1
            for chnk in tableChunks:
                chnk.insert(0, tableRows[0])
                topPosition = i * A4_PAGE_HEIGHT + 125
                tableHtmlLayout = self.composeHtmlLayout(layout, chnk, topPosition)
                i += 1

    def countPages(self, tableRows):
        if (len(tableRows) - 1) < 15:
            return 1
        else:
            return 1 + math.ceil((len(tableRows[15:]) - 1) / 45)

    def prepareFio(self, pages, layout):
        if pages == 1:
            heightPosition = 3200
        else:
            heightPosition = (pages - 1) * 3700 + 3100

        fioLabel = QgsLayoutItemLabel(layout)
        fioLabel.setText("Исполнитель: {}".format(str(self.feature["fio"])))
        fioLabel.setFont(QFont('Times New Roman', 11))
        layout.addLayoutItem(fioLabel)
        fioLabel.adjustSizeToText()
        fioLabel.attemptMove(QgsLayoutPoint(200, heightPosition, QgsUnitTypes.LayoutPixels))

    def checkIfCoordRow(self, tableRows):
        for row in tableRows[0]:
            if 'Y, °' in row:
                return True
        return False

    def getFirstPointOfArea(self, tableRows):
        for x, r in enumerate(tableRows):
            if x == 1 and r[-1] == 'Лесосека':
                return x - 1
            elif x > 1 and tableRows[x-2][-1] == 'Привязка' and r[-1] == 'Лесосека':
                return x - 1

    def cutSecondPointNumber(self, tableRows):
        if self.coordTable:
            for row in tableRows[1:]:
                row[0] = row[0].split('-')[1]
        tableRows[-1][0] = str(len(tableRows ) - 1) + '(' +str(self.getFirstPointOfArea(tableRows)) + ')'
        return tableRows

    def addBindingPointToTableRows(self, tableRows):
        if len(tableRows[0]) == 5:
            tableRows.insert(1, ['0', str(self.bindingPoint.y()), str(self.bindingPoint.x()), ''])
        elif len(tableRows[0]) == 8:
            x = geop.convertToDMS(self.bindingPoint.x())
            y = geop.convertToDMS(self.bindingPoint.y())
            tableRows.insert(1, ['0', str(y[0]), str(y[1]), str(y[2]), str(x[0]), str(x[1]), str(x[2]), ''])

    def generate(self, tableRows):
        self.coordTable = self.checkIfCoordRow(tableRows)
        if self.coordTable:
           self.cutSecondPointNumber(tableRows)
           self.addBindingPointToTableRows(tableRows)
        pages = self.countPages(tableRows)
        layout = self.prepareLayout(pages)
        header = self.prepareHeader(layout)
        description = self.prepareDescription(layout)
        self.prepareLegend(layout)
        legendImages = self.prepareLegendImages(layout)
        mapItem = self.prepareMap(layout)
        self.prepareTable(pages, layout, tableRows)
        self.prepareFio(pages, layout)
        iface.openLayoutDesigner(layout)