import React, { useState } from 'react';
import jsCookie from 'js-cookie';
import Common from 'components/Auth/Common';
import CSRFToken from 'components/Auth/CSRFToken';
import LoginInput from 'components/Auth/LoginInput';
import PasswordInput from 'components/Auth/PasswordInput';
import Errors from 'components/Auth/Errors';

const loginUser = async () => {
    // const token = fetch('https://demo.darwin-ai.ru/login/', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(credentials),
    // }).then((data) => data.json());
    const token = 'Ae0sgffZ7no91pbfEDqwkTlpNrQQsFVWgCoe89jvZzWi9Bb2d3dKExHQqTYv3vcW';
    jsCookie.set('csrftoken', token);
    return token;
};

const Login = ({ setToken }) => {
    const [csrfmiddlewaretoken, setCSRFMiddlewareToken] = useState();
    const [login, setLogin] = useState();
    const [password, setPassword] = useState();

    const handleSubmit = async (event) => {
        event.preventDefault();
        const authData = {
            csrfmiddlewaretoken,
            login,
            password,
        };
        const token = await loginUser(authData);
        setToken(token);
    };

    return (
        <Common>
            <h1>Sign in to access your dashboard</h1>
            <form onSubmit={handleSubmit}>
                <CSRFToken setCSRFMiddlewareToken={setCSRFMiddlewareToken} />
                <LoginInput setLogin={setLogin} />
                <PasswordInput setPassword={setPassword} />
                <Errors />
                <button type='submit'>Log In</button>
            </form>
        </Common>
    );
};
export default Login;
