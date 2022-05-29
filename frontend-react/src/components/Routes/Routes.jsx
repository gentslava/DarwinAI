import React, { Suspense, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import jsCookie from 'js-cookie';
import Context from 'components/Context';
import urls from 'components/Routes/urls';
import Login from 'pages/Login/Login';
import Loader from 'components/Loader/Loader';

const removeToken = (setToken) => {
    jsCookie.remove('csrftoken');
    setToken('');
};

const Common = () => {
    const [token, setToken] = useState(jsCookie.get('csrftoken'));

    const routeComponents = urls.map((link, key) => (
        <Route path={link.path} element={link.component} key={key} />
    ));
    if (!token) {
        return <Login setToken={setToken} />;
    }
    return (
        <Context.Provider value={removeToken}>
            <Suspense fallback={<Loader />}>
                <Routes>{routeComponents}</Routes>
            </Suspense>
        </Context.Provider>
    );
};
export default Common;
