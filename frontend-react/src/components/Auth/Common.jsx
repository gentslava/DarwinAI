import React from 'react';
import './style.scss';
import Logo from './Logo';

const Common = (props) => (
    <div className='login'>
        <Logo />
        {props.children}
    </div>
);
export default Common;
