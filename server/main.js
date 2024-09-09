const express = require('express');
const cors = require("cors");
const bodyParser = require('body-parser');
const morgan = require('morgan'); // Импортируем morgan
require('dotenv').config(); // Для загрузки переменных окружения 
const nano = require('nano');

USERNAME = process.env.COUCH_BD_USER;
PASSWORD = process.env.COUCH_BD_PASSWORD;

// Подключение к CouchDB
const couch = nano(`http://${USERNAME}:${PASSWORD}@localhost:5984`);
const db = couch.db.use('work');

const app = express();
app.use(cors());
app.use(morgan('combined')); // Используем morgan для логгирования запросов
const PORT = process.env.PORT || 3000;

// Функция для получения текущей даты и времени в нужном формате
function getCurrentTimestamp() {
    const date = new Date();
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

// Middleware для парсинга JSON
app.use(bodyParser.json());

// Эндпоинт для проверки пароля
app.post('/login', async (req, res) => {
    const { password } = req.body;
    console.log(req.body);

    try {
        const employee = await db.view('design_doc', 'view_name', { key: password });

        if (employee.rows.length > 0) {
            res.status(200).json(employee.rows[0].value);
        } else {
            res.status(401).json({ message: 'Неверный пароль' });
        }
    } catch (error) {
        res.status(500).json({ message: 'Ошибка сервера', error });
    }
});

const server = app.listen(PORT, () => {
    const addressInfo = server.address(); // Адрес сервера 
    console.log(`Сервер слушает на адресе ${addressInfo.address} и порту ${addressInfo.port} в режиме ${app.settings.env}`);
});
