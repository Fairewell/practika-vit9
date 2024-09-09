const nano = require('nano');

// Подключение к CouchDB
const couch = nano('http://Vasilaki_PRACTICS:vasilaki_090301@localhost:5984');
const db = couch.db.use('work');

// Пример данных о работниках
const employees = [
    {
        _id: 'employee_001',
        password: 'password123',
        object: 'Стройка 1',
        working_hours: {
            monday: {
                start: '10:00',
                end: '20:00',
                lunch: {
                    start: '12:00',
                    end: '13:00'
                },
                comment: 'Работа на стройке 1'
            },
            tuesday: {
                start: '10:00',
                end: '20:00',
                lunch: {
                    start: '12:00',
                    end: '13:00'
                },
                comment: 'Работа на стройке 1'
            }
            // Добавьте другие дни по необходимости
        },
        tools: [
            { name: 'Молоток', price: 500 },
            { name: 'Отвертка', price: 300 }
        ],
        team: 'Бригада 1',
        supervisor: 'Иванов И.И.'
    },
    {
        _id: 'employee_002',
        password: 'mypassword456',
        object: 'Стройка 2',
        working_hours: {
            monday: {
                start: '09:00',
                end: '18:00',
                lunch: {
                    start: '12:00',
                    end: '13:00'
                },
                comment: 'Работа на стройке 2'
            },
            wednesday: {
                start: '09:00',
                end: '18:00',
                lunch: {
                    start: '12:00',
                    end: '13:00'
                },
                comment: 'Работа на стройке 2'
            }
            // Добавьте другие дни по необходимости
        },
        tools: [
            { name: 'Лопата', price: 250 },
            { name: 'Уровень', price: 700 }
        ],
        team: 'Бригада 2',
        supervisor: 'Петров П.П.'
    },
    {
        _id: 'employee_003',
        password: 'securepassword789',
        object: 'Стройка 3',
        working_hours: {
            thursday: {
                start: '11:00',
                end: '19:00',
                lunch: {
                    start: '14:00',
                    end: '15:00'
                },
                comment: 'Работа на стройке 3'
            },
            friday: {
                start: '11:00',
                end: '19:00',
                lunch: {
                    start: '14:00',
                    end: '15:00'
                },
                comment: 'Работа на стройке 3'
            }
            // Добавьте другие дни по необходимости
        },
        tools: [
            { name: 'Перфоратор', price: 1500 },
            { name: 'Болгарка', price: 1200 }
        ],
        team: 'Бригада 3',
        supervisor: 'Сидоров С.С.'
    }
];

// Функция для добавления работников в базу данных
const addEmployees = async () => {
    for (const employee of employees) {
        try {
            const response = await db.insert(employee);
            console.log(`Работник добавлен: ${response.id}`);
        } catch (error) {
            console.error('Ошибка добавления работника:', error);
        }
    }
};

// Запуск функции добавления работников
addEmployees();