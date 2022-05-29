import { INCREMENT_BALANCE, DECREMENT_BALANCE, UPDATE_BALANCE } from './types';

export const increment = (amount = 1) => ({
    type: INCREMENT_BALANCE,
    payload: amount,
});

export const decrement = (amount = 1) => ({
    type: DECREMENT_BALANCE,
    payload: amount,
});

export const update = () => (dispatch) => {
    setTimeout(() => {
        dispatch({
            type: UPDATE_BALANCE,
            payload: '∞ (минуты)',
        });
    }, 2000);
};
