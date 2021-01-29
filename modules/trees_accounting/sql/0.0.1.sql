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

