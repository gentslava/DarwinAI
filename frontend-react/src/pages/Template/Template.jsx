import React from 'react';
import './style.scss';
import Menu from 'components/Menu/Menu';

const Template = (props) => (
    <div className='main-frame'>
        <Menu />
        <div className='content'>{props.children}</div>
    </div>
);
export default Template;
