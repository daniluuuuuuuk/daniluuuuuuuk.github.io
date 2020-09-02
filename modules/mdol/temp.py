from decimal import Decimal
a = [
    {'name_species': 'ель', 'code_species': 27, 'code_species_proxying': 27, 'code_trf_height': 4, 'code_author': 21, 'wpulp_ind_large': Decimal('7.98'), 'wpulp_ind_medium': Decimal('59.95'), 'wpulp_ind_small': Decimal('40.99'), 'wpulp_ind': Decimal('108.92'), 'wpulp_fuel': Decimal('19.16'), 'wpulp_liquid': Decimal('128.08'), 'wpulp_crw_lq': Decimal('2.69'), 'wpulp_brushwood': Decimal('28.53'), 'wpulp_waste': Decimal('14.20'), 'wpulp_total': Decimal('128.08'), 'trf_vl_ind': Decimal('941.04'), 'trf_vl_fuel': Decimal('1.92'), 'trf_vl_liquid': Decimal('942.96'), 'trf_vl_crw_lq': Decimal('0.27'), 'trf_vl_brushwood': 0, 'trf_vl_waste': 0, 'trf_vl_total': Decimal('942.96')},
    {'name_species': 'ольха черная', 'code_species': 62, 'code_species_proxying': 62, 'code_trf_height': 4, 'code_author': 21, 'wpulp_ind_large': Decimal('0.57'), 'wpulp_ind_medium': Decimal('4.32'), 'wpulp_ind_small': Decimal('2.50'), 'wpulp_ind': Decimal('7.39'), 'wpulp_fuel': Decimal('1.49'), 'wpulp_liquid': Decimal('8.88'), 'wpulp_crw_lq': Decimal('0.03'), 'wpulp_brushwood': Decimal('0.13'), 'wpulp_waste': Decimal('1.09'), 'wpulp_total': Decimal('8.88'), 'trf_vl_ind': Decimal('26.70'), 'trf_vl_fuel': Decimal('0.16'), 'trf_vl_liquid': Decimal('26.86'), 'trf_vl_crw_lq': Decimal('0.00'), 'trf_vl_brushwood': 0, 'trf_vl_waste': 0, 'trf_vl_total': Decimal('26.86')},
    {'name_species': 'осина', 'code_species': 64, 'code_species_proxying': 64, 'code_trf_height': 4, 'code_author': 21, 'wpulp_ind_large': Decimal('0.39'), 'wpulp_ind_medium': Decimal('0.91'), 'wpulp_ind_small': Decimal('1.54'), 'wpulp_ind': Decimal('2.84'), 'wpulp_fuel': Decimal('2.15'), 'wpulp_liquid': Decimal('4.99'), 'wpulp_crw_lq': Decimal('0.22'), 'wpulp_brushwood': Decimal('0.16'), 'wpulp_waste': Decimal('0.36'), 'wpulp_total': Decimal('4.99'), 'trf_vl_ind': Decimal('1.93'), 'trf_vl_fuel': Decimal('0.09'), 'trf_vl_liquid': Decimal('2.02'), 'trf_vl_crw_lq': Decimal('0.01'), 'trf_vl_brushwood': 0, 'trf_vl_waste': 0, 'trf_vl_total': Decimal('2.02')},
    {'name_species': 'сосна', 'code_species': 71, 'code_species_proxying': 71, 'code_trf_height': 3, 'code_author': 21, 'wpulp_ind_large': Decimal('107.46'), 'wpulp_ind_medium': Decimal('133.17'), 'wpulp_ind_small': Decimal('20.90'), 'wpulp_ind': Decimal('261.53'), 'wpulp_fuel': Decimal('29.99'), 'wpulp_liquid': Decimal('291.52'), 'wpulp_crw_lq': Decimal('7.25'), 'wpulp_brushwood': Decimal('25.17'), 'wpulp_waste': Decimal('28.88'), 'wpulp_total': Decimal('291.52'), 'trf_vl_ind': Decimal('3840.56'), 'trf_vl_fuel': Decimal('3.30'), 'trf_vl_liquid': Decimal('3843.86'), 'trf_vl_crw_lq': Decimal('0.80'), 'trf_vl_brushwood': 0, 'trf_vl_waste': 0, 'trf_vl_total': Decimal('3843.86')},
    {'name_species': 'береза', 'code_species': 5, 'code_species_proxying': 5, 'code_trf_height': 4, 'code_author': 21, 'wpulp_ind_large': Decimal('5.18'), 'wpulp_ind_medium': Decimal('16.39'), 'wpulp_ind_small': Decimal('8.07'), 'wpulp_ind': Decimal('29.64'), 'wpulp_fuel': Decimal('7.63'), 'wpulp_liquid': Decimal('37.27'), 'wpulp_crw_lq': Decimal('2.75'), 'wpulp_brushwood': Decimal('6.74'), 'wpulp_waste': Decimal('8.12'), 'wpulp_total': Decimal('37.27'), 'trf_vl_ind': Decimal('117.90'), 'trf_vl_fuel': Decimal('1.30'), 'trf_vl_liquid': Decimal('119.20'), 'trf_vl_crw_lq': Decimal('0.47'), 'trf_vl_brushwood': 0, 'trf_vl_waste': 0, 'trf_vl_total': Decimal('119.20')}
    ]
