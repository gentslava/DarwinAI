import React from 'react';
import { Link } from 'react-router-dom';

const style = {
    wrapper: {
        position: 'absolute',
        textAlign: 'center',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        marginTop: '-50px',
    },
};

const NotFound = () => (
    <div className='wrapper' style={style.wrapper}>
        <h1>Hmm.</h1>
        <p>It seems that you&apos;re lost. Let us help guide you out and get you back home.</p>
        <Link to='/'>Home</Link>
    </div>
);
export default NotFound;
