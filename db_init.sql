CREATE TABLE battles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    winner VARCHAR(255) NOT NULL,
    battle_log JSON,
    battle_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);