b = sorted(a, key=lambda x: x['name_species'])
for i in b:
    print(i['name_species'])


# from PyQt5.QtCore import QSettings
# import sys
# settings = QSettings(r"C:\Users\omelchuk\AppData\Roaming\QGIS\QGIS3\profiles\default\QGIS\QGIS3.ini", QSettings.IniFormat)
#
# print(sys.path)
# print(settings.value(r'PostgreSQL/connections/server/host'))
# print(settings.value(r'PostgreSQL/connections/server/port'))
# print(settings.value(r'PostgreSQL/connections/server/database'))
# print(settings.value(r'PostgreSQL/connections/server/username'))
# print(settings.value(r'PostgreSQL/connections/server/password'))


# import openpyxl, os
# from openpyxl.styles import Alignment, Font, Border, Side
# from openpyxl.worksheet import page
#
# a0 = 'Березинский лесхоз'
# a1 = 'Березинское лесничество'
# a2 = "Главное"
# a3 = 'сплошная'
# a4 = 'тут будет способ рубки'
# a5 = 54
# a6 = 21
# a7 = 2
# a8 = 4.1
# a9 = '(не эксплутационная)'
# a10 = 4
# a11 = 'нету'
# a12 = 'II'
# a13 = '(категория защищённости)'
# a14 = 'крапивный'
# a15 = '5ОЛЧ2Е2Б1С+ОС'
# a16 = 'Ольха черная'
# a17 = 0.7
# a18 = 73
# a19 = 'сырорастущее'
#
# wb = openpyxl.Workbook()
# dest_filename = 'D:\\empty_book.xlsx'  # ! Исправить
# ws = wb.active
# ws.title = "Ведомость перечета деревьев"
# ws.page_setup = page.PrintPageSetup(orientation='landscape', paperSize='9')  # Настройки печати(ориентация)
#
# alf = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
#        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U']
# for i in alf:
#     ws.column_dimensions[i].width = 6.2
#
# """Применяю стиль ко всем ячейкам"""
# for r in range(1, 25):
#     for c in range(1, 22):
#         ws.cell(row=r, column=c).font = Font(size=14, name='Times New Roman')
#
#
# cell = ws.cell(column=1, row=3, value='ВЕДОМОСТЬ ПЕРЕЧЕТА ДЕРЕВЬЕВ, НАЗНАЧЕНЫХ В РУБКУ')
# ws.merge_cells(start_row=3, end_row=3, start_column=1, end_column=21)
# ws.cell(row=3, column=1).alignment = Alignment(horizontal='center', vertical='center')
# ws.cell(row=3, column=1).font = Font(size=14, name='Times New Roman', bold=True)
#
# ws.merge_cells(start_row=4, end_row=5, start_column=1, end_column=21)
#
# ws.cell(column=1, row=6, value='Лесхоз:')
# ws.merge_cells(start_row=6, end_row=6, start_column=1, end_column=2)
#
# ws.cell(column=3, row=6, value=a0)  # Название лесхоза
# ws.cell(column=3, row=6).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=6, end_row=6, start_column=3, end_column=9)
#
# ws.cell(column=11, row=6, value='Лесничество:')
# ws.merge_cells(start_row=6, end_row=6, start_column=11, end_column=13)
#
# ws.cell(column=14, row=6, value=a1)  # Название лесничества
# ws.cell(column=14, row=6).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=6, end_row=6, start_column=14, end_column=21)
#
# ws.cell(column=1, row=7, value='Вид пользования:')
# ws.merge_cells(start_row=7, end_row=7, start_column=1, end_column=4)
#
# ws.cell(column=5, row=7, value=a2)  # Вид пользования
# ws.cell(column=5, row=7).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=7, end_row=7, start_column=5, end_column=13)
#
# ws.cell(column=14, row=7, value='Вид рубки:')
# ws.merge_cells(start_row=7, end_row=7, start_column=14, end_column=16)
#
# ws.cell(column=17, row=7, value=a3)  # Вид рубки
# ws.cell(column=17, row=7).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=7, end_row=7, start_column=17, end_column=21)
#
# ws.cell(column=1, row=8, value='Способ рубки:')
# ws.merge_cells(start_row=8, end_row=8, start_column=1, end_column=3)
#
# ws.cell(column=4, row=8, value=a4)  # Способ рубки
# ws.cell(column=4, row=8).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=8, end_row=8, start_column=4, end_column=21)
#
# ws.cell(column=1, row=9, value='Квартал №')
# ws.merge_cells(start_row=9, end_row=9, start_column=1, end_column=3)
#
# ws.cell(column=4, row=9, value=a5)  # Номер квартала
# ws.cell(column=4, row=9).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=9, end_row=9, start_column=4, end_column=5)
# ws.cell(column=4, row=9).alignment = Alignment(horizontal='left')
#
# ws.cell(column=6, row=9, value='Выдел №')
# ws.merge_cells(start_row=9, end_row=9, start_column=6, end_column=7)
#
# ws.cell(column=8, row=9, value=a6)  # Номер выдела
# ws.cell(column=8, row=9).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=9, end_row=9, start_column=8, end_column=10)
# ws.cell(column=8, row=9).alignment = Alignment(horizontal='left')
#
# ws.cell(column=11, row=9, value='делянка №')
# ws.merge_cells(start_row=9, end_row=9, start_column=11, end_column=13)
#
# ws.cell(column=14, row=9, value=a7)  # Номер делянки
# ws.cell(column=14, row=9).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=9, end_row=9, start_column=14, end_column=16)
# ws.cell(column=14, row=9).alignment = Alignment(horizontal='left')
#
# ws.cell(column=17, row=9, value='Площадь')
# ws.merge_cells(start_row=9, end_row=9, start_column=17, end_column=18)
#
# ws.cell(column=19, row=9, value=a8)  # площадь
# ws.cell(column=19, row=9).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=9, end_row=9, start_column=19, end_column=20)
# ws.cell(column=19, row=9).alignment = Alignment(horizontal='left')
#
# ws.cell(column=21, row=9, value='га.')
#
# ws.cell(column=1, row=10, value='в том числе не эксплуатационнная')
# ws.merge_cells(start_row=10, end_row=10, start_column=1, end_column=7)
#
# ws.cell(column=8, row=10, value=a9)  # площадь не эксплуатационная
# ws.cell(column=8, row=10).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=10, end_row=10, start_column=8, end_column=15)
# ws.cell(column=8, row=10).alignment = Alignment(horizontal='left')
#
# ws.cell(column=16, row=10, value='га.')
#
# ws.cell(column=1, row=11, value='Лесосека №')
# ws.merge_cells(start_row=11, end_row=11, start_column=1, end_column=3)
#
# ws.cell(column=4, row=11, value=a10)  # лесосека
# ws.cell(column=4, row=11).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=11, end_row=11, start_column=4, end_column=7)
# ws.cell(column=4, row=11).alignment = Alignment(horizontal='left')
#
# ws.cell(column=8, row=11, value='года, группа лесов')
# ws.merge_cells(start_row=11, end_row=11, start_column=8, end_column=11)
#
# ws.cell(column=12, row=11, value=a11)  # группа лесов
# ws.cell(column=12, row=11).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=11, end_row=11, start_column=12, end_column=14)
# ws.cell(column=12, row=11).alignment = Alignment(horizontal='left')
#
# ws.cell(column=15, row=11, value=', разряд такс:')
# ws.merge_cells(start_row=11, end_row=11, start_column=15, end_column=17)
#
# ws.cell(column=18, row=11, value=a12)  # разряд такс
# ws.cell(column=18, row=11).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=11, end_row=11, start_column=18, end_column=21)
# ws.cell(column=18, row=11).alignment = Alignment(horizontal='left')
#
# ws.cell(column=1, row=12, value='Категория защитности:')
# ws.merge_cells(start_row=12, end_row=12, start_column=1, end_column=5)
#
# ws.cell(column=6, row=12, value=a13)  # Категория защитности
# ws.cell(column=6, row=12).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=12, end_row=12, start_column=6, end_column=21)
# ws.cell(column=6, row=12).alignment = Alignment(horizontal='left')
#
# ws.cell(column=1, row=13, value='Тип леса:')
# ws.merge_cells(start_row=13, end_row=13, start_column=1, end_column=2)
#
# ws.cell(column=3, row=13, value=a14)  # тип леса
# ws.cell(column=3, row=13).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=13, end_row=13, start_column=3, end_column=5)
# ws.cell(column=3, row=13).alignment = Alignment(horizontal='left')
#
# ws.cell(column=6, row=13, value=', состав насаждения')
# ws.merge_cells(start_row=13, end_row=13, start_column=6, end_column=9)
#
# ws.cell(column=10, row=13, value=a15)  # состав насаждения
# ws.cell(column=10, row=13).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=13, end_row=13, start_column=10, end_column=14)
# ws.cell(column=10, row=13).alignment = Alignment(horizontal='left')
#
# ws.cell(column=15, row=13, value=', преобладающая порода')
# ws.merge_cells(start_row=13, end_row=13, start_column=15, end_column=19)
#
# ws.cell(column=20, row=13, value=a16)  # преоблодающая порода
# ws.cell(column=20, row=13).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=13, end_row=13, start_column=20, end_column=21)
# ws.cell(column=20, row=13).alignment = Alignment(horizontal='left')
#
# ws.cell(column=1, row=14, value='Полнота')
# ws.merge_cells(start_row=14, end_row=14, start_column=1, end_column=2)
#
# ws.cell(column=3, row=14, value=a17)  # полнота
# ws.cell(column=3, row=14).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=14, end_row=14, start_column=3, end_column=5)
# ws.cell(column=3, row=14).alignment = Alignment(horizontal='center')
#
# ws.cell(column=6, row=14, value=', возраст')
# ws.merge_cells(start_row=14, end_row=14, start_column=6, end_column=7)
#
# ws.cell(column=8, row=14, value=a18)  # возраст
# ws.cell(column=8, row=14).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=14, end_row=14, start_column=8, end_column=11)
# ws.cell(column=8, row=14).alignment = Alignment(horizontal='center')
#
# ws.cell(column=12, row=14, value='Состояние насаждения')
# ws.merge_cells(start_row=14, end_row=14, start_column=12, end_column=16)
#
# ws.cell(column=17, row=14, value=a19)  # Состояние насаждения
# ws.cell(column=17, row=14).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=14, end_row=14, start_column=17, end_column=21)
# ws.cell(column=17, row=14).alignment = Alignment(horizontal='left')
#
#
# ws.cell(column=1, row=15).border = Border(bottom=Side(style='thin'))
# ws.merge_cells(start_row=15, end_row=15, start_column=1, end_column=21)
#
#
#
#
#
#
#
#
#
#
#
# """Сохранение и открытие документа"""
# wb.save(filename=dest_filename)
# os.system('start excel.exe D:\\empty_book.xlsx')
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # dm = ws.cell(column=1, row=1, value='Ступень толщины, см.')
# # ws.merge_cells(start_row=1, end_row=3, start_column=1, end_column=1)
# #
# # cell = ws.cell(column=2, row=1, value='Количество деревьев по породам')
# # ws.merge_cells(start_row=1, end_row=1, start_column=2, end_column=len(species)*2+1)
# # cell.alignment = Alignment(wrapText=True)
# #
# # for spc in species:
# #     column = species[spc]
# #     """Название породы"""
# #     cell = ws.cell(column=column, row=2, value=spc)  # TODO: перевести породы
# #     ws.merge_cells(start_row=2, end_row=2, start_column=column, end_column=column+1)
# #
# #     """Деловая\дровяная"""
# #     cell = ws.cell(column=column, row=3, value='Деловая')
# #     cell = ws.cell(column=column+1, row=3, value='Дровяная')
# #
# # null_row =
# # for dr in dmr:
# #     cell = ws.cell(column=1, row=null_row, value=dr)
# #     null_row+=1
# #
# #
# #
# #
# # """Границы ячеек"""
# # thin_border = Border(left=Side(style='thin'),
# #                      right=Side(style='thin'),
# #                      top=Side(style='thin'),
# #                      bottom=Side(style='thin'))
# # for i in range(1, ws.max_row + 1):
# #     for ii in range(1, ws.max_column + 1):
# #         ws.cell(row=i, column=ii).border = thin_border
# #         ws.cell(row=i, column=ii).alignment = Alignment(horizontal='center',
# #                                                         vertical='center')  # Центрирую надпись
# #
# #
# # dm.alignment = Alignment(wrapText=True)
