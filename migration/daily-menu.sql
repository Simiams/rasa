CREATE TABLE daily_menu
(
    id          SERIAL PRIMARY KEY,
    day_of_week INT,
    plat        TEXT NOT NULL,
    allergens  TEXT
);

INSERT INTO daily_menu (day_of_week, plat, allergens)
VALUES (1, 'Poulet rôti', 'gluten'),
       (2, 'Poisson grillé', 'poisson'),
       (3, 'Burger', 'aucun'),
       (4, 'Salade', 'aucun'),
       (5, 'Grec', 'aucun'),
       (6, 'Pizza', 'aucun'),
       (7, 'Ratatouille', 'aucun');

