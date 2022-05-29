import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLock, faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';

const Input = ({ setPassword }) => {
    const [passwordShow, setPasswordShow] = useState(false);
    return (
        <div className='input' onChange={(event) => setPassword(event.target.value)}>
            <FontAwesomeIcon icon={faLock} />
            <input
                type={passwordShow ? 'text' : 'password'}
                placeholder='Password'
                maxLength={255}
                required
            />
            <FontAwesomeIcon
                className='icon-Show'
                icon={passwordShow ? faEyeSlash : faEye}
                // onMouseDown={() => setPasswordShow(true)}
                // onMouseUp={() => setPasswordShow(false)}
                onClick={() => setPasswordShow((state) => !state)}
            />
        </div>
    );
};
export default React.memo(Input);
