import React from 'react';
import { Link } from 'react-router-dom';
import './style.scss';
import avatar from 'assets/images/avatar.svg';
import Star from './Star/Star';

const Manager = ({ manager }) => (
    <Link
        to={`/managers/manager-${manager.id}`}
        style={{ display: manager.status ? '' : 'none' }}
    >
        <div className='manager'>
            <div className='person'>
                <Star rating={manager.rating} color={manager.color} />
                <img src={avatar} alt='' />
                <div style={{ margin: 'auto 0px' }}>
                    <p style={{ margin: '0px' }}>
                        {manager.first_name}
                        {' '}
                        {manager.last_name}
                    </p>
                    <span style={{ fontSize: '12px', color: 'rgb(151, 151, 151)' }}>
                        {manager.department}
                    </span>
                </div>
            </div>
            <div className='goals'>
                <div className='goal'>
                    <p className='icon-Target' />
                    <span className='value'>{manager.count}</span>
                    <span className='description'>Всего звонков</span>
                </div>
                <div className='goal'>
                    <span className='value'>{manager.critical}</span>
                    <span className='description'>Критические звонки</span>
                </div>
                <div className='goal'>
                    <span className='value'>{manager.purity}</span>
                    <span className='description'>Чистота речи</span>
                </div>
                <div className='goal' style={{ border: 'unset' }}>
                    <span className='value'>{manager.script_following}</span>
                    <span className='description'>Выполнение скрипта</span>
                </div>
            </div>
        </div>
    </Link>
);
export default Manager;
