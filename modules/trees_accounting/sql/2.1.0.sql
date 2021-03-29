ALTER TABLE public.subcompartment_taxation ADD ptg int2 NULL;
ALTER TABLE public.subcompartment_taxation ADD por_m3 int NULL;
ALTER TABLE public.subcompartment_taxation ADD por_m2 int NULL;
ALTER TABLE public.subcompartment_taxation ADD xmer1 int NULL;
ALTER TABLE public.subcompartment_taxation ADD xmer2 int NULL;
ALTER TABLE public.subcompartment_taxation ADD xmer3 int NULL;

ALTER TABLE public.subcompartment_taxation ADD CONSTRAINT subcompartment_taxation_fk FOREIGN KEY (xmer1) REFERENCES "dictionary".xmer(code_xmer);
ALTER TABLE public.subcompartment_taxation ADD CONSTRAINT subcompartment_taxation_fk_1 FOREIGN KEY (xmer2) REFERENCES "dictionary".xmer(code_xmer);
ALTER TABLE public.subcompartment_taxation ADD CONSTRAINT subcompartment_taxation_fk_2 FOREIGN KEY (xmer3) REFERENCES "dictionary".xmer(code_xmer);
ALTER TABLE public.subcompartment_taxation ADD CONSTRAINT subcompartment_taxation_fk_3 FOREIGN KEY (por_m3) REFERENCES "dictionary".dict_species(class_code_por);
ALTER TABLE public.subcompartment_taxation ADD CONSTRAINT subcompartment_taxation_fk_4 FOREIGN KEY (por_m2) REFERENCES "dictionary".dict_species(class_code_por);







CREATE TABLE dictionary.xmer (
	code_xmer int4 NOT NULL,
	name_xmer varchar NULL,
	CONSTRAINT xmer_pkey PRIMARY KEY (code_xmer)
);


INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1211, 'Сплошная рубка главного пользования');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1212, 'Рубка с сохранением подроста');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1269, 'Рубка по состоянию');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1222, 'Равномерно-постепенная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1227, 'Последний прием постепенной рубки');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1223, 'Группово-постепенная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1224, 'Полосно-постепенная 2-х приемная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1265, 'Добровольно-выборочная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1216, 'Узколесосечная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1251, 'Длительно-постепенная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1301, 'Рубка единичных деревьев на лесных землях, не покрытых лесами');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1701, 'Рубка реконструкции сплошная');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4321, 'Подсев трав');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1842, 'Рубка опасных в отношении автомобильных дорог, воздушных линий связии и электропередам деревьев');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1601, 'Сплошная санитарная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1605, 'Выборочная санитарная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1621, 'Уборка захламленности');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3375, 'Перевод в ценное хозяйство рубками ухода');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1470, 'Прорубка технологических коридоров');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1411, 'Осветление');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1414, 'Агротехнический уход');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1415, 'Химический уход');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1425, 'Прочистка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1431, 'Прореживание');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2304, 'Установка аншлага');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2352, 'Устройство кострищ');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1435, 'Проходная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1455, 'Обрезка сучьев');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1550, 'Рубка улучшения состава');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(5322, 'Запретить подсочку');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1528, 'Рубка улучшения пространственного размещения');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1527, 'Рубка улучшения эстетических качеств');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2345, 'Установка лесной мебели');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2361, 'Установка мусоросборников');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1704, 'Реконструкция низкополн. насаждений куртинно-груповым способом');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1705, 'Реконструкция малоценных насаждения коридорным способом');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1552, 'Рубка формирования (переформирования)');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1554, 'Рубка обновления');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3212, 'Лесные культуры декоративные под пологом леса');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2342, 'Установка беседки');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2343, 'Установка навеса');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2354, 'Установка туалета');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2401, 'Ремизные посадки');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(6221, 'Минерализация противопожарного разрыва');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(5321, 'Огораживание участка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3272, 'Уход за подростом');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3271, 'Естественное возобновление путем сохранения подроста (2 яруса) при несплошных рубках');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3211, 'Лесные культуры');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3214, 'Лесные культуры под пологом леса');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3273, 'Естественное возобновление путем сохранения подроста при сплошных рубках');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3274, 'Содействие естественому возобновлению на не покрытых лесом землях');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3275, 'Содействие естественому возобновлению под пологом леса');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1500, 'Рубка раскрытия перспективы');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1551, 'Рубка формирования опушки');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3285, 'Естественное возобновление на не покрытых лесом землях без мер содействия');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3282, 'Дополнение несомкнувшихся лесных культур');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(5315, 'Запретить пастьбу скота');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4323, 'Запретить сенокошение');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3203, 'Ландшафтные культуры');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1884, 'Расчистка под с/х пользование');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2346, 'Устройство мест отдыха');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4211, 'Внесение удобрений');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4307, 'Мелиорация');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3329, 'Плантационные лесные культуры');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4344, 'Срезка кочек');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4345, 'Коренное улучшение');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4351, 'Поверхностное улучшение');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1845, 'Рубки леса, проводимые при прокладке квартальных просек, создании противопожарных разрывов и их содержании');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1881, 'Расчистка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(6211, 'Создание минерализованных полос');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(4113, 'Ремонт мелиоративной сети');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3147, 'Рекультивация земель');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3202, 'Декоративные посадки');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2418, 'Биотехнические мероприятия');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2387, 'Уборка мусора');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3330, 'Закладка временных лесосеменных участков');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3331, 'Закладка постоянных лесосеменных участков');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2271, 'Для с/х пользования');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2371, 'Оборудование стоянки туристов');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2372, 'Оборудование автостоянок');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2412, 'Создание кормовых полей');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1846, 'Разрубка  противопожарных  разрывов');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(7131, 'Ремонт дорог');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1225, 'Полосно-постепенная 3-х приемная рубка');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1321, 'Рубка на приаэродромных территориях');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1556, 'Рубка насаждений в топливно-энергетических целях');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1808, 'Рубка плантационных лесных культур');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1809, 'Рубка деревьев, являющихся промежуточными хозяевами вредителей и болезней лесов, по периметру существующих и проектируемых лесных питомников и лесосеменных плантаций');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1810, 'Рубка деревьев, оставленных на лесосеке в целях воспроизводства лесов (семенных деревьев)');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1812, 'Рубка полос растущих хвойных насаждений в межочаговом пространстве и по опушкам усыхающих хвойных насаждений');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1813, 'Рубка деревьев на постоянных лесосеменных плантациях');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1843, 'Рубка леса при расчистке от лесных насаждений участков лесного фонда для строительства дорог, инженерных коммуникаций, других линейных сооружений, поиска и разведки полезных ископаемых и других ресурсов недр');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1847, 'Рубка деревьев, мешающих прохождению лесовозной техники при вывозке древесины с лесосек по сложившейся лесовозной сети');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1848, 'Разрубка подъездных путей к лесосеке');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1849, 'Разрубка стрелковых линий');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3286, 'Оставление семенников');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3283, 'Ввод главной (целевой) породы');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3332, 'Закладка плантаций');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3233, 'Создание плантационных л/к для выращивания топливной древесины');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3234, 'Создание плантационных л/к для выращивания балансовой древесины');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3235, 'Создание плантационных л/к для выращивания крупномерной древесины');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1851, 'Рубка деревьев, представляющих опасность для жизни граждан');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1852, 'Рубка единичных деревьев в пограничной полосе и пограничной зоне');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1853, 'Рубка, проводимая в целях проведения подготовительных работ');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1228, 'Последний прием полосно-постепенной рубки');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1901, 'Содействие естественному возобновлению после постепенных рубок');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1858, 'Расчистка противопожарного разрыва');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1857, 'Разрубка противопожарного разрыва');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3281, 'Дополнение сомкнувшихся лесных культур');
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(0, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(10, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(20, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(15, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(25, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(30, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(40, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(5, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(100, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(50, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(35, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(45, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(3, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(80, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(2, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(70, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1855, NULL);
INSERT INTO dictionary.xmer (code_xmer, name_xmer) VALUES(1856, 'Расч.кв.просек');

