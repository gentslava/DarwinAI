import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserLarge } from '@fortawesome/free-solid-svg-icons';

const Input = ({ setLogin }) => (
    <div className='input' onChange={(event) => setLogin(event.target.value)}>
        <FontAwesomeIcon icon={faUserLarge} />
        <input type='text' placeholder='Login' maxLength={255} required />
    </div>
);
export default React.memo(Input);
