CREATE TABLE plats (
                       id SERIAL PRIMARY KEY,
                       name TEXT NOT NULL,
                       description TEXT,
                       price NUMERIC(5,2) NOT NULL
);

CREATE TABLE allergens (
                            id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE
);

CREATE TABLE plat_allergen (
                                plat_id INT REFERENCES plats(id) ON DELETE CASCADE,
                                allergen_id INT REFERENCES allergens(id) ON DELETE CASCADE,
                                PRIMARY KEY (plat_id, allergen_id)
);

INSERT INTO plats (name, description, price) VALUES
                                               ('Poulet rôti', 'Servi avec légumes grillés', 14.90),
                                               ('Saumon grillé', 'Filet de saumon avec riz', 16.50),
                                               ('Pâtes carbonara', 'Recette traditionnelle', 13.00),
                                               ('Ratatouille', 'Légumes mijotés', 11.50);

INSERT INTO allergens (name) VALUES
                                 ('gluten'),
                                 ('œufs'),
                                 ('poisson'),
                                 ('lactose'),
                                 ('fruits à coque'),
                                 ('soja');

INSERT INTO plat_allergen (plat_id, allergen_id) VALUES
-- Poulet rôti : contient gluten
(1, 1),

-- Saumon grillé : contient poisson
(2, 3),

-- Pâtes carbonara : contient gluten, œufs, lactose
(3, 1),
(3, 2),
(3, 4);
