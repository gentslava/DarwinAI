/* eslint-disable react/jsx-no-useless-fragment */
import React, { lazy } from 'react';

const Registration = lazy(() => import('pages/Registration/Registration'));
const Dashboard = lazy(() => import('pages/Dashboard/Dashboard'));
const Analytics = lazy(() => import('pages/Analytics/Analytics'));
const Calls = lazy(() => import('pages/Analytics/Calls/Calls'));
const NotFound = lazy(() => import('pages/NotFound/NotFound'));

const urls = [
    {
        title: 'Рабочий стол',
        path: '/',
        icon: (
            <p className='icon-Dashboard'>
                <span className='path1' />
                <span className='path2' />
                <span className='path3' />
                <span className='path4' />
                <span className='path5' />
                <span className='path6' />
            </p>
        ),
        show: true,
        component: <Dashboard />,
    },
    {
        title: 'Аналитика звонков',
        path: '/managers',
        icon: (
            <p className='icon-Analytics'>
                <span className='path1' />
                <span className='path2' />
            </p>
        ),
        show: true,
        component: <Analytics />,
    },
    {
        title: 'Звонки менеджера',
        path: '/managers/manager-:userId/',
        icon: <React.Fragment />,
        component: <Calls />,
    },
    {
        title: 'Настройки',
        path: '/settings',
        icon: (
            <p className='icon-Phone-settings'>
                <span className='path1' />
                <span className='path2' />
            </p>
        ),
        show: true,
        component: <React.Fragment />,
    },
    {
        title: 'Скрипты',
        path: '/scripts',
        icon: <p className='icon-Scripts' />,
        show: true,
        component: <React.Fragment />,
    },
    {
        title: 'Словари',
        path: '/dictionaries',
        icon: <p className='icon-Dictionary' />,
        show: true,
        component: <React.Fragment />,
    },
    {
        title: 'Команда Проекты',
        path: '/team',
        icon: <p className='icon-Operator' />,
        show: true,
        component: <React.Fragment />,
    },
    {
        title: 'LIVE коучинг',
        path: '',
        icon: (
            <p className='icon-Live'>
                <span className='path1' />
                <span className='path2' />
                <span className='path3' />
            </p>
        ),
        show: true,
        disabled: true,
        component: <React.Fragment />,
    },
    {
        title: 'Регистрация',
        path: '/registr',
        icon: <React.Fragment />,
        component: <Registration />,
    },
    {
        title: '404',
        path: '*',
        icon: <React.Fragment />,
        component: <NotFound />,
    },
];
export default urls;
