import React, { useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileExport } from '@fortawesome/free-solid-svg-icons';
import './style.scss';
import Template from 'pages/Template/Template';
import Header from 'components/Header/Header';
import Manager from 'components/Manager/Manager';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { update } from 'components/Redux/managers/actions';
import Loader from 'components/Loader/Loader';

const Analytics = () => {
    const managers = useSelector((state) => state.managers.list);
    const dispatch = useDispatch();
    useEffect(() => dispatch(update()));

    return (
        <Template>
            <Header title='Общая аналитика звонков'>
                <Link to='/export/managers/1/Вячеслав.csv' id='export' download>
                    <FontAwesomeIcon icon={faFileExport} />
                    Экспорт
                    {/* <img
                        src='/static/images/managers-export.svg'
                        style={{ cursor: 'pointer' }}
                        alt='export'
                    /> */}
                </Link>
            </Header>
            <div className='managers-group'>
                {managers
                    ? managers.map((manager, i) => (
                        <Manager manager={manager} key={i} />
                    ))
                    : <Loader />}
            </div>
        </Template>
    );
};
export default Analytics;
