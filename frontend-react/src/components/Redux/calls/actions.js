import calls from 'pages/Analytics/Calls/callsList';
import { UPDATE_CALLS } from './types';

export const update = () => (dispatch) => {
    setTimeout(() => {
        dispatch({
            type: UPDATE_CALLS,
            payload: calls,
        });
    }, 2000);
};
