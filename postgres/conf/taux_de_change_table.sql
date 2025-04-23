CREATE TABLE taux_de_change (
    id SERIAL PRIMARY KEY,
    devise_source VARCHAR(3) NOT NULL,
    devise_cible VARCHAR(3) NOT NULL,
    taux NUMERIC(10, 4) NOT NULL,
    date_taux DATE NOT NULL
);

INSERT INTO taux_de_change (devise_source, devise_cible, taux, date_taux) VALUES
('USD', 'EUR', 0.9250, '2025-04-14'),
('EUR', 'USD', 1.0811, '2025-04-14'),
('USD', 'JPY', 151.35, '2025-04-14'),
('GBP', 'USD', 1.2532, '2025-04-14'),
('EUR', 'JPY', 163.45, '2025-04-14');



