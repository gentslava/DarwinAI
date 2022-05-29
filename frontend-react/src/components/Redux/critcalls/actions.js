import calls from 'pages/Dashboard/callsList';
import { UPDATE_CRITCALLS } from './types';

export const update = () => (dispatch) => {
    setTimeout(() => {
        dispatch({
            type: UPDATE_CRITCALLS,
            payload: calls,
        });
    }, 2000);
};
