import React, { useEffect } from 'react';
import './style.scss';
import background from 'assets/images/dashboard-bg.png';
import Template from 'pages/Template/Template';
import Header from 'components/Header/Header';
import Balance from 'components/Balance/Balance';
import Table from 'components/Table/Table';
import { useDispatch, useSelector } from 'react-redux';
import { update } from 'components/Redux/critcalls/actions';

const rootBG = `#root {
    background: url(${background}) center top/cover;
}`;

const name = 'Критические звонки';
const headers = [
    'Оператор',
    'Звонок',
    'Объем речи',
    'Соответствие скрипту',
    'Подстройка по громкости',
    'Подстройка по скорости',
    'Чистота речи',
    'Перебивания',
    'Критичные слова',
    'Нежелательные слова',
    'Негатив в диалоге \u0085 оператор | клиент',
];

const Dashboard = () => {
    const calls = useSelector((state) => state.critcalls.list);
    const dispatch = useDispatch();
    useEffect(() => dispatch(update()));

    return (
        <Template>
            <Header title='Darwin AI'>
                <Balance />
            </Header>
            <Table name={name} headers={headers} calls={calls} className='dashboard' />
            <style>{rootBG}</style>
        </Template>
    );
};
export default Dashboard;
