-- Seed data

INSERT INTO countries (id, name) VALUES
(1, 'Guatemala');

INSERT INTO companies (id, country_id, name) VALUES
(1, 1, 'Empresa Demo');

INSERT INTO branches (id, company_id, name) VALUES
(1, 1, 'Sede Central');

INSERT INTO questions (id, text) VALUES
(1, '¿Qué tan satisfecho(a) estás con el servicio?'),
(2, '¿El personal fue amable?'),
(3, '¿El tiempo de atención fue adecuado?'),
(4, '¿Recomendarías el servicio?'),
(5, '¿Qué podríamos mejorar?');
