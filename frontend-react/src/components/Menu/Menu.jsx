/* eslint-disable jsx-a11y/anchor-is-valid */
import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import './style.scss';
import Context from 'components/Context';
import urls from 'components/Routes/urls';

const Menu = () => {
    const { removeToken } = useContext(Context);
    return (
        <div className='menu'>
            <div className='head'>
                <p className='icon-Logo' id='logo' />
                {urls
                    .filter((url) => url.show)
                    .map((url, key) => (url.disabled ? (
                        <a key={key}>
                            {url.icon}
                            {url.title}
                        </a>
                    ) : (
                        <NavLink to={url.path} key={key}>
                            {url.icon}
                            {url.title}
                        </NavLink>
                    )))}
            </div>
            <div className='foot'>
                <NavLink to='/logout' onClick={removeToken}>
                    Выйти
                </NavLink>
            </div>
        </div>
    );
};
export default Menu;
