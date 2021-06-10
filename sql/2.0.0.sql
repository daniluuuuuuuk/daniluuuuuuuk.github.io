CREATE TABLE "dictionary".kind_seeds (
	code_kind_seeds int4 NOT NULL,
	name_kind_seeds varchar(50) NOT NULL,
	CONSTRAINT kind_seeds_pkey PRIMARY KEY (code_kind_seeds)
);


INSERT INTO "dictionary".kind_seeds (code_kind_seeds,name_kind_seeds) VALUES 
(1,'Одиночные деревья -семенники')
,(2,'Группы по 3-5 деревьев')
,(3,'Куртины семенные')
,(4,'Сохранение биоразнообразия')
,(5,'Деревья, запрещенные к рубке')
;








CREATE TABLE public.trees_not_cutting (
	area_uuid uuid NOT NULL,
	code_species int2 NOT NULL,
	seed_type_code int2 NOT NULL,
	seed_dmr int2 NOT NULL,
	seed_count int2 NULL,
	seed_number varchar NULL,
	id serial NOT NULL
);
CREATE INDEX trees_not_cutting_area_uuid_idx ON public.trees_not_cutting USING btree (area_uuid);


-- public.trees_not_cutting foreign keys

ALTER TABLE public.trees_not_cutting ADD CONSTRAINT trees_not_cutting_fk FOREIGN KEY (code_species) REFERENCES dictionary.species(code_species);
ALTER TABLE public.trees_not_cutting ADD CONSTRAINT trees_not_cutting_fk_1 FOREIGN KEY (seed_type_code) REFERENCES dictionary.kind_seeds(code_kind_seeds);








CREATE TABLE public.trees_trf_height (
	area_uuid uuid NOT NULL,
	code_species int2 NOT NULL,
	code_trf_height int2 NOT NULL,
	CONSTRAINT trees_trf_height_fk FOREIGN KEY (code_species) REFERENCES "dictionary".species(code_species),
	CONSTRAINT trees_trf_height_fk_1 FOREIGN KEY (code_trf_height) REFERENCES "dictionary".trf_height(code_trf_height)
);
CREATE INDEX trees_trf_height_area_uuid_idx ON public.trees_trf_height (area_uuid);

ALTER TABLE public.trees_trf_height ADD id serial8 NOT NULL;
ALTER TABLE public.trees_trf_height ADD CONSTRAINT trees_trf_height_pk PRIMARY KEY (id);

