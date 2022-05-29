import { DECREMENT_BALANCE, INCREMENT_BALANCE, UPDATE_BALANCE } from './types';

const initialState = {
    value: undefined,
};

const balanceReducer = (state = initialState, action) => {
    switch (action.type) {
        case INCREMENT_BALANCE:
            return { ...state, value: state.value + action.payload };
        case DECREMENT_BALANCE:
            return { ...state, value: state.value - action.payload };
        case UPDATE_BALANCE:
            return { ...state, value: action.payload };
        default:
            return state;
    }
};
export default balanceReducer;
