import React from 'react';
import './style.scss';

const Header = (props) => (
    <div className='header'>
        <div className='nav-prev'>
            <h1>{props.title}</h1>
        </div>
        {props.children}
    </div>
);
export default Header;
