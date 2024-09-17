const express = require('express');
const cors = require("cors");
const bodyParser = require('body-parser');
const morgan = require('morgan'); // Импортируем morgan
require('dotenv').config(); // Для загрузки переменных окружения 
const axios = require('axios');

USERNAME = process.env.COUCH_BD_USER;
PASSWORD = process.env.COUCH_BD_PASSWORD;
DB_NAME = process.env.COUCH_BD_NAME;
// Подключение к CouchDB
const COUCHDB_URL = `http://${USERNAME}:${PASSWORD}@localhost:5984/`;
console.log(COUCHDB_URL);

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

app.post('/login', async (req, res) => {
    const { password } = req.body;
    console.log(req.body);

    try {
        // URL для получения документа
        const couchdb_url = `${COUCHDB_URL}/${DB_NAME}/_all_docs?include_docs=true`;

        // Запрос на получение всех документов
        const response = await axios.get(couchdb_url);

        // Проверка полученных данных
        const employees = response.data.rows;

        // Поиск соответствия пароля
        const employee = employees.find(row => row.doc.password === password);

        if (employee) {
            console.log(employee.doc);

            res.status(200).json(employee.doc);
        } else {
            res.status(401).json({ message: 'Неверный пароль' });
        }
    } catch (error) {
        console.error('Ошибка при получении данных из CouchDB:', error.message);
        res.status(500).json({ message: 'Ошибка сервера', error });
    }
});

const server = app.listen(PORT, () => {
    const addressInfo = server.address(); // Адрес сервера 
    console.log(`Сервер слушает на адресе ${addressInfo.address} и порту ${addressInfo.port} в режиме ${app.settings.env}`);
});
