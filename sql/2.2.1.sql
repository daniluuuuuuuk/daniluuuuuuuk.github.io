ALTER TABLE public.subcompartment_taxation ADD grv int2 NULL;
ALTER TABLE public.subcompartment_taxation_m10 ALTER COLUMN poln TYPE numeric(3,2) USING poln::numeric;