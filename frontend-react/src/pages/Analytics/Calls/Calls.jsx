import React, { useEffect } from 'react';
import './style.scss';
import Template from 'pages/Template/Template';
import Header from 'components/Header/Header';
import Upload from 'components/Upload/Upload';
import Manager from 'components/Manager/Manager';
import Table from 'components/Table/Table';
import { useDispatch, useSelector } from 'react-redux';
import { update } from 'components/Redux/calls/actions';
import manager from './manager';

const name = '';
const headers = [
    'Имя файла',
    'Дата',
    'Длительность',
    'Частые подсказки',
    'Выполнение скрипта',
    'Чистота речи',
    'Перебивания',
    'Объем речи',
    'Результат звонка',
];

const Analytics = () => {
    const calls = useSelector((state) => state.calls.list);
    const dispatch = useDispatch();
    useEffect(() => dispatch(update()));

    return (
        <Template>
            <Header title='Статистика звонков менеджера' />
            <Upload />
            <Manager manager={manager} />
            <Table name={name} headers={headers} calls={calls} className='analytics' />
        </Template>
    );
};
export default Analytics;
