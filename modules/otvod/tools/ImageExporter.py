import os
from qgis.core import QgsPrintLayout, QgsLayoutItemMap, QgsLayoutPoint, QgsUnitTypes, QgsLayoutSize, QgsLayoutExporter, QgsLayoutItemPage, QgsPageSizeRegistry
from qgis.PyQt.QtCore import QSize, QRectF
from qgis.core import QgsProject, QgsFeature, QgsMapSettings, QgsMapRendererSequentialJob, QgsCoordinateReferenceSystem, QgsLayoutItemPicture, QgsLayoutItemTextTable
from qgis.core import QgsLayoutTableColumn, QgsLayoutFrame, QgsLayoutItemLabel, QgsLayoutItemHtml, QgsLayoutMeasurement
from ....tools import config
from datetime import datetime
from qgis.PyQt.QtWidgets import QMessageBox

class ImageExporter:
    """Инициализируется при вызове инструмента "Сохранить как изображение"
    модуля отвода
    Сохраняется картинка и данные отвода
    Данные отвода для вывода формируются в html-разметку
    Если данных отвода в таблице нет - в картинке будет только карта-схема
    """
    def __init__(self, project, canvas):
        super().__init__()
        self.project = project
        self.canvas = canvas

    def getReportFolder(self):
        cf = config.Configurer('report')
        settings = cf.readConfigs()
        return settings.get('path')

    def getBaseLayers(self):
        layerNamesToShow = ["Выдела", "Кварталы", "Лесосека временный слой",
        "Привязка временный слой", "Пикеты", "Точка привязки", "Привязка", "Лесосека"]
        layers = []
        for name in layerNamesToShow:
            layer = QgsProject.instance().mapLayersByName(name)
            if layer:
                layers.append(layer[0])
        return layers

    def prepareImage(self):
        settings = QgsMapSettings()
        self.canvas.refresh()
        settings.setOutputSize(QSize(391, 361))
        settings.setExtent(self.canvas.extent())
        settings.setLayers(self.getBaseLayers())
        crs = QgsCoordinateReferenceSystem('EPSG:32635')
        settings.setDestinationCrs(crs)
        job = QgsMapRendererSequentialJob(settings)
        job.start()
        job.waitForFinished()
        img = job.renderedImage()
        imagePath = os.path.join(QgsProject.instance().homePath(), "output2.png")
        img.save(imagePath)
        return imagePath
    
    def composePicture(self, layout, imgPath):
        layoutItemPicture = QgsLayoutItemPicture(layout)    
        layoutItemPicture.setPicturePath(imgPath)
        layoutItemPicture.attemptResize(QgsLayoutSize(391, 361, QgsUnitTypes.LayoutPixels))
        layout.addLayoutItem(layoutItemPicture)

    def prepareLayout(self):
        layout = QgsPrintLayout(self.project)
        layout.initializeDefaults()
        layout.setName("MyLayout")

        manager = self.project.layoutManager()
        layouts_list = manager.printLayouts()
        for ltdel in layouts_list:
            if ltdel.name() == 'MyLayout':
                manager.removeLayout(ltdel)
        manager.addLayout(layout)
        
        layout = manager.layoutByName('MyLayout')
        return layout

    def generateHTML(self, rows):
        
        def parseHeader():
            tableHeaderDict = list(rows[1].values())[0]
            keys = list(tableHeaderDict.keys())
            th = ''
            for key in keys:
                th += '<th>' + key + '</th>'
            return '<tr>' + th + '</tr>'
        
        def parseValues():
            values = ''
            for row in rows[1:]:
                valuesDict = list(row.values())[0]
                tr = ''
                td = ''                
                for data in list(valuesDict.values()):
                    td += '<td>' + data + '</td>'
                tr = '<tr>' + td + '</tr>'
                values += tr
            return values

        htmlHeader = parseHeader()
        htmlValues = parseValues()

        return '<table>' + htmlHeader + htmlValues + '</table>'

    def prepareCss(self):
        return 'table {\
            font-size: 4px;\
            font-family: Arial, Helvetica, sans-serif;\
            }' + \
            'th { \
            text-align: center;\
            }' + \
            'td { \
            text-align: center;\
            white-space: nowrap;\
            }'

    def composeHtmlLayout(self, layout, tableRows):
        if len(tableRows) < 2:
            QMessageBox.information(None, 'Внимание', "Отсутствуют узлы лесосеки. Изображение будет сохранено без таблицы промеров")
            return
        rows = len(tableRows)
        layout_html = QgsLayoutItemHtml(layout)
        html_frame = QgsLayoutFrame(layout, layout_html)
        html_frame.attemptSetSceneRect(QRectF(0, 0, 30, 5 + rows * 2.3))
        html_frame.setFrameEnabled(True)
        layout_html.addFrame(html_frame)
        layout_html.setContentMode(QgsLayoutItemHtml.ManualHtml)
        layout_html.setHtml(self.generateHTML(tableRows))
        layout_html.loadHtml()
        layout_html.setUserStylesheet(self.prepareCss())
        layout_html.setUserStylesheetEnabled(True)        
        html_frame.setFrameStrokeWidth(QgsLayoutMeasurement(0.1, QgsUnitTypes.LayoutPixels))
        html_frame.attemptMove(QgsLayoutPoint(391, 0, QgsUnitTypes.LayoutPixels))

    def doJob(self, tableRows):
        imgPath = self.prepareImage()
        layout = self.prepareLayout()
        self.composePicture(layout, imgPath)
        self.composeHtmlLayout(layout, tableRows)

        pc = layout.pageCollection()
        pc.pages()[0].setPageSize('A4', QgsLayoutItemPage.Landscape)

        currentDateTime = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')

        base_path = os.path.join(self.getReportFolder())
        img_path = os.path.join(base_path, currentDateTime + ".png")
               
        exporter = QgsLayoutExporter(layout)

        imageSettings = exporter.ImageExportSettings()
        imageSettings.dpi = 300
        imageSettings.cropToContents = True

        exporter.exportToImage(img_path, settings=imageSettings)
        return img_path
