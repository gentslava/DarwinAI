import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope } from '@fortawesome/free-solid-svg-icons';

const Input = ({ setEmail }) => (
    <div className='input' onChange={(event) => setEmail(event.target.value)}>
        <FontAwesomeIcon icon={faEnvelope} />
        <input type='email' placeholder='E-mail' maxLength='255' required />
    </div>
);
export default React.memo(Input);
