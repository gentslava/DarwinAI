import managers from 'pages/Analytics/managers';
import { UPDATE_MANAGERS } from './types';

export const update = () => (dispatch) => {
    setTimeout(() => {
        dispatch({
            type: UPDATE_MANAGERS,
            payload: managers,
        });
    }, 2000);
};
