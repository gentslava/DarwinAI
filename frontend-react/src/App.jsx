import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import 'style.scss';
import Routes from 'components/Routes/Routes';
import { Provider } from 'react-redux';
import { store } from 'components/Redux/store';

const App = () => (
    <Provider store={store}>
        <BrowserRouter>
            <Routes />
        </BrowserRouter>
    </Provider>
);
export default App;
