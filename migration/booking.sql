CREATE TABLE bookings
(
    id               SERIAL PRIMARY KEY,
    phone            VARCHAR(20) NOT NULL,
    guest_count      TEXT         NOT NULL,
    reservation_date TEXT        NOT NULL,
    code             TEXT UNIQUE
);


INSERT INTO bookings (phone, guest_count, reservation_date, code)

VALUES ('0612345678', '2', '2025-04-20', 'BLABLA'),
       ('0755667788', '4', '2025-04-20', 'BLUBLU'),
       ('0788990011', '3', '2025-04-21', 'BLIBLI');
