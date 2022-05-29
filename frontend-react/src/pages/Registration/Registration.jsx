import React, { useState } from 'react';
import Common from 'components/Auth/Common';
import CSRFToken from 'components/Auth/CSRFToken';
import LoginInput from 'components/Auth/LoginInput';
import EmailInput from 'components/Auth/EmailInput';
import PasswordInput from 'components/Auth/PasswordInput';
import Errors from 'components/Auth/Errors';

const createUser = async () => {
    // const token = fetch('https://demo.darwin-ai.ru/login/', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(credentials),
    // }).then((data) => data.json());
};

const Registration = () => {
    const [csrfmiddlewaretoken, setCSRFMiddlewareToken] = useState();
    const [login, setLogin] = useState();
    const [email, setEmail] = useState();
    const [password, setPassword] = useState();

    const handleSubmit = async (event) => {
        event.preventDefault();
        const data = {
            csrfmiddlewaretoken,
            login,
            email,
            password,
        };
        createUser(data);
    };

    return (
        <Common>
            <h1>Registration</h1>
            <form onSubmit={handleSubmit}>
                <CSRFToken setCSRFMiddlewareToken={setCSRFMiddlewareToken} />
                <LoginInput setLogin={setLogin} />
                <EmailInput setEmail={setEmail} />
                <PasswordInput setPassword={setPassword} />
                <Errors />
                <button type='submit'>Registration</button>
            </form>
        </Common>
    );
};
export default Registration;
