import React from 'react';
import './style.scss';

const Loader = () => (
    <div className='lds-ring'>
        <div />
        <div />
        <div />
        <div />
    </div>
);
export default React.memo(Loader);
